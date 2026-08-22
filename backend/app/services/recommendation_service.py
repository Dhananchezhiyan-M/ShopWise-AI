import re
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import CanonicalProduct, ProductVariant, StoreListing
from app.schemas.recommendation import (
    ParsedRequirements,
    ScoredProductRecommendation,
    RecommendationResponse,
    RecommendationSearchRequest,
)
from app.services.matching_service import ProductMatchingService
from app.services.price_service import PriceAnalyticsService
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Master Recommendation Engine:
    1. Parses natural language buyer prompts using Gemini LLM (with heuristic fallback).
    2. Retrieves candidate products across stores from SQLite & Store Adapters (Step 4).
    3. Analyzes 90-day time-series price trends & Buy/Wait verdicts via Pandas (Step 5).
    4. Evaluates customer review aspect sentiment from ChromaDB Vector RAG (Step 6).
    5. Computes a multi-factor weighted score (0-100) and generates explainable badges.
    """

    @classmethod
    def parse_user_query(cls, query: str) -> ParsedRequirements:
        """
        Parses unstructured natural language query into structured shopping criteria.
        Uses Gemini LLM if API key is provided, otherwise uses intelligent regex heuristic parser.
        """
        if not query or not query.strip():
            return ParsedRequirements(category="all", confidence_score=1.0)

        # Attempt Gemini LLM Extraction
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() and not settings.GEMINI_API_KEY.startswith("your_"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)

                prompt = f"""
You are an expert e-commerce shopping assistant. Parse the following user query into structured JSON:
User Query: "{query}"

Return ONLY valid JSON matching this schema:
{{
  "category": "laptop" | "furniture" | "shoes" | "cycles" | "kitchen_appliances" | "hardware" | "audio" | "smartphone" | "all",
  "budget_max": float or null,
  "preferred_brand": string or null,
  "usage_intent": string or null,
  "key_priorities": ["durability", "battery", "accuracy", "performance", "thermals", "comfort", "value"],
  "required_specs": {{}}
}}
"""
                response = model.generate_content(prompt)
                raw_text = response.text.strip()
                clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()
                data = json.loads(clean_json)
                return ParsedRequirements(
                    category=data.get("category", "all"),
                    budget_max=data.get("budget_max"),
                    preferred_brand=data.get("preferred_brand"),
                    usage_intent=data.get("usage_intent"),
                    key_priorities=data.get("key_priorities", []),
                    required_specs=data.get("required_specs", {}),
                    confidence_score=0.95,
                )
            except Exception as e:
                logger.warning(f"[WARN] Gemini parse failed ({e}), falling back to Heuristic Rule Parser.")

        # Fallback: High-Precision Heuristic Rule Parser
        return cls._heuristic_parse(query)

    @classmethod
    def _heuristic_parse(cls, query: str) -> ParsedRequirements:
        """
        High-precision rule-based parser for multi-category shopping queries.
        Handles budgets, categories, brands, priorities, and dimension tokens.
        """
        q_lower = query.lower()
        category = "all"
        budget_max = None
        preferred_brand = None
        priorities = []
        specs = {}
        usage_intent = "general use"

        # 1. Category Detection
        if any(w in q_lower for w in ["shoe", "shoes", "sneaker", "sneakers", "footwear", "running", "running shoes", "nike", "puma", "adidas", "reebok"]):
            category = "shoes"
        elif any(w in q_lower for w in ["cycle", "bicycle", "bike", "mtb", "gear cycle", "firefox", "hero"]):
            category = "cycles"
        elif any(w in q_lower for w in ["scale", "weighing", "kitchen scale", "food scale", "baking", "healthsense", "prestige"]):
            category = "kitchen_appliances"
        elif any(w in q_lower for w in ["cpvc", "pvc pipe", "plumbing pipe", "water pipe", "geyser pipe", "fitting", "astral", "supreme"]):
            category = "hardware"
        elif any(w in q_lower for w in ["laptop", "notebook", "coding", "programming", "macbook", "ideapad", "vivobook", "thinkpad"]):
            category = "laptop"
        elif any(w in q_lower for w in ["headphone", "headphones", "earphones", "anc", "audio", "sound", "earbuds", "sony wh", "boat", "jbl", "sennheiser"]):
            category = "audio"
        elif any(w in q_lower for w in ["phone", "smartphone", "mobile", "5g", "oneplus", "galaxy", "iphone", "redmi", "poco", "itel", "realme"]):
            category = "smartphone"
        elif any(w in q_lower for w in ["chair", "furniture", "table", "desk", "sofa", "bed", "green soul", "godrej", "cellbell", "nilkamal"]):
            category = "furniture"
        else:
            category = "all"

        # 2. Budget Extraction (e.g. "under 15000", "under 15k", "below ₹60,000", "budget 1000", "under 1k")
        k_match = re.search(r"(?:under|below|budget|within|max|around)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*k\b", q_lower)
        if k_match:
            budget_max = float(k_match.group(1)) * 1000.0
        else:
            num_match = re.search(r"(?:under|below|budget|within|max|around)\s*(?:rs\.?|inr|₹)?\s*(\d{3,7})\b", q_lower)
            if num_match:
                budget_max = float(num_match.group(1))

        # 3. Brand Detection
        brands = [
            "nike", "puma", "adidas", "reebok", "redmi", "poco", "samsung", "oneplus", "apple",
            "asus", "hp", "lenovo", "acer", "dell", "green soul", "godrej", "cellbell", "nilkamal",
            "sony", "boat", "jbl", "sennheiser", "firefox", "hero", "healthsense", "prestige", "astral", "supreme", "itel"
        ]
        for b in brands:
            if b in q_lower:
                preferred_brand = b.title()
                break

        # 4. Priority Aspects
        if any(w in q_lower for w in ["battery", "backup", "charging", "long battery"]):
            priorities.append("battery")
        if any(w in q_lower for w in ["durable", "durability", "sturdy", "robust", "strong", "quality"]):
            priorities.append("durability")
        if any(w in q_lower for w in ["accurate", "accuracy", "precision", "1g", "tare"]):
            priorities.append("accuracy")
        if any(w in q_lower for w in ["heat", "heating", "cooling", "thermal", "overheat"]):
            priorities.append("thermals")
        if any(w in q_lower for w in ["comfort", "seat", "saddle", "ergonomic"]):
            priorities.append("comfort")
        if any(w in q_lower for w in ["cheap", "budget", "value", "deal", "affordable"]):
            priorities.append("value")
        if any(w in q_lower for w in ["fast", "performance", "speed", "coding", "gaming", "smooth"]):
            priorities.append("performance")

        # 5. Usage Intent
        if "coding" in q_lower or "programming" in q_lower or "developer" in q_lower:
            usage_intent = "software development & programming"
        elif "gaming" in q_lower:
            usage_intent = "gaming & graphic tasks"
        elif "baking" in q_lower or "cooking" in q_lower:
            usage_intent = "baking & kitchen ingredient measurement"
        elif "fitness" in q_lower or "trail" in q_lower or "mountain" in q_lower:
            usage_intent = "outdoor fitness & mountain cycling"
        elif "hot water" in q_lower or "geyser" in q_lower or "plumbing" in q_lower:
            usage_intent = "hot water potable plumbing"

        # 6. Dimensions & Hardware Specs
        dim_tokens = ProductMatchingService.extract_specs_from_title(query)
        if dim_tokens.get("ram_gb"):
            specs["ram_gb"] = dim_tokens["ram_gb"]
        if dim_tokens.get("dimensions_and_units"):
            specs["dimensions"] = dim_tokens["dimensions_and_units"]

        return ParsedRequirements(
            category=category,
            budget_max=budget_max,
            preferred_brand=preferred_brand,
            usage_intent=usage_intent,
            key_priorities=priorities,
            required_specs=specs,
            confidence_score=0.90,
        )

    @classmethod
    def get_recommendations(
        cls,
        db: Session,
        request: RecommendationSearchRequest,
    ) -> RecommendationResponse:
        """
        Executes the 4-Pillar Multi-Factor Recommendation Pipeline:
        1. Parses natural language requirements.
        2. Retrieves candidate products from SQLite catalog.
        3. Analyzes 90-day price trends and moving averages (Step 5).
        4. Queries review aspect satisfaction from ChromaDB (Step 6).
        5. Computes composite scores, generates explainable badges, and returns ranked results.
        """
        parsed = cls.parse_user_query(request.query)

        if request.category and request.category != "all":
            parsed.category = request.category
        if request.max_budget:
            parsed.budget_max = request.max_budget

        candidates = ProductMatchingService.get_canonical_catalog(
            db=db,
            category=parsed.category if parsed.category != "all" else None,
            search_query=request.query if parsed.category == "all" else None,
            max_budget=parsed.budget_max,
        )

        if not candidates and parsed.category != "all":
            candidates = ProductMatchingService.get_canonical_catalog(
                db=db,
                category=parsed.category,
            )

        if not candidates:
            candidates = ProductMatchingService.get_canonical_catalog(db=db)

        scored_list: List[ScoredProductRecommendation] = []

        for item in candidates:
            variant_id = item["variant_id"]
            canonical_id = item["canonical_id"]
            price_info = item.get("pricing", {})
            lowest_price = price_info.get("lowest_price", 0.0)
            highest_price = price_info.get("highest_price") or price_info.get("max_price") or lowest_price
            savings = max(0.0, highest_price - lowest_price)

            # 1. Price Analytics (Step 5 or Live Engine)
            if variant_id >= 9000:
                from app.services.live_product_service import DynamicLiveProductService
                price_history_res = DynamicLiveProductService.generate_dynamic_price_history(lowest_price, item["title"])
                verdict = price_history_res["verdict"]
                badge = price_history_res["verdict_badge"]
                drop_pct = price_history_res["price_drop_from_avg_pct"]
                review_aspects_dict = DynamicLiveProductService.generate_dynamic_reviews(item["title"])
                review_score_10 = review_aspects_dict["overall_sentiment_score"]
                sentiment_score_100 = review_score_10 * 10.0
                key_strengths = review_aspects_dict["key_strengths"]
                key_drawbacks = review_aspects_dict["key_drawbacks"]
            else:
                price_analytics = PriceAnalyticsService.analyze_variant_pricing(db, variant_id)
                if not price_analytics:
                    continue
                verdict = price_analytics.verdict
                badge = price_analytics.verdict_badge
                drop_pct = price_analytics.price_drop_from_avg_pct
                review_aspects = rag_service.get_aspect_breakdown(variant_id, item["title"])
                review_score_10 = review_aspects.overall_sentiment_score
                sentiment_score_100 = review_score_10 * 10.0
                key_strengths = review_aspects.key_strengths[:3]
                key_drawbacks = review_aspects.key_drawbacks[:2]

            # 3. Compute 4 Pillar Scores (0 to 100):
            specs_score = 70.0
            if parsed.preferred_brand and parsed.preferred_brand.lower() in item["brand"].lower():
                specs_score += 20.0
            if parsed.category != "all" and item["category"].lower() == parsed.category.lower():
                specs_score += 10.0
            if parsed.required_specs.get("ram_gb") and item["specs"].get("ram_gb"):
                if item["specs"]["ram_gb"] >= parsed.required_specs["ram_gb"]:
                    specs_score += 10.0
                else:
                    specs_score -= 20.0
            specs_score = max(10.0, min(100.0, specs_score))

            budget_fit_score = 80.0
            if parsed.budget_max:
                if lowest_price <= parsed.budget_max:
                    budget_fit_score = 90.0 + min(10.0, (parsed.budget_max - lowest_price) / parsed.budget_max * 10.0)
                else:
                    over_pct = (lowest_price - parsed.budget_max) / parsed.budget_max
                    budget_fit_score = max(10.0, 70.0 - (over_pct * 100.0))

            price_value_score = 70.0
            if verdict == "BUY_NOW":
                price_value_score = 95.0 + min(5.0, abs(drop_pct) / 2.0)
            elif verdict == "FAIR_PRICE":
                price_value_score = 75.0
            elif verdict == "WAIT":
                price_value_score = 40.0

            review_val_score = sentiment_score_100
            if parsed.key_priorities and variant_id < 9000:
                for priority in parsed.key_priorities:
                    for aspect in review_aspects.aspects:
                        if priority in aspect.aspect:
                            if aspect.positive_percentage >= 80.0:
                                review_val_score = min(100.0, review_val_score + 5.0)
                            elif aspect.negative_percentage >= 30.0:
                                review_val_score = max(30.0, review_val_score - 15.0)

            composite_score = (
                (specs_score * 0.35)
                + (budget_fit_score * 0.15)
                + (price_value_score * 0.25)
                + (review_val_score * 0.25)
            )
            composite_score = round(composite_score, 1)

            badges = []
            if verdict == "BUY_NOW":
                badges.append(f"🟢 Price Dropped {abs(drop_pct):.1f}% (Buy Now)")
            if savings >= 500:
                badges.append(f"💰 Save ₹{savings:,.0f} on {price_info['best_store_name']}")
            if review_score_10 >= 9.0:
                badges.append(f"⭐ Top Customer Satisfaction ({review_score_10}/10)")
            if lowest_price <= (parsed.budget_max or 9999999):
                badges.append("🏷️ Within Budget")

            verdict_exp = price_history_res["verdict_explanation"] if variant_id >= 9000 else price_analytics.verdict_explanation
            explanation = (
                f"Ranked #1 choice for {parsed.usage_intent or 'your requirements'}. "
                f"Priced at ₹{lowest_price:,.0f} on {price_info['best_store_name']} "
                f"({verdict_exp}). "
                f"Verified buyers gave {review_score_10}/10 customer satisfaction."
            )

            scored_rec = ScoredProductRecommendation(
                canonical_id=canonical_id,
                variant_id=variant_id,
                title=item["title"],
                brand=item["brand"],
                category=item["category"],
                image_url=item["image_url"],
                variant_name=item["variant_name"],
                current_lowest_price=lowest_price,
                best_store_name=price_info["best_store_name"],
                best_store_url=price_info["best_store_url"],
                savings_vs_highest_store=savings,
                verdict=verdict,
                verdict_badge=badge,
                price_drop_from_avg_pct=drop_pct,
                composite_ai_score=composite_score,
                specs_match_score=round(specs_score, 1),
                budget_fit_score=round(budget_fit_score, 1),
                price_value_score=round(price_value_score, 1),
                review_sentiment_score=round(review_val_score, 1),
                badges=badges,
                why_recommended=explanation,
                key_strengths=key_strengths,
                key_drawbacks=key_drawbacks,
                store_listings=item.get("store_listings", []),
                pricing=item.get("pricing"),
            )
            scored_list.append(scored_rec)

        scored_list.sort(key=lambda x: x.composite_ai_score, reverse=True)

        top_pick = scored_list[0] if scored_list else None
        alternatives = scored_list[1:request.limit] if len(scored_list) > 1 else []

        return RecommendationResponse(
            query=request.query,
            parsed_requirements=parsed,
            top_recommendation=top_pick,
            alternative_options=alternatives,
            total_candidates_analyzed=len(scored_list),
        )

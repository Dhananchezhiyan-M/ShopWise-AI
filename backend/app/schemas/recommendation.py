from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.product import ProductVariantResponse
from app.schemas.analytics import PriceAnalyticsSummary


class RecommendationSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    max_budget: Optional[float] = None
    limit: int = 5


class ParsedRequirements(BaseModel):
    category: str = "all"
    budget_max: Optional[float] = None
    preferred_brand: Optional[str] = None
    usage_intent: Optional[str] = None
    key_priorities: List[str] = []
    required_specs: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 1.0


class ScoredProductRecommendation(BaseModel):
    canonical_id: int
    variant_id: int
    title: str
    brand: str
    category: str
    image_url: Optional[str] = None
    variant_name: str
    current_lowest_price: float
    best_store_name: str
    best_store_url: str
    savings_vs_highest_store: float = 0.0
    
    # 90-Day Trend & Verdict
    verdict: str
    verdict_badge: str
    price_drop_from_avg_pct: float
    
    # Transparent score breakdown (0-100)
    composite_ai_score: float
    specs_match_score: float
    budget_fit_score: float
    price_value_score: float
    review_sentiment_score: float
    
    # Human-readable explainability badges & pros/cons
    badges: List[str] = []
    why_recommended: str
    key_strengths: List[str] = []
    key_drawbacks: List[str] = []
    store_listings: List[Dict[str, Any]] = []
    pricing: Optional[Dict[str, Any]] = None


class RecommendationResponse(BaseModel):
    query: str
    parsed_requirements: ParsedRequirements
    top_recommendation: Optional[ScoredProductRecommendation] = None
    alternative_options: List[ScoredProductRecommendation] = []
    total_candidates_analyzed: int


from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas.product import ProductVariantResponse
from app.schemas.analytics import PriceAnalyticsSummary


class ParsedRequirements(BaseModel):
    category: str = "all"
    budget_max: Optional[float] = None
    min_ram_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    preferred_brand: Optional[str] = None
    primary_use: Optional[str] = None  # 'programming', 'gaming', 'office', 'content_creation'
    key_features: List[str] = []
    confidence_score: float = 1.0


class ScoredProductRecommendation(BaseModel):
    variant: ProductVariantResponse
    price_analytics: PriceAnalyticsSummary
    
    # Transparent score breakdown (0-100)
    composite_ai_score: float
    specs_match_score: float
    budget_fit_score: float
    price_value_score: float
    review_sentiment_score: float
    
    # Human-readable explanation
    why_recommended: str
    pros: List[str] = []
    cons_and_tradeoffs: List[str] = []
    why_not_alternatives: Optional[str] = None


class RecommendationResponse(BaseModel):
    query: str
    parsed_requirements: ParsedRequirements
    top_recommendation: Optional[ScoredProductRecommendation] = None
    alternative_options: List[ScoredProductRecommendation] = []
    total_candidates_analyzed: int

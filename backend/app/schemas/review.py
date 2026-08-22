from typing import List, Optional
from pydantic import BaseModel, Field


class AspectScore(BaseModel):
    aspect: str = Field(..., description="Machine key: battery, thermals, display, performance, build_quality, sound, camera, value")
    label: str = Field(..., description="Human-readable title (e.g. 'Battery Life', 'Thermals & Cooling')")
    icon: str = Field(..., description="UI emoji icon (e.g. 🔋, ❄️, 🖥️, ⚡)")
    positive_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of positive review mentions")
    neutral_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    negative_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    total_mentions: int = Field(..., ge=0, description="Total review mentions analyzed for this aspect")
    summary: str = Field(..., description="One-line AI synthesis of user sentiment for this aspect")
    sample_positive_quote: Optional[str] = Field(None, description="Actual quote from a verified positive review")
    sample_critical_quote: Optional[str] = Field(None, description="Actual quote from a verified critical review")


class AspectSentimentResponse(BaseModel):
    variant_id: int
    product_title: str
    total_reviews_analyzed: int
    overall_sentiment_score: float = Field(..., ge=0.0, le=10.0, description="Overall sentiment out of 10")
    aspects: List[AspectScore]
    key_strengths: List[str] = Field(default_factory=list, description="Top positive consensus bullet points")
    key_drawbacks: List[str] = Field(default_factory=list, description="Top caveats or negative consensus bullet points")


class ReviewChunk(BaseModel):
    id: str
    text: str
    store: str = Field(..., description="amazon, flipkart, or croma")
    rating: float = Field(..., ge=1.0, le=5.0)
    aspect: str
    sentiment: str = Field(..., description="positive, negative, or neutral")
    verified_purchase: bool = True
    reviewer_name: str = "Verified Buyer"
    relevance_score: Optional[float] = Field(None, description="Cosine/Euclidean similarity relevance score from ChromaDB")


class ReviewQARequest(BaseModel):
    variant_id: int = Field(..., description="The Product Variant ID to query reviews for")
    question: str = Field(..., min_length=1, max_length=500, description="User's custom question (e.g. 'Does it heat up during heavy coding?')")
    top_k: Optional[int] = Field(default=4, ge=1, le=10, description="Number of review excerpts to retrieve as context")


class ReviewQAResponse(BaseModel):
    variant_id: int
    question: str
    answer: str = Field(..., description="Grounded AI answer synthesized from retrieved customer reviews")
    grounded: bool = Field(default=True, description="True if answer is directly derived from customer reviews")
    confidence: float = Field(default=0.92, ge=0.0, le=1.0)
    aspect_detected: Optional[str] = Field(None, description="Identified question aspect (thermals, battery, etc.)")
    retrieved_sources: List[ReviewChunk] = Field(default_factory=list, description="Top review chunks retrieved from ChromaDB")

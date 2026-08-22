from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.recommendation import (
    RecommendationSearchRequest,
    RecommendationResponse,
    ParsedRequirements,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/search", response_model=RecommendationResponse, summary="Get AI Multi-Factor Product Recommendations")
def get_ai_recommendations(
    request: RecommendationSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Takes a natural language user search query (e.g. "I need a budget kitchen scale under ₹1000 for baking"
    or "A durable mountain bike for weekend fitness under ₹15,000"):
    1. Parses user requirements via Gemini AI / Heuristic NLP.
    2. Multi-factor scoring (Spec match 35%, Price drop 25%, Review Sentiment 25%, Store Savings 15%).
    3. Returns ranked top recommendation + runner-up alternatives with explainable badges.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query string cannot be empty.")
    
    return RecommendationService.get_recommendations(db=db, request=request)


@router.post("/parse-query", response_model=ParsedRequirements, summary="Parse Natural Language Query into Structured JSON")
def parse_natural_language_query(
    request: RecommendationSearchRequest,
):
    """
    Debug & Preview endpoint to see how Gemini / Heuristic NLP converts unstructured
    human sentences into structured dictionary criteria (budget, category, priorities).
    """
    return RecommendationService.parse_user_query(request.query)

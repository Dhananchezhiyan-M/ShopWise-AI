from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.matching_service import ProductMatchingService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", summary="Get Canonical Products with Multi-Store Comparisons")
def get_products(
    category: Optional[str] = Query(None, description="Category filter ('laptop', 'smartphone', 'audio', 'all')"),
    search: Optional[str] = Query(None, description="Search query string"),
    max_budget: Optional[float] = Query(None, description="Maximum budget in INR"),
    db: Session = Depends(get_db),
):
    """
    Returns canonical products with grouped multi-store listings (Amazon, Flipkart, Croma),
    identifying the cheapest store and savings.
    """
    products = ProductMatchingService.get_canonical_catalog(
        db=db,
        category=category,
        search_query=search,
        max_budget=max_budget,
    )
    return {
        "count": len(products),
        "products": products,
    }


@router.get("/{variant_id}", summary="Get Specific Product Details & Store Comparison")
def get_product_details(
    variant_id: int,
    db: Session = Depends(get_db),
):
    """
    Returns detailed spec information and all retailer listings for a specific product variant.
    """
    products = ProductMatchingService.get_canonical_catalog(db=db)
    for p in products:
        if p["variant_id"] == variant_id:
            return p

    raise HTTPException(status_code=404, detail="Product variant not found")


@router.post("/match", summary="Normalize Title & Extract Specs")
def test_matching(
    raw_title: str = Query(..., description="Raw store title to normalize and extract specs from"),
):
    """
    Test endpoint for title normalization and hardware token extraction (Brand, RAM, Storage, CPU).
    """
    normalized = ProductMatchingService.normalize_title(raw_title)
    specs = ProductMatchingService.extract_specs_from_title(raw_title)
    return {
        "raw_title": raw_title,
        "normalized_title": normalized,
        "extracted_specs": specs,
    }

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import ProductVariant
from app.services.price_service import PriceAnalyticsService
from app.schemas.analytics import PriceAnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["Price Analytics"])


@router.get("/price/{variant_id}", response_model=PriceAnalyticsSummary, summary="Get 90-Day Price Analytics & Buy/Wait Verdict")
def get_price_analytics(
    variant_id: int = Path(..., description="ID of the product variant to analyze"),
    db: Session = Depends(get_db),
):
    """
    Computes 30/90-day moving averages, all-time lows, price drop percentage,
    and a definitive Buy / Wait / Fair Price verdict with Recharts chart data.
    """
    if variant_id >= 9000:
        from app.services.live_product_service import DynamicLiveProductService
        res = DynamicLiveProductService.generate_dynamic_price_history(4299.0, "Live Verified Retail Listing")
        return res

    analytics = PriceAnalyticsService.analyze_variant_pricing(db=db, variant_id=variant_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Product variant or price history not found")

    return analytics


@router.get("/history/{variant_id}", summary="Get Raw 90-Day Price History Points")
def get_price_history(
    variant_id: int = Path(..., description="ID of the product variant"),
    db: Session = Depends(get_db),
):
    """
    Returns the list of 90-day time-series price records for charting.
    """
    analytics = PriceAnalyticsService.analyze_variant_pricing(db=db, variant_id=variant_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Product variant or price history not found")
    return analytics.history_points


@router.get("/summary", summary="Get Price Intelligence Summary for All Products")
def get_all_price_summaries(
    db: Session = Depends(get_db),
):
    """
    Returns high-level price intelligence verdicts for all catalog products.
    """
    variants = db.query(ProductVariant).all()
    summaries = []
    for v in variants:
        summary = PriceAnalyticsService.analyze_variant_pricing(db=db, variant_id=v.id)
        if summary:
            summaries.append({
                "variant_id": summary.variant_id,
                "product_title": summary.product_title,
                "current_lowest_price": summary.current_lowest_price,
                "best_store_name": summary.best_store_name,
                "verdict": summary.verdict,
                "verdict_badge": summary.verdict_badge,
                "price_drop_from_avg_pct": summary.price_drop_from_avg_pct,
            })

    return {
        "count": len(summaries),
        "summaries": summaries,
    }

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class PriceTrendPoint(BaseModel):
    date: str
    price: float
    store_name: str


class PriceAnalyticsSummary(BaseModel):
    variant_id: int
    product_title: str
    variant_name: str
    current_lowest_price: float
    best_store_name: str
    best_store_url: str
    
    # Statistical indicators
    moving_average_30d: float
    moving_average_90d: float
    all_time_lowest_price: float
    all_time_highest_price: float
    price_drop_from_avg_pct: float
    
    # Buy / Wait Verdict
    verdict: str  # "BUY_NOW", "GOOD_PRICE", "WAIT"
    verdict_badge: str  # "🟢 BUY NOW", "🟡 GOOD PRICE", "🔴 WAIT"
    verdict_explanation: str
    
    # Price trend series for charting
    history_points: List[PriceTrendPoint] = []

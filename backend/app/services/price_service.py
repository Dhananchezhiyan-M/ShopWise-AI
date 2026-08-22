import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models import ProductVariant, StoreListing, PriceHistoryRecord
from app.schemas.analytics import PriceAnalyticsSummary, PriceTrendPoint


class PriceAnalyticsService:
    """
    Price Intelligence service leveraging Pandas and statistical analytics
    to calculate moving averages, historical lows, and Buy/Wait verdict scores.
    """

    @classmethod
    def analyze_variant_pricing(
        cls,
        db: Session,
        variant_id: int
    ) -> Optional[PriceAnalyticsSummary]:
        """
        Performs full 90-day statistical price analysis on a product variant
        across all its retailer listings.
        """
        variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        if not variant or not variant.store_listings:
            return None

        listings = variant.store_listings
        # Find current best (lowest) price listing
        best_listing = min(listings, key=lambda l: l.current_price)
        current_lowest = best_listing.current_price

        # Collect all historical price records across listings
        history_rows = []
        for listing in listings:
            store_name = listing.store.name if listing.store else "Store"
            for record in listing.price_history:
                history_rows.append({
                    "date": record.recorded_at,
                    "price": float(record.price),
                    "store_name": store_name,
                    "listing_id": listing.id,
                })

        if not history_rows:
            # Fallback if no history exists yet
            return PriceAnalyticsSummary(
                variant_id=variant.id,
                product_title=variant.canonical_product.title,
                variant_name=variant.variant_name,
                current_lowest_price=current_lowest,
                best_store_name=best_listing.store.name,
                best_store_url=best_listing.product_url,
                moving_average_30d=current_lowest,
                moving_average_90d=current_lowest,
                all_time_lowest_price=current_lowest,
                all_time_highest_price=current_lowest,
                price_drop_from_avg_pct=0.0,
                verdict="GOOD_PRICE",
                verdict_badge="🟡 FAIR PRICE",
                verdict_explanation="Price is currently at baseline.",
                history_points=[],
            )

        # Build Pandas DataFrame for statistical time-series calculations
        df = pd.DataFrame(history_rows)
        df["date"] = pd.to_datetime(df["date"], utc=True)
        df = df.sort_values(by="date")

        now = datetime.datetime.now(datetime.timezone.utc)
        thirty_days_ago = now - datetime.timedelta(days=30)

        # 1. Statistical Calculations
        all_time_low = float(df["price"].min())
        all_time_high = float(df["price"].max())
        avg_90d = float(df["price"].mean())

        # 30-day moving average
        recent_df = df[df["date"] >= pd.Timestamp(thirty_days_ago)]
        avg_30d = float(recent_df["price"].mean()) if not recent_df.empty else avg_90d

        # 2. Percentage Difference vs 90-day Average
        if avg_90d > 0:
            price_drop_pct = round(((current_lowest - avg_90d) / avg_90d) * 100, 2)
        else:
            price_drop_pct = 0.0

        # 3. Rule-based Buy/Wait Verdict Engine
        # Case 1: Near All-Time Low or >= 7% below 90-day average -> BUY NOW
        if current_lowest <= (all_time_low * 1.04) or price_drop_pct <= -7.0:
            verdict = "BUY_NOW"
            verdict_badge = "🟢 BUY NOW"
            if current_lowest <= (all_time_low * 1.02):
                verdict_explanation = f"Price is near the 90-day all-time low of ₹{all_time_low:,.0f} on {best_listing.store.name}! Excellent time to purchase."
            else:
                verdict_explanation = f"Current price is {abs(price_drop_pct):.1f}% below the 90-day average price (₹{avg_90d:,.0f}). Great savings."

        # Case 2: Above 90-day average by >= 5% or near all-time high -> WAIT
        elif price_drop_pct >= 5.0 or current_lowest >= (all_time_high * 0.96):
            verdict = "WAIT"
            verdict_badge = "🔴 WAIT FOR DROP"
            verdict_explanation = f"Price recently increased (+{price_drop_pct:.1f}% vs 90-day avg). Consider waiting for upcoming sales or price dips."

        # Case 3: Within normal ±5% range -> FAIR PRICE
        else:
            verdict = "GOOD_PRICE"
            verdict_badge = "🟡 FAIR PRICE"
            verdict_explanation = f"Price is stable and within normal 90-day ranges (Average: ₹{avg_90d:,.0f}). Reasonable buy if needed right away."

        # 4. Prepare daily trend points for Recharts visualization
        # Resample daily lowest price across all stores
        daily_df = df.groupby([df["date"].dt.strftime("%b %d"), "store_name"])["price"].min().reset_index()
        
        # Take latest 30-40 daily points for clean chart rendering
        history_points = []
        for _, row in df.tail(45).iterrows():
            history_points.append(
                PriceTrendPoint(
                    date=row["date"].strftime("%b %d"),
                    price=float(row["price"]),
                    store_name=str(row["store_name"]),
                )
            )

        return PriceAnalyticsSummary(
            variant_id=variant.id,
            product_title=variant.canonical_product.title,
            variant_name=variant.variant_name,
            current_lowest_price=round(current_lowest, 2),
            best_store_name=best_listing.store.name,
            best_store_url=best_listing.product_url,
            moving_average_30d=round(avg_30d, 2),
            moving_average_90d=round(avg_90d, 2),
            all_time_lowest_price=round(all_time_low, 2),
            all_time_highest_price=round(all_time_high, 2),
            price_drop_from_avg_pct=price_drop_pct,
            verdict=verdict,
            verdict_badge=verdict_badge,
            verdict_explanation=verdict_explanation,
            history_points=history_points,
        )

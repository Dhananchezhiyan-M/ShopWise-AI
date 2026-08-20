from typing import List, Optional
from app.services.adapters.base_adapter import BaseStoreAdapter, StandardProductItem, StandardPricePoint, StandardReview


class FlipkartAdapter(BaseStoreAdapter):
    """
    Flipkart Store Adapter.
    Translates Flipkart-specific formats (FSNs, flipkart.com links, ratings)
    into StandardProductItem format.
    """
    def __init__(self):
        super().__init__(
            store_name="Flipkart",
            store_slug="flipkart",
            base_url="https://www.flipkart.com"
        )
        self.logo_url = "https://upload.wikimedia.org/wikipedia/commons/7/7a/Flipkart_logo.svg"

    def search(self, query: str, limit: int = 10) -> List[StandardProductItem]:
        """
        Executes query search against Flipkart catalog.
        """
        return []

    def get_details(self, external_id: str) -> Optional[StandardProductItem]:
        """
        Fetch Flipkart FSN details.
        """
        return None

    def get_price_history(self, external_id: str, days: int = 90) -> List[StandardPricePoint]:
        """
        Returns 90-day price records for Flipkart FSN.
        """
        return []

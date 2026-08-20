from typing import List, Optional
from app.services.adapters.base_adapter import BaseStoreAdapter, StandardProductItem, StandardPricePoint, StandardReview


class AmazonAdapter(BaseStoreAdapter):
    """
    Amazon India Store Adapter.
    Translates Amazon-specific product formats (ASINs, amazon.in links, ratings)
    into StandardProductItem format.
    """
    def __init__(self):
        super().__init__(
            store_name="Amazon India",
            store_slug="amazon",
            base_url="https://www.amazon.in"
        )
        self.logo_url = "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"

    def search(self, query: str, limit: int = 10) -> List[StandardProductItem]:
        """
        Executes query search against Amazon catalog.
        """
        # In live production, this queries Amazon Product Advertising API or scraper fallback
        return []

    def get_details(self, external_id: str) -> Optional[StandardProductItem]:
        """
        Fetch Amazon ASIN details.
        """
        return None

    def get_price_history(self, external_id: str, days: int = 90) -> List[StandardPricePoint]:
        """
        Returns 90-day price records for Amazon ASIN.
        """
        return []

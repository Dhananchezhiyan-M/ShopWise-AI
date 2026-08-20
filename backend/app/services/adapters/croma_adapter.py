from typing import List, Optional
from app.services.adapters.base_adapter import BaseStoreAdapter, StandardProductItem, StandardPricePoint, StandardReview


class CromaAdapter(BaseStoreAdapter):
    """
    Croma Store Adapter.
    Translates Croma-specific formats (SKUs, croma.com links, ratings)
    into StandardProductItem format.
    """
    def __init__(self):
        super().__init__(
            store_name="Croma",
            store_slug="croma",
            base_url="https://www.croma.com"
        )
        self.logo_url = "https://upload.wikimedia.org/wikipedia/commons/e/e0/Croma_Logo.png"

    def search(self, query: str, limit: int = 10) -> List[StandardProductItem]:
        """
        Executes query search against Croma catalog.
        """
        return []

    def get_details(self, external_id: str) -> Optional[StandardProductItem]:
        """
        Fetch Croma SKU details.
        """
        return None

    def get_price_history(self, external_id: str, days: int = 90) -> List[StandardPricePoint]:
        """
        Returns 90-day price records for Croma SKU.
        """
        return []

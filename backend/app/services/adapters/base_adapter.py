from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StandardReview:
    """Standardized review item from any retailer."""
    author: str
    rating: float
    title: str
    comment: str
    date: str
    verified_purchase: bool = True
    aspect_sentiment: Dict[str, str] = field(default_factory=dict)  # e.g. {"battery": "positive", "heating": "negative"}


@dataclass
class StandardPricePoint:
    """Historical price snapshot point."""
    price: float
    date: str  # YYYY-MM-DD format
    event_label: Optional[str] = None  # e.g., "Prime Day Sale", "Regular Price"


@dataclass
class StandardProductItem:
    """
    Standardized product listing model returned by all store adapters.
    Normalizes differing field names across Amazon, Flipkart, Croma, etc.
    """
    store_name: str                         # "Amazon", "Flipkart", "Croma"
    store_slug: str                         # "amazon", "flipkart", "croma"
    external_id: str                        # ASIN / FSN / SKU
    title: str                              # Raw title on store
    product_url: str                        # Direct link to buy
    current_price: float                    # Price in INR
    original_mrp: Optional[float] = None    # MRP in INR
    discount_percent: Optional[float] = None
    in_stock: bool = True
    rating_star: Optional[float] = None     # Store star rating (e.g. 4.4)
    rating_count: Optional[int] = None      # Number of ratings (e.g. 8210)
    image_url: Optional[str] = None
    category: str = "general"               # "laptop", "smartphone", "audio", "smartwatch"
    
    # Specs dictionary extracted by the adapter
    specs: Dict[str, Any] = field(default_factory=dict)
    
    # Customer reviews for RAG vector ingestion
    reviews: List[StandardReview] = field(default_factory=list)
    
    # 90-day price history points
    price_history: List[StandardPricePoint] = field(default_factory=list)


class BaseStoreAdapter(ABC):
    """
    Abstract Base Class contract that every store adapter must implement.
    """
    def __init__(self, store_name: str, store_slug: str, base_url: str):
        self.store_name = store_name
        self.store_slug = store_slug
        self.base_url = base_url

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[StandardProductItem]:
        """
        Search for products matching the query on this store.
        Returns a list of standardized product listings.
        """
        pass

    @abstractmethod
    def get_details(self, external_id: str) -> Optional[StandardProductItem]:
        """
        Retrieve full product details, specs, and reviews for a given external product ID.
        """
        pass

    @abstractmethod
    def get_price_history(self, external_id: str, days: int = 90) -> List[StandardPricePoint]:
        """
        Retrieve historical price points for trend analysis.
        """
        pass

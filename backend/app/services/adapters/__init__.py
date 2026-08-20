from app.services.adapters.base_adapter import (
    BaseStoreAdapter,
    StandardProductItem,
    StandardPricePoint,
    StandardReview,
)
from app.services.adapters.amazon_adapter import AmazonAdapter
from app.services.adapters.flipkart_adapter import FlipkartAdapter
from app.services.adapters.croma_adapter import CromaAdapter

SUPPORTED_ADAPTERS = [
    AmazonAdapter(),
    FlipkartAdapter(),
    CromaAdapter(),
]

__all__ = [
    "BaseStoreAdapter",
    "StandardProductItem",
    "StandardPricePoint",
    "StandardReview",
    "AmazonAdapter",
    "FlipkartAdapter",
    "CromaAdapter",
    "SUPPORTED_ADAPTERS",
]

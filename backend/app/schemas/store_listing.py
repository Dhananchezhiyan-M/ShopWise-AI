from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.store import StoreResponse


class StoreListingBase(BaseModel):
    external_product_id: Optional[str] = None
    product_url: str
    title_in_store: str
    current_price: float
    original_mrp: Optional[float] = None
    discount_percent: Optional[float] = None
    in_stock: bool = True
    rating_star: Optional[float] = None
    rating_count: Optional[int] = None


class StoreListingCreate(StoreListingBase):
    variant_id: int
    store_id: int


class StoreListingResponse(StoreListingBase):
    id: int
    variant_id: int
    store_id: int
    store: Optional[StoreResponse] = None
    last_scraped_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

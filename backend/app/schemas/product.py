from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.store_listing import StoreListingResponse


class ProductVariantBase(BaseModel):
    variant_name: str
    sku: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    cpu_processor: Optional[str] = None
    gpu_graphics: Optional[str] = None
    screen_size_inch: Optional[float] = None
    battery_specs: Optional[str] = None
    color: Optional[str] = None
    specifications_json: Optional[str] = None


class ProductVariantCreate(ProductVariantBase):
    canonical_product_id: int


class ProductVariantResponse(ProductVariantBase):
    id: int
    canonical_product_id: int
    store_listings: List[StoreListingResponse] = []
    
    # Computed properties
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    best_store: Optional[str] = None
    best_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CanonicalProductBase(BaseModel):
    title: str
    brand: str
    category: str
    base_model: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


class CanonicalProductCreate(CanonicalProductBase):
    pass


class CanonicalProductResponse(CanonicalProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    variants: List[ProductVariantResponse] = []

    model_config = ConfigDict(from_attributes=True)

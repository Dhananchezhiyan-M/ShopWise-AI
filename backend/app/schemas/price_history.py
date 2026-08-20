from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PriceHistoryBase(BaseModel):
    price: float
    recorded_at: datetime


class PriceHistoryCreate(PriceHistoryBase):
    store_listing_id: int


class PriceHistoryResponse(PriceHistoryBase):
    id: int
    store_listing_id: int

    model_config = ConfigDict(from_attributes=True)

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StoreBase(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool = True


class StoreCreate(StoreBase):
    pass


class StoreResponse(StoreBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

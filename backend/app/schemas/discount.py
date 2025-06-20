from typing import Optional
from pydantic import BaseModel
from datetime import date


class DiscountBase(BaseModel):
    name: str
    description: Optional[str] = None
    discount_type: str  # "percentage" или "fixed"
    value: float
    is_active: bool = True
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    target_city: Optional[str] = None
    required_client_status: Optional[str] = None
    image_url: Optional[str] = None


class DiscountCreate(DiscountBase):
    tour_ids: Optional[list[int]] = None


class DiscountUpdate(DiscountBase):
    tour_ids: Optional[list[int]] = None


class Discount(DiscountBase):
    id: int

    class Config:
        from_attributes = True 
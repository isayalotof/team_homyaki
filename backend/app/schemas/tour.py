from pydantic import BaseModel, HttpUrl, validator
from datetime import date
from typing import List, Optional

from .booking import Booking
from .review import Review


# Base schema for tour properties
class TourBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_price: float
    duration_days: int
    start_date: date
    end_date: date
    max_tourists: int
    available_count: int
    country: str
    city: str
    image_url: Optional[str] = None
    meal_type: Optional[str] = None  # RO, BB, ...
    stars: Optional[int] = None  # 1-5

    # Ensure images always use relative path so they are served through the same origin behind Nginx
    @validator("image_url", pre=True, always=True)
    def _strip_hardcoded_host(cls, v):
        if isinstance(v, str) and v.startswith("http://localhost:8000"):
            return v.replace("http://localhost:8000", "")
        return v


# Schema for creating a tour
class TourCreate(TourBase):
    pass


# Schema for updating a tour
class TourUpdate(TourBase):
    pass


# Full tour schema, used for responses
class Tour(TourBase):
    id: int
    reviews: List[Review] = []
    discount_promo_name: Optional[str] = None
    discounted_price: Optional[float] = None
    discount_percent: Optional[float] = None
    rating: Optional[float] = None

    class Config:
        from_attributes = True


# Schema for a tour with its bookings
class TourWithBookings(Tour):
    bookings: List[Booking] = []


# Schema for a paginated list of tours
class TourPage(BaseModel):
    tours: List[Tour]
    pagination: dict 
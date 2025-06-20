from typing import Optional, List
from pydantic import BaseModel, validator, EmailStr
from datetime import datetime, date
from app.models.booking import BookingStatus


# New schemas for multi-step form
class TouristData(BaseModel):
    full_name: str
    birth_date: date
    passport_number: str

class BookerData(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    
class ExtraService(BaseModel):
    name: str
    price: float


# Base schema for booking, shared properties
class BookingBase(BaseModel):
    tour_id: int
    tourists_count: int
    total_price: float
    status: BookingStatus = BookingStatus.PENDING
    hotel_tier: Optional[str] = None
    
    class Config:
        from_attributes = True


# Schema for creating a new booking from the form
class BookingCreate(BaseModel):
    tour_id: int
    tourists_count: int
    hotel_tier: str
    tourists: List[TouristData]
    booker: BookerData
    extra_services: Optional[List[ExtraService]] = []


# Schema for updating a booking
class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None


# Schema for data stored in DB
class BookingInDBBase(BookingBase):
    id: int
    user_id: int
    booking_date: datetime
    discount_amount: Optional[float] = None
    applied_discount_id: Optional[int] = None

    class Config:
        from_attributes = True


# Schema for returning a booking to the client
class Booking(BookingInDBBase):
    pass 
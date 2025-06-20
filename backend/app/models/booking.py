from sqlalchemy import Column, Integer, ForeignKey, Numeric, Enum as PgEnum, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from .enums import BookingStatus


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    tourists_count = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(PgEnum(BookingStatus), default=BookingStatus.PENDING)
    booking_date = Column(DateTime, default=func.now(), nullable=False)

    # New fields for multi-step booking
    hotel_tier = Column(String)
    tourists_data = Column(JSONB) # List of tourist details
    booker_info = Column(JSONB) # Booker's contact info
    extra_services = Column(JSONB) # List of extra services

    # Applied discount info
    applied_discount_id = Column(Integer, ForeignKey("discounts.id"), nullable=True)
    discount_amount = Column(Numeric(10, 2), default=0.0)

    # Relationships
    user = relationship("User", back_populates="bookings")
    tour = relationship("Tour", back_populates="bookings")
    applied_discount = relationship("Discount") 
from sqlalchemy import Boolean, Column, Integer, String, Float, Text, Date, ForeignKey, Table, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


# Association table for many-to-many relationship between Tour and TourType
tour_tour_types = Table(
    'tour_tour_types',
    Base.metadata,
    Column('tour_id', Integer, ForeignKey('tours.id'), primary_key=True),
    Column('tour_type_id', Integer, ForeignKey('tour_types.id'), primary_key=True)
)

user_favorite_tours = Table(
    'user_favorite_tours', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('tour_id', Integer, ForeignKey('tours.id'), primary_key=True)
)


class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    country = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    max_tourists = Column(Integer, default=20)
    available_count = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Foreign keys
    hotel_id = Column(Integer, ForeignKey('hotels.id'), nullable=True)
    discount_id = Column(Integer, ForeignKey('discounts.id'), nullable=True)
    
    # New fields for meal type and hotel stars (denormalised for simpler filtering)
    meal_type = Column(String(3), nullable=True)  # RO, BB, HB, FB, AI, UAI
    stars = Column(Integer, nullable=True)  # 1-5
    
    # Relationships
    bookings = relationship("Booking", back_populates="tour", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="tour", cascade="all, delete-orphan")
    hotel = relationship("Hotel", back_populates="tours")
    tour_types = relationship("TourType", secondary=tour_tour_types, back_populates="tours")
    favorited_by_users = relationship("User", secondary="user_favorite_tours", back_populates="favorite_tours")
    discount = relationship("Discount", back_populates="tours") 
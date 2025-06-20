from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author_name = Column(String(100), nullable=True)
    author_email = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    tour = relationship("Tour", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    hotel = relationship("Hotel", back_populates="reviews") 
from sqlalchemy import Column, Integer, String, Text, Enum as PgEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .enums import MealType


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    stars = Column(Integer, nullable=False)
    meal_type = Column(PgEnum(MealType), nullable=False)
    description = Column(Text)
    image_url = Column(String(255))

    # Relationships
    tours = relationship("Tour", back_populates="hotel")
    reviews = relationship("Review", back_populates="hotel") 
from sqlalchemy import Column, Integer, String, Numeric, Enum as PgEnum, DateTime, Boolean, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .enums import DiscountType, ClientStatus


class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    discount_type = Column(PgEnum(DiscountType), nullable=False)
    value = Column(Numeric(10, 2), nullable=False)
    
    is_active = Column(Boolean, default=True)
    valid_from = Column(Date)
    valid_to = Column(Date)
    
    # Conditions
    target_city = Column(String, index=True) # e.g., "Москва"
    image_url = Column(String(255))
    required_client_status = Column(PgEnum(ClientStatus))

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # relationships
    tours = relationship("Tour", back_populates="discount") 
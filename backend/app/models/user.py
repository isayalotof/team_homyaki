from sqlalchemy import Column, Integer, String, Boolean, Enum as PgEnum, Date, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .enums import UserRole, ClientStatus


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    
    date_of_birth = Column(Date, nullable=True)
    client_status = Column(PgEnum(ClientStatus), default=ClientStatus.REGULAR, nullable=False)

    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    role = Column(PgEnum(UserRole), default=UserRole.client, nullable=False)
    
    # Поля для восстановления пароля
    # reset_token = Column(String, nullable=True)
    # reset_token_expires = Column(DateTime, nullable=True)

    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    favorite_tours = relationship("Tour", secondary="user_favorite_tours", back_populates="favorited_by_users") 
from .user import User
from .tour import Tour
from .hotel import Hotel
from .booking import Booking
from .review import Review
from .discount import Discount
from .tour_type import TourType
from .enums import UserRole, BookingStatus, ClientStatus, DiscountType, TourType as EnumTourType

# Association table for favorites
from .tour import user_favorite_tours

__all__ = [
    "User",
    "Tour",
    "Hotel",
    "Booking",
    "Review",
    "Discount",
    "TourType",
    "user_favorite_tours",
    # Enums
    "UserRole",
    "BookingStatus",
    "ClientStatus",
    "DiscountType",
    "EnumTourType"
] 
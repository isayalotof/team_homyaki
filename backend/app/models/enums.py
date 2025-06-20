import enum


class UserRole(str, enum.Enum):
    client = "client"
    agency_manager = "agency_manager"
    operator_manager = "operator_manager"
    admin = "admin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class ClientStatus(str, enum.Enum):
    REGULAR = "Обычный"
    SILVER = "Серебряный"
    GOLD = "Золотой"
    PLATINUM = "Платиновый"


class MealType(str, enum.Enum):
    RO = "Без питания"
    BB = "Завтрак"
    HB = "Полупансион"
    FB = "Полный пансион"
    AI = "Все включено"
    UAI = "Ультра все включено"


class TourType(str, enum.Enum):
    excursion = "Экскурсионный"
    beach = "Пляжный"
    ski = "Горнолыжный"
    gastronomic = "Гастрономический"
    eco = "Эко-туризм"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class DiscountType(str, enum.Enum):
    FIXED = "fixed"  # в рублях
    PERCENTAGE = "percentage"  # в процентах 
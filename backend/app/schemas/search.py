from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
from datetime import date

from .tour import Tour


class TourSearchParams(BaseModel):
    """
    Параметры поиска туров
    """
    query: Optional[str] = None
    price_min: Optional[float] = 0
    price_max: Optional[float] = 1000000
    duration: Optional[int] = None
    tourists: Optional[int] = 1
    hotel_stars: Optional[int] = 0
    meal_type: Optional[str] = "any"
    date_range: Optional[str] = None
    region: Optional[str] = None
    page: Optional[int] = 1
    sort_by: Optional[str] = "priority"  # priority, price_asc, price_desc, rating
    tour_types_order: Optional[List[int]] = None


class PaginationData(BaseModel):
    page: int
    per_page: int
    total_items: int
    total_pages: int


class TourSearchResponse(BaseModel):
    """
    Результаты поиска туров
    """
    tours: List[Tour]
    pagination: PaginationData
    
    class Config:
        from_attributes = True


class Destination(BaseModel):
    """
    Направление (город или достопримечательность)
    """
    id: int
    name: str
    type: str  # city или attraction
    popularity: Optional[int] = 0
    
    class Config:
        from_attributes = True


class WizardDateRange(BaseModel):
    """
    Диапазон дат для конструктора тура
    """
    start: Optional[date] = None
    end: Optional[date] = None


class WizardTourists(BaseModel):
    """
    Информация о туристах для конструктора тура
    """
    adults: int = 2
    children: Optional[int] = 0


class WizardAccommodation(BaseModel):
    """
    Параметры проживания для конструктора тура
    """
    type: Optional[str] = "hotel"  # hotel, hostel, apartment
    stars: Optional[int] = 3


class WizardPreferences(BaseModel):
    """
    Предпочтения для конструктора тура
    """
    transport: Optional[str] = "any"  # train, plane, bus, any
    accommodation: Optional[WizardAccommodation] = None
    includeMeals: Optional[bool] = True
    includeExcursions: Optional[bool] = True


class WizardSearchParams(BaseModel):
    """
    Параметры поиска из конструктора тура
    """
    destinations: Optional[List[Dict[str, Any]]] = None
    dates: Optional[WizardDateRange] = None
    tourists: Optional[WizardTourists] = None
    budget: Optional[float] = 50000
    preferences: Optional[WizardPreferences] = None 
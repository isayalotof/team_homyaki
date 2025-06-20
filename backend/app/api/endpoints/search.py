from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.TourSearchResponse)
async def search_tours(
    *,
    db: Session = Depends(deps.get_db),
    search_params: schemas.TourSearchParams = Body(...),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Advanced tour search with priority sorting based on tour types.
    """
    # Extract filters from search params
    filters = {
        "price_min": search_params.price_min,
        "price_max": search_params.price_max,
        "duration": search_params.duration,
        "hotel_stars": search_params.hotel_stars if search_params.hotel_stars > 0 else None,
        "meal_type": search_params.meal_type if search_params.meal_type != "any" else None,
        "min_available": search_params.tourists,
    }
    
    # Get date range
    if search_params.date_range:
        date_parts = search_params.date_range.split(" - ")
        if len(date_parts) == 2:
            from datetime import datetime
            try:
                start_date = datetime.strptime(date_parts[0], "%d.%m.%Y").date()
                end_date = datetime.strptime(date_parts[1], "%d.%m.%Y").date()
                filters["start_date_from"] = start_date
                filters["start_date_to"] = end_date
            except ValueError:
                pass
    
    # Get tours with filters
    page = search_params.page or 1
    sort_by = search_params.sort_by or "priority"
    
    tours_data = crud.crud_tour.get_filtered_tours(
        db, 
        filters=filters, 
        sort_by=sort_by, 
        page=page, 
        page_size=9,
        tour_types_order=search_params.tour_types_order
    )
    
    return tours_data


@router.get("/destinations", response_model=List[schemas.Destination])
async def get_destinations(
    *,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Get available destinations (cities and attractions) for the tour constructor.
    """
    # Получаем уникальные города из туров
    cities = db.query(
        models.Tour.destination.label("name"),
        func.count(models.Tour.id).label("tour_count")
    ).group_by(models.Tour.destination).order_by(func.count(models.Tour.id).desc()).limit(10).all()
    
    # Получаем популярные достопримечательности из описаний туров
    attractions = db.query(
        models.Tour.name.label("name"),
        func.count(models.Booking.id).label("booking_count")
    ).outerjoin(models.Booking).group_by(models.Tour.name).order_by(
        func.count(models.Booking.id).desc()
    ).limit(5).all()
    
    # Формируем список направлений
    destinations = []
    
    # Добавляем города
    for i, city in enumerate(cities):
        if city.name:  # Проверяем, что название города не пустое
            destinations.append({
                "id": i + 1,
                "name": city.name,
                "type": "city",
                "popularity": city.tour_count
            })
    
    # Добавляем достопримечательности
    for i, attraction in enumerate(attractions):
        if attraction.name:  # Проверяем, что название достопримечательности не пустое
            destinations.append({
                "id": len(cities) + i + 1,
                "name": attraction.name,
                "type": "attraction",
                "popularity": attraction.booking_count or 0
            })
    
    return destinations


@router.post("/wizard", response_model=schemas.TourSearchResponse)
async def search_tours_from_wizard(
    *,
    db: Session = Depends(deps.get_db),
    wizard_data: schemas.WizardSearchParams = Body(...),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Search tours based on the wizard data.
    """
    # Преобразуем данные из конструктора в параметры поиска
    filters = {}
    
    # Добавляем фильтр по городам
    if wizard_data.destinations:
        city_names = [dest["name"] for dest in wizard_data.destinations if dest["type"] == "city"]
        if city_names:
            filters["destinations"] = city_names
    
    # Добавляем фильтр по датам
    if wizard_data.dates and wizard_data.dates.start and wizard_data.dates.end:
        from datetime import datetime
        filters["start_date_from"] = wizard_data.dates.start
        filters["start_date_to"] = wizard_data.dates.end
    
    # Добавляем фильтр по количеству туристов
    if wizard_data.tourists:
        filters["min_available"] = wizard_data.tourists.adults + (wizard_data.tourists.children or 0)
    
    # Добавляем фильтр по бюджету
    if wizard_data.budget:
        filters["price_max"] = wizard_data.budget
    
    # Добавляем фильтры по предпочтениям
    if wizard_data.preferences:
        if wizard_data.preferences.accommodation and wizard_data.preferences.accommodation.stars:
            filters["hotel_stars"] = wizard_data.preferences.accommodation.stars
    
    # Получаем туры с фильтрами
    tours_data = crud.crud_tour.get_filtered_tours(
        db, 
        filters=filters, 
        page=1, 
        page_size=12
    )
    
    return tours_data

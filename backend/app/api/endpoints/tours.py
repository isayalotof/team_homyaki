from typing import Any, List, Optional
from datetime import date
import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.api import deps
from app.crud import crud_tour
from app.services.discount_service import get_best_discount_for_tour
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=schemas.TourPage)
def read_tours(
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
    # Pagination
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    # Sorting
    sort_by: str = Query('popularity', enum=['popularity', 'price_asc', 'price_desc', 'rating', 'date']),
    # Filters
    query: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    tourists: Optional[int] = Query(None, ge=1),
    duration_min: Optional[int] = Query(None, ge=1),
    duration_max: Optional[int] = Query(None, ge=1),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    stars: Optional[List[int]] = Query(None),
    meal_type: Optional[str] = Query(None),
    tour_type: Optional[List[int]] = Query(None),
    promotion: Optional[int] = Query(None),
) -> Any:
    """
    Retrieve tours with discount information.
    """
    filters = {
        'query': query,
        'country': country,
        'city': city,
        'start_date': start_date,
        'tourists': tourists,
        'duration_min': duration_min,
        'duration_max': duration_max,
        'price_min': price_min,
        'price_max': price_max,
        'stars': stars,
        'meal_type': meal_type,
        'tour_type': tour_type,
        'promotion': promotion,
    }
    # Remove None values so we don't pass them to the CRUD function
    active_filters = {k: v for k, v in filters.items() if v is not None and v != '' and v != []}

    result = crud_tour.get_filtered_tours(
        db, page=page, page_size=limit, sort_by=sort_by, filters=active_filters
    )
    tours = result['tours']
    pagination_data = result['pagination']
    
    tours_with_discounts = []
    for tour in tours:
        tour_schema = schemas.Tour.from_orm(tour)
        discounted_price, promo_name = get_best_discount_for_tour(db, tour=tour, user=current_user)
        tour_schema.discounted_price = discounted_price
        tour_schema.discount_promo_name = promo_name
        if tour.discount and tour.discount.discount_type.value == 'percentage':
            tour_schema.discount_percent = float(tour.discount.value)
        elif tour.discount and tour.discount.discount_type.value == 'fixed':
            try:
                tour_schema.discount_percent = round(float(tour.discount.value) / float(tour.base_price) * 100, 1)
            except ZeroDivisionError:
                tour_schema.discount_percent = None
        tours_with_discounts.append(tour_schema)
        
    return {
        "tours": tours_with_discounts,
        "pagination": pagination_data
    }


@router.get("/{tour_id}", response_model=schemas.Tour)
def read_tour(
    *,
    db: Session = Depends(deps.get_db),
    tour_id: int,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Get tour by ID with discount information.
    """
    tour = crud_tour.get(db, id=tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
        
    tour_schema = schemas.Tour.from_orm(tour)
    discounted_price, promo_name = get_best_discount_for_tour(db, tour=tour, user=current_user)
    tour_schema.discounted_price = discounted_price
    tour_schema.discount_promo_name = promo_name
    
    return tour_schema


@router.get("/with-bookings", response_model=List[schemas.TourWithBookings])
def read_tours_with_bookings(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve tours with booking counts.
    Admin only.
    """
    tours = crud_tour.get_tours_with_booking_count(db, skip=skip, limit=limit)
    return tours


@router.get("/search", response_model=List[schemas.Tour])
def search_tours(
    db: Session = Depends(deps.get_db),
    destination: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    start_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Search tours by criteria.
    """
    tours = crud_tour.search_tours(
        db, 
        destination=destination,
        min_price=min_price,
        max_price=max_price,
        start_date=start_date,
        skip=skip, 
        limit=limit
    )
    return tours


@router.post("/", response_model=schemas.Tour)
def create_tour(
    *,
    db: Session = Depends(deps.get_db),
    tour_in: schemas.TourCreate,
    current_user: models.User = Depends(deps.get_current_active_manager),
) -> Any:
    """
    Create new tour.
    Admin only.
    """
    tour = crud_tour.create(db, obj_in=tour_in)
    return tour


@router.post("", response_model=schemas.Tour)
def create_tour_no_slash(
    *,
    db: Session = Depends(deps.get_db),
    tour_in: schemas.TourCreate,
    current_user: models.User = Depends(deps.get_current_active_manager),
):
    return create_tour(db=db, tour_in=tour_in, current_user=current_user)


@router.put("/{tour_id}", response_model=schemas.Tour)
def update_tour(
    *,
    db: Session = Depends(deps.get_db),
    tour_id: int,
    tour_in: schemas.TourUpdate,
    current_user: models.User = Depends(deps.get_current_active_manager),
) -> Any:
    """
    Update a tour.
    Admin only.
    """
    tour = crud_tour.get(db, id=tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    tour = crud_tour.update(db, db_obj=tour, obj_in=tour_in)
    return tour


@router.delete("/{tour_id}", response_model=schemas.Tour)
def delete_tour(
    *,
    db: Session = Depends(deps.get_db),
    tour_id: int,
    current_user: models.User = Depends(deps.get_current_active_manager),
) -> Any:
    """
    Delete a tour.
    Admin only.
    """
    tour = crud_tour.get(db, id=tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    tour = crud_tour.remove(db, id=tour_id)
    return tour


@router.post("/upload-image")
async def upload_tour_image(
    image: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_manager)
):
    """Upload image for a tour and return absolute URL."""
    # Validate content type
    if image.content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    static_dir = Path("app/static/images/tours")
    static_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    ext = Path(image.filename).suffix
    filename = f"tour_{uuid.uuid4().hex}{ext}"
    file_path = static_dir / filename

    # Save file
    with file_path.open("wb") as f:
        shutil.copyfileobj(image.file, f)

    url = f"/static/images/tours/{filename}"
    return {"url": url}


# Alternative route without trailing slash (same params) so /api/tours and /api/tours/ both work
# Not added to OpenAPI schema to avoid duplicates
@router.get("", response_model=schemas.TourPage, include_in_schema=False)
def read_tours_no_slash(
    # Pagination
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    # Sorting
    sort_by: str = Query('popularity', enum=['popularity', 'price_asc', 'price_desc', 'rating', 'date']),
    # Filters (same list as main route)
    query: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    tourists: Optional[int] = Query(None, ge=1),
    duration_min: Optional[int] = Query(None, ge=1),
    duration_max: Optional[int] = Query(None, ge=1),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    stars: Optional[List[int]] = Query(None),
    meal_type: Optional[str] = Query(None),
    tour_type: Optional[List[int]] = Query(None),
    promotion: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    return read_tours(
        db=db, current_user=current_user,
        page=page, limit=limit, sort_by=sort_by,
        query=query, country=country, city=city, start_date=start_date,
        tourists=tourists, duration_min=duration_min, duration_max=duration_max,
        price_min=price_min, price_max=price_max, stars=stars, meal_type=meal_type,
        tour_type=tour_type, promotion=promotion
    ) 
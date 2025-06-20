from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud import crud_booking, crud_tour
from app.models.booking import BookingStatus

router = APIRouter()


@router.get("/", response_model=List[schemas.Booking])
def read_bookings(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all bookings.
    Admin only.
    """
    bookings = crud_booking.get_multi(db, skip=skip, limit=limit)
    return bookings


@router.get("/my-bookings", response_model=List[schemas.Booking])
def read_user_bookings(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve current user's bookings.
    """
    bookings = crud_booking.get_multi_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return bookings


@router.get("/tour/{tour_id}", response_model=List[schemas.Booking])
def read_tour_bookings(
    tour_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve bookings for a specific tour.
    Admin only.
    """
    bookings = crud_booking.get_multi_by_tour(db, tour_id=tour_id, skip=skip, limit=limit)
    return bookings


@router.post("/", response_model=schemas.Booking)
def create_booking(
    *,
    db: Session = Depends(deps.get_db),
    booking_in: schemas.BookingCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new booking.
    """
    booking = crud_booking.create_with_owner(db=db, obj_in=booking_in, user=current_user)
    # Here you could trigger email sending, etc.
    return booking


@router.get("/{booking_id}", response_model=schemas.Booking)
def read_booking(
    booking_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get booking by ID.
    """
    booking = crud_booking.get(db, id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user is admin or booking owner
    if booking.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return booking


@router.put("/{booking_id}", response_model=schemas.Booking)
def update_booking(
    *,
    db: Session = Depends(deps.get_db),
    booking_id: int,
    booking_in: schemas.BookingUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a booking.
    """
    booking = crud_booking.get(db, id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # Check if user is admin or booking owner
    if booking.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # If user is not admin, they can only update participants count
    if not current_user.is_superuser:
        booking_in_dict = booking_in.dict(exclude_unset=True)
        if "status" in booking_in_dict:
            del booking_in_dict["status"]
        booking = crud_booking.update(db, db_obj=booking, obj_in=booking_in_dict)
    else:
        booking = crud_booking.update(db, db_obj=booking, obj_in=booking_in)
    
    return booking


@router.post("/{booking_id}/cancel", response_model=schemas.Booking)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancel a booking.
    """
    booking = crud_booking.get(db, id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # Check if user is admin or booking owner
    if booking.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if booking is already cancelled
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    
    booking = crud_booking.cancel_booking(db, booking_id=booking_id)
    return booking 
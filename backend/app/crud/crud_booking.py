from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, or_
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from datetime import date, timedelta

from app.crud.base import CRUDBase
from app.models.booking import Booking, BookingStatus
from app.models.tour import Tour
from app.models.user import User
from app.models.discount import Discount, DiscountType
from app.schemas.booking import BookingCreate, BookingUpdate


class CRUDBooking(CRUDBase[Booking, BookingCreate, BookingUpdate]):
    def _calculate_and_apply_discount(self, db: Session, *, tour: Tour, user: User, initial_price: float) -> (float, Optional[int]):
        """Calculates and returns the discount amount and the ID of the applied discount."""
        
        # 1. Birthday discount
        birthday_discount_amount = 0
        if user.date_of_birth:
            today = date.today()
            user_birthday_this_year = user.date_of_birth.replace(year=today.year)
            if abs((user_birthday_this_year - today).days) <= 5:
                birthday_discount_amount = initial_price * 0.05

        # 2. Find all applicable promotions
        today = date.today()
        applicable_discounts = db.query(Discount).filter(
            Discount.is_active == True,
            Discount.valid_from <= today,
            Discount.valid_to >= today,
            or_(
                Discount.target_city == None,
                Discount.target_city == tour.city
            ),
             or_(
                Discount.required_client_status == None,
                Discount.required_client_status == user.client_status
            )
        ).all()
        
        best_promo_discount = 0
        best_promo_id = None

        for discount in applicable_discounts:
            current_discount = 0
            if discount.discount_type == DiscountType.PERCENTAGE:
                current_discount = initial_price * (discount.value / 100)
            else: # Fixed
                current_discount = discount.value
            
            if current_discount > best_promo_discount:
                best_promo_discount = current_discount
                best_promo_id = discount.id
        
        # 3. Choose the best discount (birthday vs promotion)
        final_discount_amount = max(birthday_discount_amount, best_promo_discount)
        applied_discount_id = best_promo_id if best_promo_discount > birthday_discount_amount else None

        # 4. Cap discount at 40%
        max_discount = initial_price * 0.4
        final_discount_amount = min(final_discount_amount, max_discount)
        
        return round(final_discount_amount, 2), applied_discount_id

    def create_with_owner(
        self, db: Session, *, obj_in: BookingCreate, user: User
    ) -> Booking:
        # 1. Get tour details
        tour = db.query(Tour).filter(Tour.id == obj_in.tour_id).first()
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")
        if not tour.is_active:
            raise HTTPException(status_code=400, detail="Tour is not active")
        if tour.available_count < obj_in.tourists_count:
            raise HTTPException(status_code=400, detail="Not enough available places")

        # 2. Calculate total price on the server
        total_price = tour.base_price * obj_in.tourists_count

        # Add accommodation cost
        hotel_multipliers = {"standard": 1.0, "comfort": 1.2, "premium": 1.5}
        multiplier = hotel_multipliers.get(obj_in.hotel_tier, 1.0)
        total_price *= multiplier
        
        # Add extras cost
        for service in obj_in.extra_services:
            # In the frontend, the price for per-person services was already multiplied.
            # Here, we just sum them up.
            total_price += service.price

        # 3. Apply discount
        discount_amount, applied_discount_id = self._calculate_and_apply_discount(
            db, tour=tour, user=user, initial_price=total_price
        )
        final_price = total_price - discount_amount

        # 4. Create booking object
        db_obj = Booking(
            user_id=user.id,
            tour_id=obj_in.tour_id,
            tourists_count=obj_in.tourists_count,
            total_price=final_price,
            hotel_tier=obj_in.hotel_tier,
            tourists_data=jsonable_encoder(obj_in.tourists),
            booker_info=jsonable_encoder(obj_in.booker),
            extra_services=jsonable_encoder(obj_in.extra_services),
            discount_amount=discount_amount,
            applied_discount_id=applied_discount_id
        )
        
        # 5. Decrease available tour count
        tour.available_count -= obj_in.tourists_count

        db.add(db_obj)
        db.add(tour)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Booking]:
        return (
            db.query(Booking)
            .filter(Booking.user_id == user_id)
            .order_by(desc(Booking.booking_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_tour(
        self, db: Session, *, tour_id: int, skip: int = 0, limit: int = 100
    ) -> List[Booking]:
        return (
            db.query(Booking)
            .filter(Booking.tour_id == tour_id)
            .order_by(desc(Booking.booking_date))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_status(
        self, db: Session, *, booking_id: int, status: BookingStatus
    ) -> Optional[Booking]:
        booking = self.get(db, id=booking_id)
        if not booking:
            return None
        
        booking.status = status
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
    
    def cancel_booking(self, db: Session, *, booking_id: int) -> Optional[Booking]:
        return self.update_status(db, booking_id=booking_id, status=BookingStatus.CANCELLED)
    
    def confirm_booking(self, db: Session, *, booking_id: int) -> Optional[Booking]:
        return self.update_status(db, booking_id=booking_id, status=BookingStatus.CONFIRMED)
    
    def complete_booking(self, db: Session, *, booking_id: int) -> Optional[Booking]:
        return self.update_status(db, booking_id=booking_id, status=BookingStatus.COMPLETED)


crud_booking = CRUDBooking(Booking) 
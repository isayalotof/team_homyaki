from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from decimal import Decimal

from app.models import Tour, User, Discount, DiscountType

def get_best_discount_for_tour(db: Session, tour: Tour, user: Optional[User]) -> Optional[Tuple[float, str]]:
    """
    Finds the best applicable discount for a given tour and user.
    Returns a tuple of (discounted_price, promotion_name) or None.
    """
    today = date.today()
    applicable_discounts = db.query(Discount).filter(
        Discount.is_active == True,
        Discount.valid_from <= today,
        Discount.valid_to >= today,
        (Discount.target_city == None) | (Discount.target_city == tour.city)
    ).all()

    best_discount_value = Decimal('0')
    best_discount_name = None

    # Check promotions
    for discount in applicable_discounts:
        # Check client status if required
        if discount.required_client_status and (not user or user.client_status != discount.required_client_status):
            continue

        current_discount_value = Decimal('0')
        if discount.discount_type == DiscountType.PERCENTAGE:
            current_discount_value = tour.base_price * (discount.value / Decimal('100'))
        else:  # Fixed amount
            current_discount_value = discount.value
        
        if current_discount_value > best_discount_value:
            best_discount_value = current_discount_value
            best_discount_name = discount.name

    # Check birthday discount
    if user and user.date_of_birth:
        user_birthday_this_year = user.date_of_birth.replace(year=today.year)
        if abs((user_birthday_this_year - today).days) <= 5:
            birthday_discount_value = tour.base_price * Decimal('0.05')
            if birthday_discount_value > best_discount_value:
                best_discount_value = birthday_discount_value
                best_discount_name = "Скидка на День Рождения"

    if best_discount_value > 0:
        # Cap discount at 40%
        max_discount = tour.base_price * Decimal('0.4')
        final_discount_value = min(best_discount_value, max_discount)
        
        final_price = tour.base_price - final_discount_value
        # Convert Decimal to float for JSON serialization
        return round(float(final_price), 2), best_discount_name

    return None, None 
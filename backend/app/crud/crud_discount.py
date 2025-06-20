from app.crud.base import CRUDBase
from app.models.discount import Discount
from app.schemas.discount import DiscountCreate, DiscountUpdate

class CRUDDiscount(CRUDBase[Discount, DiscountCreate, DiscountUpdate]):
    # You can add custom CRUD methods here later if needed
    # For example, a method to find all active discounts
    pass

crud_discount = CRUDDiscount(Discount) 
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import uuid, os
from fastapi.responses import JSONResponse

from app import models, schemas, crud
from app.api import deps
from app.models.enums import DiscountType

router = APIRouter()

# ---------- Image Upload ----------
UPLOAD_DIR = os.path.join(os.getcwd(), "app", "static", "images", "promotions")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-image")
async def upload_promo_image(image: UploadFile = File(...), current_user: models.User = Depends(deps.get_current_active_manager)):
    ext = os.path.splitext(image.filename)[1]
    filename = f"promo_{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        f.write(await image.read())
    url = f"/static/images/promotions/{filename}"
    return JSONResponse({"url": url})

@router.post("/", response_model=schemas.Discount, status_code=201)
def create_discount(
    *,
    db: Session = Depends(deps.get_db),
    discount_in: schemas.DiscountCreate,
    current_user: models.User = Depends(deps.get_current_active_manager),
) -> Any:
    """
    Create a new discount. (Admin only)
    """
    obj_data = discount_in.dict()
    try:
        obj_data["discount_type"] = DiscountType(obj_data["discount_type"])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid discount_type")

    tour_ids = obj_data.pop("tour_ids", None)

    discount_obj = models.Discount(**obj_data)
    db.add(discount_obj)
    db.commit()
    db.refresh(discount_obj)

    # Attach discount to selected tours (one promotion per tour)
    if tour_ids:
        from app.models import Tour
        tours = db.query(Tour).filter(Tour.id.in_(tour_ids)).all()
        for t in tours:
            t.discount_id = discount_obj.id
        db.commit()

    return discount_obj

@router.get("/", response_model=List[schemas.Discount])
def read_discounts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all discounts. (Admin only)
    """
    discounts = crud.crud_discount.get_multi(db, skip=skip, limit=limit)
    return discounts

@router.get("/promotions/", response_model=List[schemas.Discount])
def read_active_promotions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve active promotions for clients.
    """
    promotions = db.query(models.Discount).filter(models.Discount.is_active == True).offset(skip).limit(limit).all()
    return promotions

@router.delete("/{discount_id}", status_code=204)
def delete_discount(
    *,
    discount_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_manager),
):
    """Delete a discount/promotion (manager/superuser)"""
    discount = crud.crud_discount.get(db, id=discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    # Снимаем скидку со всех туров, чтобы не нарушить FK
    from app.models import Tour
    affected_tours = db.query(Tour).filter(Tour.discount_id == discount_id).all()
    for t in affected_tours:
        t.discount_id = None
    db.commit()

    crud.crud_discount.remove(db, id=discount_id)
    return None

# ---------- Update promotion ----------

@router.put("/{discount_id}", response_model=schemas.Discount)
def update_discount(
    *,
    discount_id: int,
    db: Session = Depends(deps.get_db),
    discount_in: schemas.DiscountUpdate,
    current_user: models.User = Depends(deps.get_current_active_manager),
):
    """Update an existing discount and re-assign tours (manager/superuser)."""

    discount_obj = crud.crud_discount.get(db, id=discount_id)
    if not discount_obj:
        raise HTTPException(status_code=404, detail="Discount not found")

    obj_data = discount_in.dict(exclude_unset=True)

    tour_ids = obj_data.pop("tour_ids", None)

    # -------- update simple scalar fields --------
    for field, value in obj_data.items():
        if hasattr(discount_obj, field):
            setattr(discount_obj, field, value)

    # -------- Re-assign tours if list provided --------
    if tour_ids is not None:
        # Detach discount from tours that are no longer selected
        from app.models import Tour
        currently_attached = db.query(Tour).filter(Tour.discount_id == discount_id).all()
        for t in currently_attached:
            if t.id not in tour_ids:
                t.discount_id = None

        # Attach to newly selected tours
        if tour_ids:
            new_tours = db.query(Tour).filter(Tour.id.in_(tour_ids)).all()
            for t in new_tours:
                t.discount_id = discount_id

    db.commit()
    db.refresh(discount_obj)

    return discount_obj 
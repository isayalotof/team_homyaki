from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud import crud_user, crud_tour

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud_user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.post("/{user_id}/favorites/{tour_id}", response_model=schemas.User)
def add_favorite_tour(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    tour_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Add a tour to user's favorites.
    """
    if user_id != current_user.id and not crud_user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    tour = crud_tour.get(db, id=tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    user = crud_user.add_tour_to_favorites(db, user=user, tour=tour)
    return user


@router.delete("/{user_id}/favorites/{tour_id}", response_model=schemas.User)
def remove_favorite_tour(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    tour_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Remove a tour from user's favorites.
    """
    if user_id != current_user.id and not crud_user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tour = crud_tour.get(db, id=tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    user = crud_user.remove_tour_from_favorites(db, user=user, tour=tour)
    return user 
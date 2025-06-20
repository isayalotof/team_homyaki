from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud.crud_review import crud_review

router = APIRouter()


@router.get("/", response_model=List[schemas.Review])
def read_reviews(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    verified_only: bool = Query(True),
    tour_id: Optional[int] = Query(None),
) -> Any:
    """
    Retrieve reviews.
    """
    if tour_id:
        reviews = crud_review.get_multi_by_tour(
            db, tour_id=tour_id, skip=skip, limit=limit, verified_only=verified_only
        )
    else:
        reviews = crud_review.get_latest_reviews(
            db, limit=limit, verified_only=verified_only
        )
    return reviews


@router.post("/", response_model=schemas.Review)
def create_review(
    *,
    db: Session = Depends(deps.get_db),
    review_in: schemas.ReviewCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Create new review - works for both logged in users and guests.
    """
    # Добавляем отладочный вывод
    print(f"Creating review. Current user: {current_user}")
    print(f"Review data: {review_in}")
    
    # Проверяем, что есть либо tour_id, либо hotel_id
    if not review_in.tour_id and not review_in.hotel_id:
        raise HTTPException(status_code=400, detail="Either tour_id or hotel_id is required")
    
    try:
        # If user is authenticated, use their account details
        if current_user:
            print(f"Creating review as authorized user: {current_user.id}")
            # For logged in users, we don't need author_name/email
            review = crud_review.create_with_owner(
                db=db, obj_in=review_in, user_id=current_user.id
            )
        else:
            print("Creating review as guest")
            # For guests, we require author_name and author_email
            if not review_in.author_name or not review_in.author_email:
                raise HTTPException(
                    status_code=400, 
                    detail="Author name and email are required for guest reviews"
                )
            
            review = crud_review.create_as_guest(db=db, obj_in=review_in)
        
        print(f"Review created successfully: {review.id}")
        return review
    except Exception as e:
        print(f"Error creating review: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/latest", response_model=List[schemas.Review])
def get_latest_reviews(
    db: Session = Depends(deps.get_db),
    limit: int = 6,
) -> Any:
    """
    Get the latest verified reviews for the homepage.
    """
    reviews = crud_review.get_latest_reviews(db, limit=limit, verified_only=True)
    return reviews


@router.get("/stats/{tour_id}", response_model=dict)
def get_tour_review_stats(
    tour_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get review statistics for a specific tour.
    """
    stats = crud_review.get_tour_stats(db, tour_id=tour_id)
    return stats


@router.get("/{review_id}", response_model=schemas.Review)
def get_review(
    review_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific review by ID.
    """
    review = crud_review.get(db, id=review_id)
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )
    
    return review


@router.put("/{review_id}/verify", response_model=schemas.Review)
def verify_review(
    review_id: int,
    verified: bool = Body(..., embed=True),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_manager),
) -> Any:
    """
    Verify or unverify a review (admin/manager only).
    """
    review = crud_review.toggle_verification(db, review_id=review_id, verified=verified)
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )
    
    return review

@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Delete a review.
    Only the review author or an admin can delete a review.
    """
    review = crud_review.get(db, id=review_id)
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )
    
    # Check if the current user is the author or an admin
    if review.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    crud_review.remove(db, id=review_id)
    
    return None

@router.get("/test-route", status_code=200)
def test_review_route():
    """
    Test route to confirm API routing is working correctly.
    """
    return {"status": "success", "message": "Reviews API is working correctly"} 
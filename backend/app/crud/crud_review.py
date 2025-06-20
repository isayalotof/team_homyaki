from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: ReviewCreate, user_id: int
    ) -> Review:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id, verified=True)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_as_guest(
        self, db: Session, *, obj_in: ReviewCreate
    ) -> Review:
        """Create a review from a guest user"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, verified=False)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_tour(
        self, db: Session, *, tour_id: int, skip: int = 0, limit: int = 100, 
        verified_only: bool = False
    ) -> List[Review]:
        query = db.query(self.model).filter(Review.tour_id == tour_id)
        if verified_only:
            query = query.filter(Review.verified == True)
        return query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
        
    def get_latest_reviews(
        self, db: Session, *, limit: int = 6, verified_only: bool = True
    ) -> List[Review]:
        """Get the latest reviews across all tours/hotels"""
        query = db.query(self.model)
        if verified_only:
            query = query.filter(Review.verified == True)
        return query.order_by(desc(Review.created_at)).limit(limit).all()
    
    def toggle_verification(
        self, db: Session, *, review_id: int, verified: bool
    ) -> Review:
        """Toggle the verification status of a review"""
        review = db.query(self.model).filter(Review.id == review_id).first()
        if not review:
            return None
        review.verified = verified
        db.commit()
        db.refresh(review)
        return review
    
    def get_tour_stats(self, db: Session, *, tour_id: int) -> Dict[str, Any]:
        """Get review statistics for a tour"""
        reviews = db.query(self.model).filter(Review.tour_id == tour_id).all()
        if not reviews:
            return {"avg_rating": 0, "count": 0, "ratings": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}}
            
        total = len(reviews)
        avg = sum(r.rating for r in reviews) / total if total > 0 else 0
        
        # Count ratings by value
        ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in reviews:
            ratings[r.rating] = ratings.get(r.rating, 0) + 1
        
        return {
            "avg_rating": round(avg, 1),
            "count": total,
            "ratings": ratings
        }

    def remove(self, db: Session, *, id: int) -> Review:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


crud_review = CRUDReview(Review) 
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=2000)
    author_name: Optional[str] = Field(None, min_length=2, max_length=100)
    author_email: Optional[EmailStr] = None

class ReviewCreate(ReviewBase):
    tour_id: Optional[int] = None
    hotel_id: Optional[int] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v
    
    @validator('tour_id', 'hotel_id')
    def validate_ids(cls, v, values):
        # Ensure at least one of tour_id or hotel_id is provided
        if 'tour_id' in values and values['tour_id'] is None and v is None:
            raise ValueError('At least one of tour_id or hotel_id must be provided')
        return v

class ReviewUpdate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    tour_id: Optional[int] = None
    hotel_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime
    verified: bool = False
    
    class Config:
        from_attributes = True 
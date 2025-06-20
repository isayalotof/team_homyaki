from fastapi import APIRouter

from app.api.endpoints import (
    auth, users, tours, bookings, reviews, search, discounts
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tours.router, prefix="/tours", tags=["tours"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(discounts.router, prefix="/discounts", tags=["discounts"]) 
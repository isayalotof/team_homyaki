from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_

from app.crud.base import CRUDBase
from app.models.tour import Tour
from app.models.booking import Booking
from app.models.review import Review
from app.models.tour_type import TourType
from app.models.discount import Discount
from app.schemas.tour import TourCreate, TourUpdate


class CRUDTour(CRUDBase[Tour, TourCreate, TourUpdate]):
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Tour]:
        query = db.query(Tour)
        if active_only:
            query = query.filter(Tour.is_active == True)
        return query.order_by(desc(Tour.start_date)).offset(skip).limit(limit).all()
    
    def get_tours_with_booking_count(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        tours_with_count = (
            db.query(
                Tour,
                func.count(Booking.id).label("bookings_count")
            )
            .outerjoin(Booking, Tour.id == Booking.tour_id)
            .filter(Tour.is_active == True)
            .group_by(Tour.id)
            .order_by(desc(Tour.start_date))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        result = []
        for tour, count in tours_with_count:
            tour_dict = {
                **{c.name: getattr(tour, c.name) for c in tour.__table__.columns},
                "bookings_count": count
            }
            result.append(tour_dict)
            
        return result
    
    def search_tours(
        self, db: Session, *, destination: str = None, min_price: float = None, 
        max_price: float = None, start_date=None, skip: int = 0, limit: int = 100
    ) -> List[Tour]:
        query = db.query(Tour).filter(Tour.is_active == True)
        
        if destination:
            query = query.filter(Tour.destination.ilike(f"%{destination}%"))
        if min_price is not None:
            query = query.filter(Tour.price >= min_price)
        if max_price is not None:
            query = query.filter(Tour.price <= max_price)
        if start_date is not None:
            query = query.filter(Tour.start_date >= start_date)
            
        return query.order_by(desc(Tour.start_date)).offset(skip).limit(limit).all()

    def get_filtered_tours(
        self, 
        db: Session, 
        *, 
        page: int = 1, 
        page_size: int = 12, 
        sort_by: str = 'popularity',
        filters: Dict[str, Any],
        tour_types_order: List[int] = None
    ) -> Dict[str, Any]:
        
        query = db.query(Tour).outerjoin(Review).group_by(Tour.id)

        # Apply text search
        if query_str := filters.get('query'):
            query = query.filter(Tour.name.ilike(f"%{query_str}%"))

        # Apply filters
        if country := filters.get('country'):
            query = query.filter(Tour.country == country)
        if city := filters.get('city'):
            query = query.filter(Tour.city == city)
            
        # Фильтрация по городам из конструктора тура
        if destinations := filters.get('destinations'):
            # Если destinations - список городов, создаем условие OR для поиска по всем городам
            if isinstance(destinations, list) and destinations:
                destination_filters = []
                for dest in destinations:
                    destination_filters.append(Tour.destination.ilike(f"%{dest}%"))
                    destination_filters.append(Tour.name.ilike(f"%{dest}%"))
                query = query.filter(or_(*destination_filters))
            # Если destinations - строка, ищем по одному городу
            elif isinstance(destinations, str):
                query = query.filter(
                    or_(
                        Tour.destination.ilike(f"%{destinations}%"),
                        Tour.name.ilike(f"%{destinations}%")
                    )
                )
                
        if start_date := filters.get('start_date'):
            query = query.filter(Tour.start_date >= start_date)
        # Фильтрация по диапазону дат из конструктора тура
        if start_date_from := filters.get('start_date_from'):
            query = query.filter(Tour.start_date >= start_date_from)
        if start_date_to := filters.get('start_date_to'):
            query = query.filter(Tour.start_date <= start_date_to)
        if tourists := filters.get('tourists'):
            query = query.filter(Tour.available_count >= tourists)
            
        if duration_min := filters.get('duration_min'):
            query = query.filter(Tour.duration_days >= duration_min)
        if duration_max := filters.get('duration_max'):
            query = query.filter(Tour.duration_days <= duration_max)

        if price_min := filters.get('price_min'):
            query = query.filter(Tour.base_price >= price_min)
        if price_max := filters.get('price_max'):
            query = query.filter(Tour.base_price <= price_max)
            
        if tour_types := filters.get('tour_type'):
            query = query.join(Tour.tour_types).filter(TourType.id.in_(tour_types))

        if promotion_id := filters.get('promotion'):
            query = query.filter(Tour.discount_id == promotion_id)

        # Hotel-related filters require join
        if stars_list := filters.get('stars'):
            # Ensure stars_list is always a list, even if a single value is passed
            if not isinstance(stars_list, list):
                stars_list = [stars_list]
            stars_int = [int(s) for s in stars_list]
            query = query.filter(Tour.stars.in_(stars_int))
        
        # Фильтрация по звездам отеля из конструктора тура
        if hotel_stars := filters.get('hotel_stars'):
            query = query.filter(Tour.stars >= hotel_stars)

        if meal := filters.get('meal_type'):
            # Only apply filter if meal_type is not empty
            if meal:
                query = query.filter(Tour.meal_type == meal)

        # Count total items before pagination
        total_items = query.count()
        total_pages = (total_items + page_size - 1) // page_size

        # Apply sorting
        if sort_by == 'price_asc':
            query = query.order_by(asc(Tour.base_price))
        elif sort_by == 'price_desc':
            query = query.order_by(desc(Tour.base_price))
        elif sort_by == 'date':
            query = query.order_by(asc(Tour.start_date))
        elif sort_by == 'rating':
            query = query.order_by(desc(func.avg(Review.rating)))
        elif sort_by == 'duration':
            query = query.order_by(asc(Tour.duration_days))
        elif sort_by == 'priority' and tour_types_order:
            # For priority sorting, we need to get all matching tours first
            # then sort them based on the user's preferences
            tours = query.all()
            
            # Custom sorting based on tour type weights
            # Higher weight for types that appear earlier in the drag & drop list
            def get_tour_priority(tour):
                # Default low priority
                priority = 0
                
                # Get tour types for this tour
                tour_type_ids = [tt.id for tt in tour.tour_types]
                
                # Calculate priority based on position in tour_types_order
                # Earlier positions have higher weight
                for i, type_id in enumerate(tour_types_order):
                    if type_id in tour_type_ids:
                        # 10 - i gives higher weight to earlier positions (max 9)
                        weight = 9 - min(i, 8)  # Limit to 9 weights
                        priority += weight
                
                return priority
            
            # Sort tours by priority (higher first)
            sorted_tours = sorted(tours, key=get_tour_priority, reverse=True)
            
            # Apply pagination manually
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            tours = sorted_tours[start_idx:end_idx]
            
            # Build response and return early
            pagination_data = {
                "page": page,
                "per_page": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            }
            
            # Список всех активных акций (независимо от того, есть ли уже туры)
            promotions_list = db.query(Discount).filter(Discount.is_active == True).all()
            
            return {
                "tours": tours,
                "pagination": pagination_data,
                "promotions": promotions_list
            }
            
        else:  # Default to popularity (e.g., more reviews)
            query = query.order_by(desc(func.count(Review.id)))
            
        # Apply pagination
        tours = query.offset((page - 1) * page_size).limit(page_size).all()

        pagination_data = {
            "page": page,
            "per_page": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }

        # Список всех активных акций (независимо от того, есть ли уже туры)
        promotions_list = db.query(Discount).filter(Discount.is_active == True).all()

        return {
            "tours": tours,
            "pagination": pagination_data,
            "promotions": promotions_list
        }


crud_tour = CRUDTour(Tour) 
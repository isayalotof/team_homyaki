import logging
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models import User, UserRole, UserStatus, Tour, Booking, BookingStatus, Hotel, MealType
from app.models import Review, TourType, Discount, DiscountType


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


# Function to create initial data in the database
def init_db(db: Session) -> None:
    # Create test users
    create_test_users(db)
    
    # Create tour types
    create_tour_types(db)
    
    # Create hotels
    create_hotels(db)
    
    # Create tours
    create_tours(db)
    
    # Create discounts
    create_discounts(db)
    
    # Create bookings
    create_bookings(db)
    
    # Create reviews
    create_reviews(db)


def create_test_users(db: Session) -> None:
    logger.info("Creating test users")
    
    # Check if we already have users in the database
    user = db.query(User).first()
    if user:
        logger.info("Users already exist, skipping creation")
        return
    
    users_data = [
        {
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "Admin User",
            "phone": "+79001234567",
            "birth_date": date(1990, 1, 15),
            "role": UserRole.admin,
            "status": UserStatus.ACTIVE,
            "is_superuser": True
        },
        {
            "email": "manager@agency.com",
            "password": "manager123",
            "full_name": "Agency Manager",
            "phone": "+79011234567",
            "birth_date": date(1985, 5, 20),
            "role": UserRole.agency_manager,
            "status": UserStatus.ACTIVE
        },
        {
            "email": "operator@tour.com",
            "password": "operator123",
            "full_name": "Tour Operator",
            "phone": "+79021234567",
            "birth_date": date(1988, 8, 10),
            "role": UserRole.operator_manager,
            "status": UserStatus.ACTIVE
        },
        {
            "email": "client1@example.com",
            "password": "client123",
            "full_name": "Ivan Ivanov",
            "phone": "+79031234567",
            "birth_date": date(1995, 3, 25),
            "role": UserRole.client,
            "status": UserStatus.ACTIVE
        },
        {
            "email": "client2@example.com",
            "password": "client123",
            "full_name": "Maria Petrova",
            "phone": "+79041234567",
            "birth_date": date(1992, 7, 15),
            "role": UserRole.client,
            "status": UserStatus.ACTIVE
        }
    ]
    
    for user_data in users_data:
        db_user = User(
            email=user_data["email"],
            hashed_password=pwd_context.hash(user_data["password"]),
            full_name=user_data["full_name"],
            phone=user_data["phone"],
            birth_date=user_data["birth_date"],
            role=user_data["role"],
            status=user_data["status"],
            is_superuser=user_data.get("is_superuser", False)
        )
        db.add(db_user)
    
    db.commit()


def create_tour_types(db: Session) -> None:
    logger.info("Creating tour types")
    
    # Check if we already have tour types in the database
    tour_type = db.query(TourType).first()
    if tour_type:
        logger.info("Tour types already exist, skipping creation")
        return
    
    tour_types_data = [
        {
            "name": "Международный",
            "description": "Международные туры в разные страны мира"
        },
        {
            "name": "Внутренний",
            "description": "Туры по России"
        },
        {
            "name": "Детский",
            "description": "Туры для детей с развлекательной и образовательной программой"
        },
        {
            "name": "Лечебный",
            "description": "Лечебно-оздоровительные туры в санатории"
        },
        {
            "name": "Экскурсионный",
            "description": "Туры с насыщенной экскурсионной программой"
        }
    ]
    
    for type_data in tour_types_data:
        db_type = TourType(
            name=type_data["name"],
            description=type_data["description"]
        )
        db.add(db_type)
    
    db.commit()


def create_hotels(db: Session) -> None:
    logger.info("Creating hotels")
    
    # Check if we already have hotels in the database
    hotel = db.query(Hotel).first()
    if hotel:
        logger.info("Hotels already exist, skipping creation")
        return
    
    hotels_data = [
        {
            "name": "Приморский Resort & Spa",
            "address": "Россия, Сочи, ул. Приморская, 15",
            "stars": 5,
            "meal_type": MealType.AI,
            "description": "Роскошный курортный отель с собственным пляжем и спа-центром",
            "image_url": "/static/images/hotels/primorsky.jpg"
        },
        {
            "name": "Moscow Plaza Hotel",
            "address": "Россия, Москва, Тверская ул., 30",
            "stars": 4,
            "meal_type": MealType.BB,
            "description": "Бизнес-отель в центре Москвы с панорамным рестораном",
            "image_url": "/static/images/hotels/moscow_plaza.jpg"
        },
        {
            "name": "Golden Sands Resort",
            "address": "Турция, Анталья, Lara Beach, 5",
            "stars": 5,
            "meal_type": MealType.UAI,
            "description": "Роскошный курорт на берегу моря с аквапарком и анимацией",
            "image_url": "/static/images/hotels/golden_sands.jpg"
        },
        {
            "name": "Alpine Retreat",
            "address": "Австрия, Зальцбург, Alpine St. 42",
            "stars": 4,
            "meal_type": MealType.HB,
            "description": "Уютный отель в Альпах с видом на горы и спа-центром",
            "image_url": "/static/images/hotels/alpine.jpg"
        },
        {
            "name": "City Express Hotel",
            "address": "Россия, Санкт-Петербург, Невский пр., 15",
            "stars": 3,
            "meal_type": MealType.RO,
            "description": "Удобный отель в центре города с кафе и конференц-залом",
            "image_url": "/static/images/hotels/city_express.jpg"
        }
    ]
    
    for hotel_data in hotels_data:
        db_hotel = Hotel(
            name=hotel_data["name"],
            address=hotel_data["address"],
            stars=hotel_data["stars"],
            meal_type=hotel_data["meal_type"],
            description=hotel_data["description"],
            image_url=hotel_data["image_url"]
        )
        db.add(db_hotel)
    
    db.commit()


def create_tours(db: Session) -> None:
    logger.info("Creating tours")
    
    # Check if we already have tours in the database
    tour = db.query(Tour).first()
    if tour:
        logger.info("Tours already exist, skipping creation")
        return
    
    # Get tour types and hotels for relationships
    tour_types = {tour_type.name: tour_type for tour_type in db.query(TourType).all()}
    hotels = {hotel.name: hotel for hotel in db.query(Hotel).all()}
    
    # Calculate dates
    today = date.today()
    
    tours_data = [
        {
            "name": "Пляжный отдых в Сочи",
            "description": "Отдых на Черноморском побережье с проживанием в 5* отеле",
            "country": "Россия",
            "city": "Сочи",
            "base_price": 65000.00,
            "duration_days": 7,
            "max_tourists": 30,
            "available_count": 25,
            "start_date": today + timedelta(days=30),
            "end_date": today + timedelta(days=37),
            "image_url": "/static/images/tours/sochi.jpg",
            "hotel": "Приморский Resort & Spa",
            "tour_types": ["Внутренний", "Лечебный"]
        },
        {
            "name": "Экскурсионный тур по Москве",
            "description": "Культурный тур по главным достопримечательностям Москвы",
            "country": "Россия",
            "city": "Москва",
            "base_price": 45000.00,
            "duration_days": 5,
            "max_tourists": 20,
            "available_count": 15,
            "start_date": today + timedelta(days=15),
            "end_date": today + timedelta(days=20),
            "image_url": "/static/images/tours/moscow.jpg",
            "hotel": "Moscow Plaza Hotel",
            "tour_types": ["Внутренний", "Экскурсионный"]
        },
        {
            "name": "Всё включено в Турции",
            "description": "Роскошный отдых на побережье Средиземного моря",
            "country": "Турция",
            "city": "Анталья",
            "base_price": 85000.00,
            "duration_days": 10,
            "max_tourists": 40,
            "available_count": 30,
            "start_date": today + timedelta(days=45),
            "end_date": today + timedelta(days=55),
            "image_url": "/static/images/tours/turkey.jpg",
            "hotel": "Golden Sands Resort",
            "tour_types": ["Международный"]
        },
        {
            "name": "Горнолыжный тур в Альпы",
            "description": "Катание на лыжах в Австрийских Альпах",
            "country": "Австрия",
            "city": "Зальцбург",
            "base_price": 120000.00,
            "duration_days": 7,
            "max_tourists": 15,
            "available_count": 10,
            "start_date": today + timedelta(days=90),
            "end_date": today + timedelta(days=97),
            "image_url": "/static/images/tours/alps.jpg",
            "hotel": "Alpine Retreat",
            "tour_types": ["Международный", "Лечебный"]
        },
        {
            "name": "Детский лагерь «Юный исследователь»",
            "description": "Образовательная программа для детей с экскурсиями",
            "country": "Россия",
            "city": "Санкт-Петербург",
            "base_price": 50000.00,
            "duration_days": 14,
            "max_tourists": 30,
            "available_count": 20,
            "start_date": today + timedelta(days=60),
            "end_date": today + timedelta(days=74),
            "image_url": "/static/images/tours/kids_camp.jpg",
            "hotel": "City Express Hotel",
            "tour_types": ["Внутренний", "Детский", "Экскурсионный"]
        }
    ]
    
    for tour_data in tours_data:
        db_tour = Tour(
            name=tour_data["name"],
            description=tour_data["description"],
            country=tour_data["country"],
            city=tour_data["city"],
            base_price=tour_data["base_price"],
            duration_days=tour_data["duration_days"],
            max_tourists=tour_data["max_tourists"],
            available_count=tour_data["available_count"],
            start_date=tour_data["start_date"],
            end_date=tour_data["end_date"],
            image_url=tour_data["image_url"],
            hotel=hotels[tour_data["hotel"]]
        )
        
        # Add tour types
        for type_name in tour_data["tour_types"]:
            db_tour.tour_types.append(tour_types[type_name])
        
        db.add(db_tour)
    
    db.commit()


def create_discounts(db: Session) -> None:
    logger.info("Creating discounts")
    
    # Check if we already have discounts in the database
    discount = db.query(Discount).first()
    if discount:
        logger.info("Discounts already exist, skipping creation")
        return
    
    discounts_data = [
        {
            "name": "Раннее бронирование",
            "discount_type": DiscountType.PERCENTAGE,
            "value": 15.00,
            "description": "При бронировании тура за 60 дней до начала",
            "is_active": True,
            "target_city": "Сочи",
            "valid_from": date.today(),
            "valid_to": date.today() + timedelta(days=90)
        },
        {
            "name": "Семейная скидка",
            "discount_type": DiscountType.PERCENTAGE,
            "value": 10.00,
            "description": "Для семей с детьми от 3 человек",
            "is_active": True,
            "target_city": "Москва",
            "valid_from": date.today(),
            "valid_to": date.today() + timedelta(days=60)
        },
        {
            "name": "Постоянным клиентам",
            "discount_type": DiscountType.PERCENTAGE,
            "value": 7.00,
            "description": "При наличии 3 и более предыдущих поездок",
            "is_active": True,
            "valid_from": date.today(),
            "valid_to": date.today() + timedelta(days=120)
        },
        {
            "name": "Праздничная скидка",
            "discount_type": DiscountType.FIXED,
            "value": 5000.00,
            "description": "В период майских праздников",
            "is_active": False,
            "valid_from": date.today() + timedelta(days=30),
            "valid_to": date.today() + timedelta(days=45)
        },
        {
            "name": "Горящий тур",
            "discount_type": DiscountType.PERCENTAGE,
            "value": 20.00,
            "description": "При бронировании за 7 дней до начала тура",
            "is_active": True,
            "target_city": "Санкт-Петербург",
            "valid_from": date.today(),
            "valid_to": date.today() + timedelta(days=30),
            "image_url": "/static/images/promotions/promo_1b60ee9e82b84894ae9b7901175a6e99.jpeg"
        }
    ]
    
    for discount_data in discounts_data:
        db_discount = Discount(
            name=discount_data["name"],
            discount_type=discount_data["discount_type"],
            value=discount_data["value"],
            description=discount_data["description"],
            is_active=discount_data["is_active"],
            target_city=discount_data.get("target_city"),
            valid_from=discount_data.get("valid_from"),
            valid_to=discount_data.get("valid_to"),
            image_url=discount_data.get("image_url")
        )
        db.add(db_discount)
    
    db.commit()


def create_bookings(db: Session) -> None:
    logger.info("Creating bookings")
    
    # Check if we already have bookings in the database
    booking = db.query(Booking).first()
    if booking:
        logger.info("Bookings already exist, skipping creation")
        return
    
    # Get tours and users
    tours = db.query(Tour).all()
    users = db.query(User).filter(User.role == UserRole.client).all()
    
    if not tours or not users:
        logger.warning("No tours or users found, skipping booking creation")
        return
    
    # Create some sample bookings
    bookings_data = [
        {
            "user": users[0],
            "tour": tours[0],
            "tourists_count": 2,
            "total_price": tours[0].base_price * 2,
            "status": BookingStatus.CONFIRMED.value
        },
        {
            "user": users[1],
            "tour": tours[1],
            "tourists_count": 1,
            "total_price": tours[1].base_price,
            "status": BookingStatus.PAID.value
        },
        {
            "user": users[0],
            "tour": tours[2],
            "tourists_count": 3,
            "total_price": tours[2].base_price * 3,
            "status": BookingStatus.CREATED.value
        },
        {
            "user": users[1],
            "tour": tours[3],
            "tourists_count": 2,
            "total_price": tours[3].base_price * 2,
            "status": BookingStatus.CANCELLED.value
        }
    ]
    
    for booking_data in bookings_data:
        db_booking = Booking(
            user=booking_data["user"],
            tour=booking_data["tour"],
            tourists_count=booking_data["tourists_count"],
            total_price=booking_data["total_price"],
            status=booking_data["status"]
        )
        db.add(db_booking)
    
    db.commit()


def create_reviews(db: Session) -> None:
    logger.info("Creating reviews")
    
    # Check if we already have reviews in the database
    review = db.query(Review).first()
    if review:
        logger.info("Reviews already exist, skipping creation")
        return
    
    # Get tours and users
    tours = db.query(Tour).limit(3).all()
    users = db.query(User).filter(User.role == UserRole.client).all()
    
    if not tours or not users:
        logger.warning("No tours or users found, skipping review creation")
        return

    hotels = db.query(Hotel).all()
    
    reviews_data = [
        {
            "user": users[0],
            "tour": tours[0],
            "hotel": hotels[0],
            "rating": 5,
            "comment": "Отличный тур, все понравилось! Отель превзошел ожидания."
        },
        {
            "user": users[1],
            "tour": tours[1],
            "hotel": hotels[1],
            "rating": 4,
            "comment": "Хороший тур, но экскурсии можно было организовать лучше."
        },
        {
            "user": users[0],
            "tour": None,
            "hotel": hotels[2],
            "rating": 5,
            "comment": "Прекрасный отель с высоким уровнем сервиса."
        },
        {
            "user": users[1],
            "tour": tours[3],
            "hotel": hotels[3],
            "rating": 3,
            "comment": "Средний уровень сервиса, но горнолыжные трассы отличные."
        }
    ]
    
    for review_data in reviews_data:
        db_review = Review(
            user=review_data["user"],
            tour=review_data["tour"],
            hotel=review_data["hotel"],
            rating=review_data["rating"],
            comment=review_data["comment"]
        )
        db.add(db_review)
    
    db.commit() 
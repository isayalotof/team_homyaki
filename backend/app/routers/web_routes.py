from typing import Optional, List
from datetime import datetime, timedelta
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Form, Response, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.utils.email import send_password_reset_email


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    tours = crud.crud_tour.get_multi(db, limit=8)
    reviews = crud.crud_review.get_latest_reviews(db, limit=4, verified_only=True)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tours": tours,
            "reviews": reviews,
            "current_user": current_user,
            "now": datetime.now(),
        },
    )


@router.get("/tours", response_class=HTMLResponse)
async def tours_page(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
    search: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    promotion: Optional[int] = None,
    sort_by: Optional[str] = None,
    wizard: Optional[int] = None,
    page: int = Query(1, alias="page"),
):
    filters = {
        "query": search,
        "min_price": min_price,
        "max_price": max_price,
        "promotion": promotion,
    }
    
    # Обработка данных из конструктора тура
    wizard_data = None
    if wizard and search:
        try:
            import json
            wizard_data = json.loads(search)
            
            # Добавляем фильтры из wizard_data
            if "destinations" in wizard_data and wizard_data["destinations"]:
                city_names = [dest["name"] for dest in wizard_data["destinations"] if dest["type"] == "city"]
                if city_names:
                    filters["destinations"] = city_names
            
            if "dates" in wizard_data and wizard_data["dates"]:
                if wizard_data["dates"]["start"]:
                    filters["start_date_from"] = datetime.strptime(wizard_data["dates"]["start"], "%Y-%m-%d").date()
                if wizard_data["dates"]["end"]:
                    filters["start_date_to"] = datetime.strptime(wizard_data["dates"]["end"], "%Y-%m-%d").date()
            
            if "tourists" in wizard_data and wizard_data["tourists"]:
                adults = wizard_data["tourists"].get("adults", 0)
                children = wizard_data["tourists"].get("children", 0)
                filters["min_available"] = adults + children
            
            if "budget" in wizard_data:
                filters["max_price"] = wizard_data["budget"]
            
            if "preferences" in wizard_data and wizard_data["preferences"]:
                preferences = wizard_data["preferences"]
                if "accommodation" in preferences and preferences["accommodation"]:
                    if "stars" in preferences["accommodation"]:
                        filters["hotel_stars"] = preferences["accommodation"]["stars"]
        except Exception as e:
            print(f"Ошибка при обработке данных из конструктора: {e}")
    
    tours_data = crud.crud_tour.get_filtered_tours(
        db, filters=filters, sort_by=sort_by, page=page, page_size=12
    )

    return templates.TemplateResponse(
        "tours.html",
        {
            "request": request,
            "tours": tours_data["tours"],
            "pagination": tours_data["pagination"],
            "total_pages": tours_data["pagination"]["total_pages"],
            "current_user": current_user,
            "query_params": request.query_params,
            "now": datetime.now(),
            "promotions": tours_data["promotions"],
            "filters": filters,
            "wizard_data": wizard_data,
            "from_wizard": bool(wizard)
        },
    )


@router.get("/tours/{tour_id}", response_class=HTMLResponse)
async def tour_details(
    request: Request,
    tour_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    tour = crud.crud_tour.get(db, id=tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    reviews = crud.crud_review.get_multi_by_tour(db, tour_id=tour_id)
    related_tours = crud.crud_tour.get_multi(db, limit=4)
    stats = crud.crud_review.get_tour_stats(db, tour_id=tour_id)

    return templates.TemplateResponse(
        "tour_details.html",
        {
            "request": request,
            "tour": tour,
            "reviews": reviews,
            "stats": stats,
            "related_tours": [t for t in related_tours if t.id != tour.id][:3],
            "current_user": current_user,
        },
    )


@router.get("/booking/{tour_id}", response_class=HTMLResponse)
async def booking_form(
    request: Request,
    tour_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    tour = crud.crud_tour.get(db, id=tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    return templates.TemplateResponse(
        "booking.html",
        {"request": request, "tour": tour, "current_user": current_user},
    )


@router.get("/profile", response_class=HTMLResponse)
async def user_profile(
    request: Request,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    bookings = crud.crud_booking.get_multi_by_user(db, user_id=current_user.id)
    favorite_tours = current_user.favorite_tours
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request, 
            "current_user": current_user,
            "bookings": bookings,
            "favorite_tours": favorite_tours,
        },
    )


@router.get("/promotions", response_class=HTMLResponse)
async def promotions_page(
    request: Request, 
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional)
):
    promotions = db.query(models.Discount).filter(models.Discount.is_active == True).all()
    return templates.TemplateResponse("promotions.html", {"request": request, "promotions": promotions, "current_user": current_user})


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, current_user: Optional[models.User] = Depends(deps.get_current_user_optional)):
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request, "current_user": None})


@router.post("/login")
async def login_for_access_token(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = crud.crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user or not user.is_active:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "current_user": None,
                "error": "Неверный email или пароль",
            },
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response


@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request, current_user: Optional[models.User] = Depends(deps.get_current_user_optional)):
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("auth/register.html", {"request": request, "current_user": None})


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    db: Session = Depends(deps.get_db),
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    phone: Optional[str] = Form(None),
    birth_date: Optional[str] = Form(None),
):
    if password != password_confirm:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "current_user": None,
                "error": "Пароли не совпадают",
            },
        )
    # Check if user already exists
    user = crud.crud_user.get_by_email(db, email=email)
    if user:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "current_user": None,
                "error": "Пользователь с таким email уже существует",
            },
        )
    
    # Преобразуем строку даты в объект date, если она предоставлена
    birth_date_obj = None
    if birth_date:
        try:
            birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "current_user": None,
                    "error": "Неверный формат даты рождения. Используйте формат ГГГГ-ММ-ДД",
                },
            )
    
    # Create user
    user_in = schemas.UserCreate(
        full_name=full_name,
        email=email,
        password=password,
        phone=phone,
        birth_date=birth_date_obj,
        is_active=True,
        is_superuser=False
    )
    user = crud.crud_user.create(db, obj_in=user_in)
    # TODO: add logic to send confirmation email
    return templates.TemplateResponse("auth/login.html", {"request": request, "current_user": None, "message": "Регистрация прошла успешно! Теперь вы можете войти."})


@router.get("/search", response_class=HTMLResponse)
async def search_wizard(
    request: Request,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    return templates.TemplateResponse(
        "search_new.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


# Админ-роуты
@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form(
    request: Request, 
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional)
):
    # Если пользователь авторизован и является менеджером, перенаправляем на дашборд
    if current_user and current_user.role in [models.UserRole.agency_manager, models.UserRole.operator_manager, models.UserRole.admin]:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/admin/login")
async def admin_login_for_access_token(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = crud.crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user or not user.is_active:
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": request,
                "error": "Неверный email или пароль",
            },
        )
    
    # Проверка, что пользователь имеет роль менеджера или админа
    if user.role not in [models.UserRole.agency_manager, models.UserRole.operator_manager, models.UserRole.admin]:
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": request,
                "error": "У вас нет доступа к панели администратора",
            },
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response


@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_manager),
):
    # Получаем статистику для дашборда
    stats = {
        "total_tours": db.query(models.Tour).count(),
        "active_tours": db.query(models.Tour).filter(models.Tour.is_active == True).count(),
        "active_bookings": db.query(models.Booking).filter(models.Booking.status.in_([models.BookingStatus.PENDING, models.BookingStatus.CONFIRMED])).count(),
        "total_bookings": db.query(models.Booking).count(),
        "monthly_revenue": db.query(func.sum(models.Booking.total_price))
            .filter(models.Booking.status != models.BookingStatus.CANCELLED)
            .filter(models.Booking.booking_date >= datetime.now() - timedelta(days=30))
            .scalar() or 0,
        "new_clients": db.query(models.User)
            .filter(models.User.role == models.UserRole.client)
            .filter(models.User.date_of_birth >= datetime.now() - timedelta(days=30))
            .count()
    }
    
    # Получаем последние активности (последние 5 бронирований)
    recent_bookings = db.query(models.Booking).order_by(models.Booking.booking_date.desc()).limit(5).all()
    
    # Формируем данные для активностей
    activities = []
    for booking in recent_bookings:
        activity = {
            "title": f"Новое бронирование #{booking.id}",
            "description": f"Тур: {booking.tour.name}, Клиент: {booking.user.full_name}",
            "timestamp": booking.booking_date.strftime("%d.%m.%Y %H:%M"),
            "user": booking.user.full_name
        }
        activities.append(activity)
    
    # --- Chart Data ---
    # Monthly sales for last 12 months
    from calendar import month_abbr
    import json
    first_day_this_month = datetime(datetime.now().year, datetime.now().month, 1)
    months = []
    sales_values = []
    for i in range(11, -1, -1):
        month_start = first_day_this_month - timedelta(days=30*i)  # rough month shift
        month_label = month_abbr[month_start.month]
        month_end = month_start + timedelta(days=31)
        revenue = db.query(func.sum(models.Booking.total_price)).filter(
            models.Booking.status != models.BookingStatus.CANCELLED,
            models.Booking.booking_date >= month_start,
            models.Booking.booking_date < month_end
        ).scalar() or 0
        months.append(month_label)
        sales_values.append(float(revenue))

    # Booking status distribution
    status_labels = []
    status_counts = []
    for st in models.BookingStatus:
        count = db.query(models.Booking).filter(models.Booking.status == st).count()
        if count:
            status_labels.append(st.value)
            status_counts.append(count)

    # Popular destinations (top 6 tours by bookings)
    pop_labels = []
    pop_counts = []
    popular = (
        db.query(models.Tour.name, func.count(models.Booking.id).label('cnt'))
        .join(models.Booking, models.Booking.tour_id == models.Tour.id, isouter=True)
        .group_by(models.Tour.id)
        .order_by(func.count(models.Booking.id).desc())
        .limit(6)
        .all()
    )
    for name, cnt in popular:
        if cnt:
            pop_labels.append(name)
            pop_counts.append(cnt)

    return templates.TemplateResponse(
        "admin/dashboard.html", 
        {
            "request": request,
            "current_user": current_user,
            "stats": stats,
            "activities": activities,
            "sales_labels": json.dumps(months, ensure_ascii=False),
            "sales_values": json.dumps(sales_values),
            "status_labels": json.dumps(status_labels, ensure_ascii=False),
            "status_counts": json.dumps(status_counts),
            "pop_labels": json.dumps(pop_labels, ensure_ascii=False),
            "pop_counts": json.dumps(pop_counts),
        }
    )


@router.get("/admin/tours", response_class=HTMLResponse)
async def admin_tours(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_manager),
    search: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    tour_type: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, alias="page"),
):
    # Фильтры для поиска туров
    filters = {
        "query": search,
        "min_price": min_price,
        "max_price": max_price,
        "tour_type": tour_type,
        "status": status
    }
    
    # Получаем туры с пагинацией и фильтрами
    tours_data = crud.crud_tour.get_filtered_tours(
        db, filters=filters, page=page, page_size=10
    )
    
    # Получаем типы туров для фильтрации
    tour_types = db.query(models.TourType).all()
    
    # Получаем отели для формы создания тура
    hotels = db.query(models.Hotel).all()
    
    return templates.TemplateResponse(
        "admin/tours.html", 
        {
            "request": request,
            "current_user": current_user,
            "tours": tours_data["tours"],
            "pagination": tours_data["pagination"],
            "tour_types": tour_types,
            "hotels": hotels,
            "filters": filters
        }
    )


@router.get("/admin/bookings", response_class=HTMLResponse)
async def admin_bookings(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_manager),
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    tour_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, alias="page"),
):
    # Формируем фильтры для запроса
    query = db.query(models.Booking)
    
    if status:
        try:
            booking_status = models.BookingStatus(status)
            query = query.filter(models.Booking.status == booking_status)
        except ValueError:
            pass
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            query = query.filter(models.Booking.booking_date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date() + timedelta(days=1)
            query = query.filter(models.Booking.booking_date < date_to_obj)
        except ValueError:
            pass
    
    if tour_id:
        query = query.filter(models.Booking.tour_id == tour_id)
    
    if search:
        query = query.join(models.User).filter(
            (models.User.full_name.ilike(f"%{search}%")) | (models.User.email.ilike(f"%{search}%"))
        )
    
    # Получаем количество и список бронирований с пагинацией
    total = query.count()
    page_size = 15
    pages = (total + page_size - 1) // page_size
    bookings = query.order_by(models.Booking.booking_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # Формируем данные для пагинации
    pagination = {
        "total": total,
        "page_size": page_size,
        "current_page": page,
        "total_pages": pages
    }
    
    # Получаем список туров для фильтрации
    tours = db.query(models.Tour).order_by(models.Tour.name).all()
    
    return templates.TemplateResponse(
        "admin/bookings.html", 
        {
            "request": request,
            "current_user": current_user,
            "bookings": bookings,
            "pagination": pagination,
            "tours": tours
        }
    )


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_manager),
    role: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, alias="page"),
):
    # Формируем запрос с фильтрами
    query = db.query(models.User)
    
    if role:
        try:
            user_role = models.UserRole(role)
            query = query.filter(models.User.role == user_role)
        except ValueError:
            pass
    
    if status:
        active_status = status.lower() == 'active'
        query = query.filter(models.User.is_active == active_status)
    
    if search:
        query = query.filter(
            (models.User.full_name.ilike(f"%{search}%")) | 
            (models.User.email.ilike(f"%{search}%")) |
            (models.User.phone.ilike(f"%{search}%"))
        )
    
    # Получаем количество и список пользователей с пагинацией
    total = query.count()
    page_size = 15
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Добавляем сортировку по активности, чтобы активные пользователи были сверху
    query = query.order_by(models.User.is_active.desc(), models.User.id)
    
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Формируем данные для пагинации
    pagination = {
        "total": total,
        "page_size": page_size,
        "current_page": page,
        "total_pages": pages
    }
    
    return templates.TemplateResponse(
        "admin/users.html", 
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "pagination": pagination
        }
    )


@router.get("/admin/promotions", response_class=HTMLResponse)
async def admin_promotions(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_manager),
    type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, alias="page"),
):
    # Формируем запрос с фильтрами
    query = db.query(models.Discount)
    
    if type:
        query = query.filter(models.Discount.discount_type == type)
    if is_active is not None:
        query = query.filter(models.Discount.is_active == is_active)
    if search:
        query = query.filter(models.Discount.name.ilike(f"%{search}%"))
    
    # Пагинация
    total = query.count()
    page_size = 10
    total_pages = (total + page_size - 1) // page_size
    
    discounts = query.order_by(models.Discount.created_at.desc()).offset((page-1) * page_size).limit(page_size).all()
    
    # Формируем строку запроса для пагинации
    query_params = []
    if type:
        query_params.append(f"type={type}")
    if is_active is not None:
        query_params.append(f"is_active={str(is_active).lower()}")
    if search:
        query_params.append(f"search={search}")
    
    query_string = "&".join(query_params)
    if query_string:
        query_string = "&" + query_string
    
    # Получаем список туров для выбора в форме
    tours = db.query(models.Tour).filter(models.Tour.is_active == True).all()
    
    return templates.TemplateResponse(
        "admin/promotions.html",
        {
            "request": request,
            "current_user": current_user,
            "discounts": discounts,
            "tours": tours,
            "pagination": {
                "page": page,
                "total_pages": total_pages
            },
            "query_string": query_string,
            "filters": {
                "type": type,
                "is_active": is_active,
                "search": search,
            }
        },
    )


@router.get("/admin/reviews", response_class=HTMLResponse)
async def admin_reviews(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_manager),
    verified: Optional[str] = None,
    rating: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, alias="page"),
):
    """
    Admin page for managing reviews
    """
    # Build query with filters
    query = db.query(models.Review)
    
    if verified == "true":
        query = query.filter(models.Review.verified == True)
    elif verified == "false":
        query = query.filter(models.Review.verified == False)
        
    if rating:
        try:
            rating_value = int(rating)
            query = query.filter(models.Review.rating == rating_value)
        except ValueError:
            pass
        
    if search:
        query = query.filter(
            or_(
                models.Review.author_name.ilike(f"%{search}%"),
                models.Review.comment.ilike(f"%{search}%"),
                # Search in user names if there's a user
                models.User.full_name.ilike(f"%{search}%")
            )
        ).outerjoin(models.User)
    
    # Pagination
    total = query.count()
    page_size = 20
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Get reviews with sorting
    reviews = query.order_by(
        models.Review.verified.asc(), 
        models.Review.created_at.desc()
    ).offset((page-1) * page_size).limit(page_size).all()
    
    # Build query string for pagination links
    query_params = []
    if verified is not None:
        query_params.append(f"verified={verified}")
    if rating is not None:
        query_params.append(f"rating={rating}")
    if search:
        query_params.append(f"search={search}")
    
    query_string = "&".join(query_params)
    if query_string:
        query_string = "&" + query_string
    
    return templates.TemplateResponse(
        "admin/reviews.html",
        {
            "request": request,
            "current_user": current_user,
            "reviews": reviews,
            "pagination": {
                "page": page,
                "total_pages": total_pages,
                "total_items": total
            },
            "query_string": query_string,
        },
    )


@router.get("/about", response_class=HTMLResponse)
async def about_page(
    request: Request,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get("/contacts", response_class=HTMLResponse)
async def contacts_page(
    request: Request,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    return templates.TemplateResponse(
        "contacts.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get("/faq", response_class=HTMLResponse)
async def faq_page(
    request: Request,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    return templates.TemplateResponse(
        "faq.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get("/terms", response_class=HTMLResponse)
async def terms_page(
    request: Request,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    return templates.TemplateResponse(
        "terms.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_page(
    request: Request,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    return templates.TemplateResponse(
        "privacy.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get("/blog", response_class=HTMLResponse)
async def blog_page(
    request: Request,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
    page: int = Query(1, alias="page"),
):
    # В будущем здесь можно добавить логику получения статей блога из базы данных
    return templates.TemplateResponse(
        "blog.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get("/reviews", response_class=HTMLResponse)
async def reviews_page(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit"),
):
    """
    Dedicated page for reviews with statistics and submission form.
    """
    # Get reviews with pagination
    skip = (page - 1) * limit
    reviews = crud.crud_review.get_latest_reviews(
        db, limit=limit, verified_only=True
    )
    
    # Get total count for pagination
    total = db.query(models.Review).filter(models.Review.verified == True).count()
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    
    # Get review statistics
    all_reviews = db.query(models.Review).filter(models.Review.verified == True).all()
    total_reviews = len(all_reviews)
    avg_rating = sum(r.rating for r in all_reviews) / total_reviews if total_reviews > 0 else 0
    
    # Count ratings by value
    ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in all_reviews:
        ratings[r.rating] = ratings.get(r.rating, 0) + 1
    
    # Get tours for the dropdown
    tours = crud.crud_tour.get_multi(db, limit=50)
    
    return templates.TemplateResponse(
        "reviews.html",
        {
            "request": request,
            "current_user": current_user,
            "reviews": reviews,
            "pagination": {
                "page": page,
                "per_page": limit,
                "total_items": total,
                "total_pages": total_pages,
            },
            "total_reviews": total_reviews,
            "avg_rating": avg_rating,
            "ratings": ratings,
            "tours": tours,
        },
    )


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_form(
    request: Request,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
):
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "auth/forgot-password.html", 
        {
            "request": request, 
            "current_user": None, 
            "reset_sent": False
        }
    )


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    email: str = Form(...),
):
    user = crud.crud_user.get_by_email(db, email=email)
    
    # Временно отключена функциональность сброса пароля
    # Показываем сообщение об успешной отправке в любом случае
    return templates.TemplateResponse(
        "auth/forgot-password.html",
        {
            "request": request,
            "current_user": None,
            "reset_sent": True,
            "message": "Функция восстановления пароля временно недоступна. Пожалуйста, свяжитесь с администратором."
        },
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(
    request: Request,
    token: str,
    db: Session = Depends(deps.get_db),
):
    # Временно отключена функциональность сброса пароля
    return templates.TemplateResponse(
        "auth/reset-password.html",
        {
            "request": request,
            "token": token,
            "token_valid": False,
            "error": "Функция восстановления пароля временно недоступна. Пожалуйста, свяжитесь с администратором.",
            "current_user": None
        },
    )


@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(deps.get_db),
):
    # Временно отключена функциональность сброса пароля
    return templates.TemplateResponse(
        "auth/reset-password.html",
        {
            "request": request,
            "token": token,
            "token_valid": False,
            "error": "Функция восстановления пароля временно недоступна. Пожалуйста, свяжитесь с администратором.",
            "current_user": None
        },
    )


@router.get("/offline", response_class=HTMLResponse)
async def offline(request: Request):
    return templates.TemplateResponse(
        "offline.html",
        {
            "request": request,
            "current_user": None,
        },
    )


@router.get("/static/manifest.json")
async def manifest():
    return FileResponse("app/static/manifest.json")


@router.get("/admin/profile", response_class=HTMLResponse)
async def admin_profile(
    request: Request,
    current_user: models.User = Depends(deps.get_current_active_manager),
):
    return templates.TemplateResponse(
        "admin/profile.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(
    request: Request,
    current_user: models.User = Depends(deps.get_current_active_manager),
):
    return templates.TemplateResponse(
        "admin/settings.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    return templates.TemplateResponse("404.html", {"request": request, "current_user": None}, status_code=404)
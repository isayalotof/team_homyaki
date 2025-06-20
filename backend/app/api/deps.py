from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/access-token",
    auto_error=False
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
) -> models.User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        # Больше не проверяем префикс Bearer, так как мы его не добавляем
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.crud_user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_active_manager(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role not in [models.UserRole.agency_manager, models.UserRole.operator_manager, models.UserRole.admin]:
        raise HTTPException(
            status_code=403, detail="У вас недостаточно прав для доступа к этой странице"
        )
    return current_user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(reusable_oauth2),
    access_token: Optional[str] = Cookie(None)
) -> Optional[models.User]:
    """
    Validates the token if present and returns the user or None if no valid token.
    This function should not raise exceptions for auth failures.
    """
    # Prefer the Authorization header token, fallback to the access_token cookie
    jwt_token = token or access_token
    
    if not jwt_token:
        # Проверим, может быть токен в state или cookies
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return crud.crud_user.get(db, id=user_id)
        return None
    
    try:
        payload = jwt.decode(
            jwt_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        # Не вызываем исключение при ошибке валидации, просто возвращаем None
        return None
    
    user = crud.crud_user.get(db, id=token_data.sub)
    return user 
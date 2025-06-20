from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional

from app.core.config import settings
from app.api.api import api_router
from app.db.session import engine, Base, get_db
from app.models.user import User
from app.core.security import decode_access_token
from app.routers import web_router
from sqlalchemy.orm import Session

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Путешествуй по России API",
    description="API для туристического агентства Путешествуй по России",
    version="0.1.0",
)

# Configure CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API router is separated from the main app to ensure it has priority
api_app = FastAPI(
    title="Путешествуй по России API - только API",
    docs_url=None,
    redoc_url=None,
)

# Add error handling middleware to the API app
@api_app.middleware("http")
async def api_exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        print(f"API ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        # Возвращаем ошибку в формате JSON вместо HTML
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Internal Server Error: {str(e)}"}
        )

# Register API routes explicitly
api_app.include_router(api_router)

# Mount the API app at the API prefix path
# This ensures API routes are handled separately with highest priority
app.mount(settings.API_PREFIX, api_app)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include web router for all other routes
app.include_router(web_router, include_in_schema=False)

# Authentication middleware
@app.middleware("http")
async def authenticate_user(request: Request, call_next):
    request.state.user_id = None
    token = request.cookies.get("access_token")
    if token:
        # Больше не проверяем префикс Bearer, так как мы его не добавляем
        try:
            payload = decode_access_token(token)
            if payload:
                request.state.user_id = payload.get("sub")
        except (JWTError, AttributeError):
            # Invalid token, proceed as anonymous user, clear bad cookie
            response = await call_next(request)
            response.delete_cookie("access_token")
            return response

    # Define protected routes that require a valid user
    protected_paths = ['/admin', '/profile', '/booking']
    is_protected = any(request.url.path.startswith(p) for p in protected_paths)

    if is_protected and not request.state.user_id:
        # For protected routes, if no valid user, redirect to login
        return RedirectResponse(url=f"/login?next={request.url.path}", status_code=status.HTTP_303_SEE_OTHER)

    response = await call_next(request)
    return response

# API routing middleware to ensure API calls are correctly handled
@app.middleware("http")
async def route_api_calls(request: Request, call_next):
    # Log requests for debugging
    print(f"Request: {request.method} {request.url.path}")
    
    # Check if this is an API request
    if request.url.path.startswith(settings.API_PREFIX):
        print(f"API request detected: {request.method} {request.url.path}")
    
    response = await call_next(request)
    return response

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/debug-routes")
async def debug_routes():
    """Debug endpoint to list all registered routes."""
    routes = []
    for route in app.routes:
        routes.append({
            "path": getattr(route, "path", None),
            "name": getattr(route, "name", None),
            "methods": getattr(route, "methods", None),
        })
    return {"routes": routes}

# Configure API docs in main app
app.openapi_url = f"{settings.API_PREFIX}/openapi.json"
app.docs_url = f"{settings.API_PREFIX}/docs"
app.redoc_url = f"{settings.API_PREFIX}/redoc" 
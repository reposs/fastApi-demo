from fastapi import APIRouter

from app.api.routers import auth, health, users

api_v1_router = APIRouter()

# Modular routing for v1 API endpoints
api_v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(users.router, tags=["users"])
api_v1_router.include_router(health.router, tags=["health"])

__all__ = ["api_v1_router"]

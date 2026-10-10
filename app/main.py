import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import auth, health, users
from app.api.v1.api import api_v1_router
from app.core.config import settings
from app.core.db.database import engine, init_db
from app.core.exceptions import AppException

# OpenAPI tags documentation
tags_metadata = [
    {
        "name": "auth",
        "description": "Authentication and authorization operations (JWT generation, login, register, profile).",
    },
    {
        "name": "users",
        "description": "User CRUD operations, pagination and profile management.",
    },
    {
        "name": "health",
        "description": "System liveness, readiness and database connectivity checks.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown events."""
    # Startup: ensure tables exist in dev / test environments
    try:
        init_db()
    except Exception as exc:
        # Avoid crashing startup if DB is offline; health checks will report status
        pass

    yield

    # Shutdown: gracefully dispose engine connection pool
    engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Performance Tracking Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    return response


# 3. Centralized Domain Exception Handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application domain exceptions with consistent JSON formatting."""
    content: dict[str, Any] = {
        "detail": exc.message,
        "error_code": exc.error_code,
    }
    if exc.details:
        content["details"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


# 4. Welcome & Health Root Endpoint
@app.get("/", tags=["health"], summary="Root service status")
def root() -> dict[str, Any]:
    return {
        "message": "Hello World!, It's a FastAPI demo by R.David Marquez",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_STR,
    }


# 5. Modular API Routers (v1)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# 6. Backwards-compatible Direct Routes (matches original routes)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)

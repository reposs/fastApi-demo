from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, status
from sqlalchemy import text
from sqlmodel import Session

from app.api.dependencies import DatabaseSession
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Service health check",
    description="Returns service availability, application name, version, and server timestamp.",
)
def health_check() -> dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/db",
    status_code=status.HTTP_200_OK,
    summary="Database connectivity check",
    description="Executes a ping query to verify database connection pool status.",
)
def database_health(session: DatabaseSession) -> dict[str, Any]:
    """Database connectivity health check."""
    try:
        session.exec(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"unreachable: {exc}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.now(UTC).isoformat(),
    }

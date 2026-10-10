from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# Determine engine parameters based on database driver
engine_kwargs: dict = {
    "pool_pre_ping": settings.DB_POOL_PRE_PING,
}

if settings.sync_database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE

engine = create_engine(settings.sync_database_url, **engine_kwargs)


def init_db() -> None:
    """Initialize database tables defined in SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and ensures rollback on failure."""
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


__all__ = ["engine", "get_db", "init_db"]
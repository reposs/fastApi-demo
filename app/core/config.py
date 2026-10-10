import os
from functools import lru_cache
from typing import Annotated
from urllib.parse import quote_plus

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class _BaseSettingsConfig(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )

except ImportError:
    # Graceful fallback if pydantic-settings is not yet installed in local environment
    from pydantic import BaseModel

    class _BaseSettingsConfig(BaseModel):  # type: ignore[no-redef]
        def __init__(self, **data):
            super().__init__(**data)

from pydantic import Field, computed_field


class Settings(_BaseSettingsConfig):
    # Application Info
    PROJECT_NAME: str = Field(default="fastApi-demo", description="Application name")
    VERSION: str = Field(default="0.1.0", description="Application version")
    DESCRIPTION: str = Field(
        default="High-performance, production-ready FastAPI demo service with authentication, user management and Clean Architecture.",
        description="Application description",
    )
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins",
    )

    # Database Configuration
    DATABASE_URL: str | None = Field(
        default_factory=lambda: os.getenv("DATABASE_URL"),
        description="Direct database URL string",
    )
    DB_HOST: str = Field(
        default_factory=lambda: os.getenv("DB_HOST", "aws-1-eu-west-1.pooler.supabase.com")
    )
    DB_PORT: int = Field(
        default_factory=lambda: int(os.getenv("DB_PORT", "5432"))
    )
    DB_NAME: str = Field(
        default_factory=lambda: os.getenv("DB_NAME", "postgres")
    )
    DB_USER: str = Field(
        default_factory=lambda: os.getenv("DB_USER", "postgres")
    )
    DB_PASSWORD: str | None = Field(
        default_factory=lambda: os.getenv("DB_PASSWORD")
    )

    # Database Connection Pool Settings
    DB_POOL_SIZE: int = Field(default=5, description="Connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    DB_POOL_PRE_PING: bool = Field(default=True, description="Enable connection pre-ping")
    DB_POOL_RECYCLE: int = Field(default=300, description="Recycle connections in seconds")

    # JWT & Security Configuration
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", "insecure-fallback-secret-key-change-me"),
        description="Secret key for signing JWT tokens",
    )
    JWT_ALGORITHM: str = Field(
        default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"),
        description="JWT algorithm",
    )
    JWT_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(os.getenv("JWT_EXPIRE_MINUTES", "30")),
        description="Access token expiration in minutes",
    )

    # Demo credentials (optional initial seeding)
    DEMO_EMAIL: str = Field(
        default_factory=lambda: os.getenv("DEMO_EMAIL", "johndoe@example.com")
    )
    DEMO_PASSWORD: str = Field(
        default_factory=lambda: os.getenv("DEMO_PASSWORD", "Secret123!")
    )
    DEMO_FIRSTNAME: str = Field(
        default_factory=lambda: os.getenv("DEMO_FIRSTNAME", "John")
    )
    DEMO_LASTNAME: str = Field(
        default_factory=lambda: os.getenv("DEMO_LASTNAME", "Doe")
    )

    @computed_field
    @property
    def sync_database_url(self) -> str:
        """Returns the PostgreSQL connection string or an in-memory SQLite for testing/fallback."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.DB_PASSWORD:
            username = quote_plus(self.DB_USER)
            encoded_password = quote_plus(self.DB_PASSWORD)
            return (
                f"postgresql+psycopg://{username}:{encoded_password}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

        # Fallback to local SQLite when no database credentials are provided
        return "sqlite:///./app_local.db"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings."""
    return Settings()


settings = get_settings()

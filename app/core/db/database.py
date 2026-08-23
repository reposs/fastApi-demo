import os
from collections.abc import Generator
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlmodel import Session, create_engine


load_dotenv()


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    password = os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "Define DATABASE_URL or DB_PASSWORD before starting the application"
        )

    username = quote_plus(os.getenv("DB_USER", "postgres"))
    encoded_password = quote_plus(password)
    host = os.getenv("DB_HOST", "aws-1-eu-west-1.pooler.supabase.com")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "postgres")
    return (
        f"postgresql+psycopg://{username}:{encoded_password}"
        f"@{host}:{port}/{database}"
    )


engine = create_engine(_get_database_url(), pool_pre_ping=True)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as db:
        yield db
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from dotenv import load_dotenv
from jose import JWTError, jwt
from pwdlib import PasswordHash

load_dotenv()

password_hash = PasswordHash.recommended()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def _get_jwt_secret_key() -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError("Define JWT_SECRET_KEY in .env before using authentication")
    return JWT_SECRET_KEY


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": subject, "exp": expires_at},
        _get_jwt_secret_key(),
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, _get_jwt_secret_key(), algorithms=[JWT_ALGORITHM])


__all__ = ["JWTError", "create_access_token", "decode_access_token", "hash_password", "verify_password"]
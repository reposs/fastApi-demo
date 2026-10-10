import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings

# 1. Password Hashing with Argon2 (via pwdlib) or standard library fallback
try:
    from pwdlib import PasswordHash

    _password_hash = PasswordHash.recommended()

    def hash_password(password: str) -> str:
        """Hash a plain text password using Argon2."""
        return _password_hash.hash(password)

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a stored hash."""
        return _password_hash.verify(plain_password, hashed_password)

except ImportError:
    # Graceful fallback for minimal environments
    def hash_password(password: str) -> str:
        salt = "argon2_simulated_salt_"
        digest = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"sha256:{digest}"

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        salt = "argon2_simulated_salt_"
        expected = f"sha256:{hashlib.sha256((salt + plain_password).encode()).hexdigest()}"
        return hmac.compare_digest(expected, hashed_password)


# 2. JWT Encoding / Decoding with python-jose or standard library fallback
try:
    from jose import JWTError, jwt

    def create_access_token(
        subject: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a signed JWT access token."""
        if expires_delta is not None:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

        to_encode: dict[str, Any] = {
            "sub": str(subject),
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def decode_access_token(token: str) -> dict[str, Any]:
        """Decode and validate a JWT access token."""
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

except ImportError:
    class JWTError(Exception):
        """JWT Decode error fallback."""
        pass

    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode().rstrip("=")

    def _b64url_decode(data: str) -> bytes:
        padding = "=" * (4 - (len(data) % 4))
        return base64.urlsafe_b64decode((data + padding).encode())

    def create_access_token(
        subject: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        if expires_delta is not None:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

        header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        payload_data = {
            "sub": str(subject),
            "exp": int(expire.timestamp()),
            "type": "access",
        }
        payload = _b64url_encode(json.dumps(payload_data).encode())
        signing_input = f"{header}.{payload}".encode()
        signature = _b64url_encode(
            hmac.new(settings.JWT_SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        )
        return f"{header}.{payload}.{signature}"

    def decode_access_token(token: str) -> dict[str, Any]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise JWTError("Invalid token format")
            header, payload, signature = parts
            signing_input = f"{header}.{payload}".encode()
            expected_sig = _b64url_encode(
                hmac.new(settings.JWT_SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
            )
            if not hmac.compare_digest(expected_sig, signature):
                raise JWTError("Invalid signature")
            data = json.loads(_b64url_decode(payload).decode())
            if "exp" in data and datetime.now(UTC).timestamp() > data["exp"]:
                raise JWTError("Token expired")
            return data
        except Exception as exc:
            raise JWTError(str(exc)) from exc


__all__ = [
    "JWTError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
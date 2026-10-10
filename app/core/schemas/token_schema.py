from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

try:
    import email_validator  # noqa: F401
    from pydantic import EmailStr
except ImportError:
    # Graceful fallback when email-validator package is not yet installed
    EmailStr = Annotated[str, Field(pattern=r"^[\w\.\+-]+@[\w\.-]+\.\w+$")]  # type: ignore[misc, assignment]


class Token(BaseModel):
    """JWT access token response model."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(description="JWT access token string")
    token_type: str = Field(default="bearer", description="Token type, standard Bearer")
    expires_in: int = Field(description="Token expiration time in seconds")


class TokenPayload(BaseModel):
    """Decoded JWT payload data."""

    sub: str | None = Field(default=None, description="Subject (user identifier/email)")
    exp: int | None = Field(default=None, description="Expiration timestamp")


class LoginRequest(BaseModel):
    """JSON login request payload."""

    email: EmailStr = Field(description="User registered email address")
    password: str = Field(min_length=1, description="User password")

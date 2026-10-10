import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

try:
    import email_validator  # noqa: F401
    from pydantic import EmailStr
except ImportError:
    # Graceful fallback when email-validator package is not yet installed
    EmailStr = Annotated[str, Field(pattern=r"^[\w\.\+-]+@[\w\.-]+\.\w+$")]  # type: ignore[misc, assignment]

from app.core.validators.password_validator import validate_password


class UserBase(BaseModel):
    """Base user properties shared across create and response schemas."""

    firstname: Annotated[
        str,
        Field(min_length=2, max_length=50, description="User first name", examples=["John"]),
    ]
    lastname: Annotated[
        str | None,
        Field(default=None, min_length=2, max_length=50, description="User last name", examples=["Doe"]),
    ] = None
    email: Annotated[
        EmailStr,
        Field(description="User valid email address", examples=["johndoe@example.com"]),
    ]
    disabled: Annotated[
        bool,
        Field(default=False, description="Whether the user account is disabled"),
    ] = False


class UserCreate(UserBase):
    """Schema for user registration / creation."""

    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=64,
            description="User password meeting complexity requirements",
            examples=["SecurePassword1!"],
        ),
        AfterValidator(validate_password),
    ]


class UserResponse(UserBase):
    """Public user response schema - never exposes password."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Unique user identifier")
    created_at: datetime.datetime = Field(description="Timestamp of user registration (UTC)")


class UserUpdate(BaseModel):
    """Schema for updating user details."""

    model_config = ConfigDict(from_attributes=True)

    firstname: Annotated[
        str | None,
        Field(default=None, min_length=2, max_length=50, description="User first name", examples=["John"]),
    ] = None
    lastname: Annotated[
        str | None,
        Field(default=None, min_length=2, max_length=50, description="User last name", examples=["Doe"]),
    ] = None
    email: Annotated[
        EmailStr | None,
        Field(default=None, description="User email address", examples=["johndoe@example.com"]),
    ] = None
    disabled: Annotated[
        bool | None,
        Field(default=None, description="Disabled status flag"),
    ] = None
    password: Annotated[
        str | None,
        Field(
            default=None,
            min_length=8,
            max_length=64,
            description="New password (optional)",
            examples=["NewSecurePassword2!"],
        ),
        AfterValidator(validate_password),
    ] = None


class UserListResponse(BaseModel):
    """Paginated user list response."""

    model_config = ConfigDict(from_attributes=True)

    total: int = Field(ge=0, description="Total matching user count")
    items: list[UserResponse] = Field(description="List of users for the current page")
    skip: int = Field(ge=0, description="Current offset")
    limit: int = Field(ge=1, description="Page limit")
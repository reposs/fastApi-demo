import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, EmailStr, Field

from app.core.validators.password_validator import validate_password


class UserIn(BaseModel):
    id: UUID | None = None
    created_at: datetime.datetime | None = None
    firstname: Annotated[
        str,
        Field(min_length=3, max_length=50, description="The user firstname"),
    ]
    lastname: Annotated[
        str | None,
        Field(min_length=3, max_length=50, description="The user lastname"),
    ] = None
    email: Annotated[EmailStr, Field(description="The user email")]
    disabled: bool = False
    password: Annotated[
        str,
        Field(min_length=8, max_length=64),
        AfterValidator(validate_password),
    ]


class UserOut(BaseModel):
    id: UUID
    created_at: datetime.datetime | None = None
    firstname: str
    lastname: str | None = None
    email: EmailStr
    disabled: bool = False


class UserUpdate(BaseModel):
    firstname: Annotated[
        str | None,
        Field(min_length=3, max_length=50),
    ] = None
    lastname: Annotated[str | None, Field(min_length=3, max_length=50)] = None
    email: EmailStr | None = None
    disabled: bool | None = None
    password: Annotated[
        str | None,
        Field(min_length=8, max_length=64),
        AfterValidator(validate_password),
    ] = None
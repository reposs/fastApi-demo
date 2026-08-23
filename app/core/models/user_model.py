import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    firstname: str = Field(max_length=50)
    lastname: str | None = Field(default=None, max_length=50)
    email: str = Field(max_length=320, unique=True, index=True)
    disabled: bool = Field(default=False)
    password: str = Field(max_length=255)
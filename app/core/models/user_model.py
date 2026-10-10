import datetime
from uuid import UUID, uuid4

try:
    from sqlmodel import Field, SQLModel
except ImportError:
    # Graceful fallback when sqlmodel is not installed
    from pydantic import BaseModel, Field  # type: ignore[no-redef]

    class SQLModel(BaseModel):  # type: ignore[no-redef]
        def __init_subclass__(cls, table: bool = False, **kwargs):
            super().__init_subclass__(**kwargs)


class UserModel(SQLModel, table=True):
    """Database model for application users."""

    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        description="Unique identifier (UUIDv4)",
    )
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
        description="User creation timestamp (UTC)",
    )
    firstname: str = Field(
        max_length=50,
        nullable=False,
        description="User first name",
    )
    lastname: str | None = Field(
        default=None,
        max_length=50,
        nullable=True,
        description="User last name",
    )
    email: str = Field(
        max_length=320,
        unique=True,
        index=True,
        nullable=False,
        description="User unique email address",
    )
    disabled: bool = Field(
        default=False,
        nullable=False,
        description="Flag indicating if the account is deactivated",
    )
    password: str = Field(
        max_length=255,
        nullable=False,
        description="Hashed password (Argon2 / pwdlib)",
    )

    def __repr__(self) -> str:
        return f"<UserModel id={self.id} email={self.email} disabled={self.disabled}>"
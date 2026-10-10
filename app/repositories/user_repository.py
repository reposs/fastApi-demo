from collections.abc import Sequence
from uuid import UUID

try:
    from sqlalchemy import func
    from sqlmodel import Session, select
except ImportError:
    class Session:  # type: ignore[no-redef]
        pass

    class _Func:
        @staticmethod
        def count():
            return "count"

        @staticmethod
        def lower(col):
            return col

    func = _Func()  # type: ignore[assignment]
    select = None  # type: ignore[assignment]

from app.core.models.user_model import UserModel


class UserRepository:
    """Repository pattern implementation for user persistence operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: UUID) -> UserModel | None:
        """Fetch a user by their unique UUID."""
        return self.session.get(UserModel, user_id)

    def get_by_email(self, email: str) -> UserModel | None:
        """Fetch a user by their email address (case-insensitive search)."""
        normalized = email.strip().lower()
        statement = select(UserModel).where(func.lower(UserModel.email) == normalized)
        return self.session.exec(statement).first()

    def exists_by_email(self, email: str, exclude_id: UUID | None = None) -> bool:
        """Check if an email is already registered, optionally excluding an existing user ID."""
        normalized = email.strip().lower()
        statement = select(UserModel.id).where(func.lower(UserModel.email) == normalized)
        if exclude_id is not None:
            statement = statement.where(UserModel.id != exclude_id)
        return self.session.exec(statement).first() is not None

    def list(self, skip: int = 0, limit: int = 10) -> list[UserModel]:
        """List users with offset pagination."""
        statement = select(UserModel).offset(skip).limit(limit).order_by(UserModel.created_at.desc())
        return list(self.session.exec(statement).all())

    def count(self) -> int:
        """Return the total count of registered users."""
        statement = select(func.count()).select_from(UserModel)
        count = self.session.exec(statement).one()
        return int(count)

    def save(self, user: UserModel) -> UserModel:
        """Persist a new or modified user to the database."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: UserModel) -> None:
        """Delete a user entity from the database."""
        self.session.delete(user)
        self.session.commit()
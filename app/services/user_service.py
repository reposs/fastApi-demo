from uuid import UUID, uuid4

from app.core.exceptions import (
    AuthenticationError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.core.models.user_model import UserModel
from app.core.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository


class UserService:
    """Service layer encapsulating all business logic for User operations."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def get_by_id(self, user_id: UUID) -> UserModel:
        """Retrieve a user by their UUID or raise EntityNotFoundError."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(entity_name="User", identifier=user_id)
        return user

    def get_by_email(self, email: str) -> UserModel | None:
        """Retrieve a user by email address."""
        return self.repository.get_by_email(email)

    def list_users(self, skip: int = 0, limit: int = 10) -> tuple[list[UserModel], int]:
        """Return a page of users along with the total count."""
        users = self.repository.list(skip=skip, limit=limit)
        total = self.repository.count()
        return users, total

    def create(self, data: UserCreate) -> UserModel:
        """Create a new user with duplicate email validation and password hashing."""
        email_str = str(data.email).strip().lower()
        if self.repository.exists_by_email(email_str):
            raise EntityAlreadyExistsError(
                entity_name="User",
                field="email",
                value=email_str,
                message="A user with this email already exists",
            )

        user = UserModel(
            id=uuid4(),
            firstname=data.firstname.strip(),
            lastname=data.lastname.strip() if data.lastname else None,
            email=email_str,
            disabled=data.disabled,
            password=hash_password(data.password),
        )
        return self.repository.save(user)

    # Alias for backwards compatibility
    create_user = create

    def update(self, user_id: UUID, data: UserUpdate) -> UserModel:
        """Update existing user properties."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(entity_name="User", identifier=user_id)

        values = data.model_dump(exclude_unset=True)

        if "email" in values and values["email"] is not None:
            new_email = str(values["email"]).strip().lower()
            if self.repository.exists_by_email(new_email, exclude_id=user_id):
                raise EntityAlreadyExistsError(
                    entity_name="User",
                    field="email",
                    value=new_email,
                    message="A user with this email already exists",
                )
            values["email"] = new_email

        if "password" in values and values["password"] is not None:
            values["password"] = hash_password(values["password"])
        elif "password" in values and values["password"] is None:
            # Do not overwrite password with None
            del values["password"]

        if "firstname" in values and values["firstname"] is not None:
            values["firstname"] = values["firstname"].strip()

        if "lastname" in values and values["lastname"] is not None:
            values["lastname"] = values["lastname"].strip()

        for field, value in values.items():
            setattr(user, field, value)

        return self.repository.save(user)

    # Alias for backwards compatibility
    update_user = update

    def delete(self, user_id: UUID) -> None:
        """Delete user by UUID or raise EntityNotFoundError."""
        user = self.get_by_id(user_id)
        self.repository.delete(user)

    # Alias for backwards compatibility
    delete_user = delete

    def authenticate(self, email: str, password: str) -> UserModel:
        """Authenticate user credentials and return the user if active."""
        user = self.repository.get_by_email(email)
        if not user or user.disabled or not verify_password(password, user.password):
            raise AuthenticationError(message="Incorrect email or password")
        return user
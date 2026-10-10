import datetime
import unittest
from uuid import UUID, uuid4

from app.core.exceptions import (
    AuthenticationError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.core.models.user_model import UserModel
from app.core.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import hash_password
from app.services.user_service import UserService


class InMemoryUserRepository:
    """In-memory stub of UserRepository for fast and isolated unit tests."""

    def __init__(self):
        self.users: dict[UUID, UserModel] = {}

    def get_by_id(self, user_id: UUID) -> UserModel | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> UserModel | None:
        norm = email.strip().lower()
        for u in self.users.values():
            if u.email.lower() == norm:
                return u
        return None

    def exists_by_email(self, email: str, exclude_id: UUID | None = None) -> bool:
        norm = email.strip().lower()
        for u in self.users.values():
            if u.email.lower() == norm and (exclude_id is None or u.id != exclude_id):
                return True
        return False

    def list(self, skip: int = 0, limit: int = 10) -> list[UserModel]:
        all_users = list(self.users.values())
        return all_users[skip : skip + limit]

    def count(self) -> int:
        return len(self.users)

    def save(self, user: UserModel) -> UserModel:
        self.users[user.id] = user
        return user

    def delete(self, user: UserModel) -> None:
        self.users.pop(user.id, None)


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryUserRepository()
        self.service = UserService(self.repo)

    def test_create_user_success(self):
        dto = UserCreate(
            firstname="John",
            lastname="Doe",
            email="john@example.com",
            password="StrongPass123!",
        )
        user = self.service.create_user(dto)
        self.assertEqual(user.firstname, "John")
        self.assertEqual(user.email, "john@example.com")
        self.assertNotEqual(user.password, "StrongPass123!")  # hashed
        self.assertEqual(self.repo.count(), 1)

    def test_create_user_duplicate_email_raises_error(self):
        dto = UserCreate(
            firstname="John",
            lastname="Doe",
            email="john@example.com",
            password="StrongPass123!",
        )
        self.service.create_user(dto)

        # Duplicate email attempt
        duplicate_dto = UserCreate(
            firstname="Jane",
            lastname="Doe",
            email="JOHN@example.com",  # case insensitive
            password="OtherPass123!",
        )
        with self.assertRaises(EntityAlreadyExistsError):
            self.service.create_user(duplicate_dto)

    def test_get_by_id_not_found(self):
        random_id = uuid4()
        with self.assertRaises(EntityNotFoundError):
            self.service.get_by_id(random_id)

    def test_update_user_success(self):
        dto = UserCreate(
            firstname="John",
            lastname="Doe",
            email="john@example.com",
            password="StrongPass123!",
        )
        user = self.service.create_user(dto)

        update_dto = UserUpdate(firstname="Johnny")
        updated = self.service.update_user(user.id, update_dto)
        self.assertEqual(updated.firstname, "Johnny")
        self.assertEqual(updated.email, "john@example.com")

    def test_update_user_duplicate_email(self):
        user1 = self.service.create_user(
            UserCreate(firstname="User1", email="user1@example.com", password="Pass123!user")
        )
        user2 = self.service.create_user(
            UserCreate(firstname="User2", email="user2@example.com", password="Pass123!user")
        )

        with self.assertRaises(EntityAlreadyExistsError):
            self.service.update_user(user2.id, UserUpdate(email="user1@example.com"))

    def test_delete_user(self):
        user = self.service.create_user(
            UserCreate(firstname="User", email="del@example.com", password="Pass123!user")
        )
        self.assertEqual(self.repo.count(), 1)

        self.service.delete_user(user.id)
        self.assertEqual(self.repo.count(), 0)

        with self.assertRaises(EntityNotFoundError):
            self.service.delete_user(user.id)

    def test_authenticate(self):
        raw_password = "Password123!"
        user = self.service.create_user(
            UserCreate(firstname="Auth", email="auth@example.com", password=raw_password)
        )

        # Successful auth
        authenticated = self.service.authenticate("auth@example.com", raw_password)
        self.assertEqual(authenticated.id, user.id)

        # Wrong password
        with self.assertRaises(AuthenticationError):
            self.service.authenticate("auth@example.com", "WrongPassword1!")

        # Non-existent email
        with self.assertRaises(AuthenticationError):
            self.service.authenticate("nonexistent@example.com", raw_password)

        # Disabled user
        user.disabled = True
        self.repo.save(user)
        with self.assertRaises(AuthenticationError):
            self.service.authenticate("auth@example.com", raw_password)


if __name__ == "__main__":
    unittest.main()

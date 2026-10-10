import datetime
import unittest
from uuid import uuid4

from pydantic import ValidationError

from app.core.schemas.token_schema import LoginRequest, Token
from app.core.schemas.user_schema import UserCreate, UserListResponse, UserResponse, UserUpdate


class TestSchemas(unittest.TestCase):
    def test_user_create_valid(self):
        user = UserCreate(
            firstname="Alice",
            lastname="Smith",
            email="alice@example.com",
            password="StrongPassword1!",
        )
        self.assertEqual(user.firstname, "Alice")
        self.assertEqual(user.lastname, "Smith")
        self.assertEqual(user.email, "alice@example.com")
        self.assertFalse(user.disabled)

    def test_user_create_invalid_password(self):
        with self.assertRaises(ValidationError):
            UserCreate(
                firstname="Alice",
                email="alice@example.com",
                password="weak",
            )

    def test_user_update_with_none_password(self):
        """Ensure password=None is valid and does not raise ValidationError."""
        update_data = UserUpdate(firstname="Bob", password=None)
        self.assertEqual(update_data.firstname, "Bob")
        self.assertIsNone(update_data.password)

    def test_user_update_empty(self):
        update_data = UserUpdate()
        self.assertIsNone(update_data.firstname)
        self.assertIsNone(update_data.password)

    def test_user_response_serialization(self):
        now = datetime.datetime.now(datetime.UTC)
        user_id = uuid4()
        response = UserResponse(
            id=user_id,
            created_at=now,
            firstname="Carlos",
            lastname="Santana",
            email="carlos@example.com",
            disabled=False,
        )
        data = response.model_dump()
        self.assertEqual(data["id"], user_id)
        self.assertEqual(data["firstname"], "Carlos")
        self.assertNotIn("password", data)

    def test_token_schema(self):
        token = Token(access_token="fake.jwt.token", token_type="bearer", expires_in=1800)
        self.assertEqual(token.token_type, "bearer")
        self.assertEqual(token.expires_in, 1800)

    def test_login_request_schema(self):
        req = LoginRequest(email="test@example.com", password="SecretPassword1!")
        self.assertEqual(req.email, "test@example.com")


if __name__ == "__main__":
    unittest.main()

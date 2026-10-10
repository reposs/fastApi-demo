import unittest

from app.core.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class TestExceptions(unittest.TestCase):
    def test_app_exception_defaults(self):
        exc = AppException("Generic error")
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.error_code, "INTERNAL_SERVER_ERROR")
        self.assertEqual(exc.message, "Generic error")

    def test_entity_not_found_error(self):
        exc = EntityNotFoundError(entity_name="User", identifier="1234")
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.error_code, "NOT_FOUND")
        self.assertIn("User", exc.message)
        self.assertEqual(exc.details["entity"], "User")
        self.assertEqual(exc.details["identifier"], "1234")

    def test_entity_already_exists_error(self):
        exc = EntityAlreadyExistsError(entity_name="User", field="email", value="test@example.com")
        self.assertEqual(exc.status_code, 409)
        self.assertEqual(exc.error_code, "CONFLICT")
        # Verify it is also a ValueError for backwards compatibility!
        self.assertIsInstance(exc, ValueError)

    def test_auth_errors(self):
        auth_err = AuthenticationError("Bad credentials")
        self.assertEqual(auth_err.status_code, 401)
        self.assertEqual(auth_err.error_code, "UNAUTHORIZED")

        forbidden_err = AuthorizationError("Forbidden")
        self.assertEqual(forbidden_err.status_code, 403)
        self.assertEqual(forbidden_err.error_code, "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()

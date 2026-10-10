import unittest

from app.core.validators.password_validator import validate_password


class TestPasswordValidator(unittest.TestCase):
    def test_valid_password(self):
        valid = "SecurePass123!"
        self.assertEqual(validate_password(valid), valid)

    def test_password_none_graceful_handling(self):
        """Verify that None returns None without raising TypeError."""
        self.assertIsNone(validate_password(None))

    def test_missing_lowercase_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            validate_password("SECURE123!@#")
        self.assertIn("lowercase", str(ctx.exception))

    def test_missing_uppercase_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            validate_password("secure123!@#")
        self.assertIn("uppercase", str(ctx.exception))

    def test_missing_digit_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            validate_password("SecurePass!@#")
        self.assertIn("number", str(ctx.exception))

    def test_missing_special_char_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            validate_password("SecurePass1234")
        self.assertIn("special character", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

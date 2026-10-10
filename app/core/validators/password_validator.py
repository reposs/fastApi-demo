def validate_password(password: str | None) -> str | None:
    """Validate password complexity.

    Requires:
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one digit
    - At least one special (non-alphanumeric) character

    Accepts None to support optional updates in partial schemas.
    """
    if password is None:
        return None

    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one number")

    if not any(not c.isalnum() for c in password):
        raise ValueError("Password must contain at least one special character")

    return password
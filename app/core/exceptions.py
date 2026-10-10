from typing import Any


class AppException(Exception):
    """Base exception for application domain errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundError(AppException):
    """Raised when an entity is not found."""

    def __init__(
        self,
        entity_name: str,
        identifier: Any,
        message: str | None = None,
    ) -> None:
        msg = message or f"{entity_name} with identifier '{identifier}' was not found"
        super().__init__(
            message=msg,
            status_code=404,
            error_code="NOT_FOUND",
            details={"entity": entity_name, "identifier": str(identifier)},
        )


class EntityAlreadyExistsError(AppException, ValueError):
    """Raised when attempting to create a duplicate entity."""

    def __init__(
        self,
        entity_name: str,
        field: str,
        value: Any,
        message: str | None = None,
    ) -> None:
        msg = message or f"{entity_name} with {field} '{value}' already exists"
        super().__init__(
            message=msg,
            status_code=409,
            error_code="CONFLICT",
            details={"entity": entity_name, "field": field, "value": str(value)},
        )


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Invalid authentication credentials",
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )


class AuthorizationError(AppException):
    """Raised when access is forbidden."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )


class BadRequestError(AppException):
    """Raised when request payload or parameters are invalid."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details,
        )

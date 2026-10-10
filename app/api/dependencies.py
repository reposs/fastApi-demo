from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session

from app.core.db.database import get_db
from app.core.models.user_model import UserModel
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

# OAuth2 scheme for Swagger UI integration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(session: Annotated[Session, Depends(get_db)]) -> UserRepository:
    """Dependency that provides an instance of UserRepository."""
    return UserRepository(session)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Dependency that provides an instance of UserService with injected repository."""
    return UserService(repository)


def get_current_user(
    oauth2_token: Annotated[str | None, Depends(oauth2_scheme)],
    bearer_creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserModel:
    """Validate access token from either OAuth2 scheme or HTTP Bearer header and return UserModel."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract raw token from either source
    raw_token = oauth2_token
    if not raw_token and bearer_creds and bearer_creds.scheme.lower() == "bearer":
        raw_token = bearer_creds.credentials

    if not raw_token:
        raise credentials_error

    try:
        payload = decode_access_token(raw_token)
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise credentials_error
    except JWTError as error:
        raise credentials_error from error

    user = user_service.get_by_email(email)
    if not user:
        raise credentials_error

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


# Clean type annotations for route injection
DatabaseSession = Annotated[Session, Depends(get_db)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]

__all__ = [
    "CurrentUser",
    "DatabaseSession",
    "UserRepositoryDep",
    "UserServiceDep",
    "get_current_user",
    "get_user_repository",
    "get_user_service",
]
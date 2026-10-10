from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import CurrentUser, UserServiceDep
from app.core.config import settings
from app.core.schemas.token_schema import LoginRequest, Token
from app.core.schemas.user_schema import UserCreate, UserResponse
from app.core.security import create_access_token

router = APIRouter(tags=["auth"])


class AuthFormData:
    """Flexible form data parser supporting both OAuth2 (username/password) and direct email/password."""

    def __init__(
        self,
        username: str | None = Form(default=None, description="Username or email for OAuth2 standard"),
        email: str | None = Form(default=None, description="Email address"),
        password: str = Form(..., description="Password"),
    ) -> None:
        self.identifier = email or username or ""
        self.password = password


@router.post(
    "/token",
    response_model=Token,
    summary="Login to obtain JWT access token (Form Data / OAuth2)",
    description="OAuth2 compatible token login endpoint. Accepts either 'username' (OAuth2 standard) or 'email' form field.",
)
def login_for_access_token(
    form_data: Annotated[AuthFormData, Depends()],
    user_service: UserServiceDep,
) -> Token:
    """Authenticate credentials and generate access token."""
    if not form_data.identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username is required",
        )

    user = user_service.authenticate(
        email=form_data.identifier,
        password=form_data.password,
    )

    access_token = create_access_token(subject=user.email)
    expires_in = settings.JWT_EXPIRE_MINUTES * 60

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Login with JSON body",
    description="JSON-based login endpoint for web and mobile clients.",
)
def login_json(
    credentials: LoginRequest,
    user_service: UserServiceDep,
) -> Token:
    """Authenticate via JSON payload."""
    user = user_service.authenticate(
        email=credentials.email,
        password=credentials.password,
    )

    access_token = create_access_token(subject=user.email)
    expires_in = settings.JWT_EXPIRE_MINUTES * 60

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Public user registration",
    description="Allows new users to create an account without requiring authentication.",
)
def register(
    data: UserCreate,
    user_service: UserServiceDep,
) -> UserResponse:
    """Register a new user account."""
    return user_service.create_user(data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
    description="Returns the profile details of the currently authenticated user.",
)
def get_me(
    current_user: CurrentUser,
) -> UserResponse:
    """Return profile of authenticated user."""
    return current_user
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import CurrentUser, UserServiceDep
from app.core.schemas.user_schema import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Registers a new user in the system. Requires authentication.",
)
def user_create(
    data: UserCreate,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> UserResponse:
    """Create a new user."""
    return user_service.create_user(data)


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users",
    description="Retrieve a paginated list of users. Total count is returned in X-Total-Count header.",
)
def user_list(
    response: Response,
    current_user: CurrentUser,
    user_service: UserServiceDep,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Max records to return"),
) -> list[UserResponse]:
    """List users with pagination."""
    users, total = user_service.list_users(skip=skip, limit=limit)
    response.headers["X-Total-Count"] = str(total)
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Fetch a single user profile by their UUID.",
)
def user_get(
    user_id: UUID,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> UserResponse:
    """Get user by unique ID."""
    return user_service.get_by_id(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user details",
    description="Update user information by UUID.",
)
def user_update(
    user_id: UUID,
    data: UserUpdate,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> UserResponse:
    """Update user attributes."""
    return user_service.update_user(user_id, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Remove a user from the system by their UUID.",
)
def user_delete(
    user_id: UUID,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> None:
    """Delete user by ID."""
    user_service.delete_user(user_id)
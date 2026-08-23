from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.dependencies import CurrentUser
from app.core.db.database import get_db
from app.core.schemas.user_schema import UserIn, UserOut, UserUpdate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def user_create(
    data: UserIn,
    current_user: CurrentUser,
    session: Session = Depends(get_db),
):
    try:
        return UserService(UserRepository(session)).create(data)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("", response_model=list[UserOut])
def user_list(
    current_user: CurrentUser,
    session: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    return UserRepository(session).list(skip, limit)


@router.get("/{user_id}", response_model=UserOut)
def user_get(
    user_id: UUID,
    current_user: CurrentUser,
    session: Session = Depends(get_db),
):
    user = UserRepository(session).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def user_update(
    user_id: UUID,
    data: UserUpdate,
    current_user: CurrentUser,
    session: Session = Depends(get_db),
):
    try:
        user = UserService(UserRepository(session)).update(user_id, data)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def user_delete(
    user_id: UUID,
    current_user: CurrentUser,
    session: Session = Depends(get_db),
):
    repository = UserRepository(session)
    user = repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    repository.delete(user)
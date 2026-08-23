from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlmodel import Session

from app.core.db.database import get_db
from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository

router = APIRouter(tags=["auth"])


class EmailPasswordForm:
    def __init__(
        self,
        email: str = Form(default="johndoe@example.com"),
        password: str = Form(default="fakehashedsecret"),
    ):
        self.email = email
        self.password = password


@router.post("/token")
def login(
    form_data: Annotated[EmailPasswordForm, Depends()],
    session: Annotated[Session, Depends(get_db)],
):
    user = UserRepository(session).get_by_email(form_data.email)
    if not user or user.disabled or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.email), "token_type": "bearer"}
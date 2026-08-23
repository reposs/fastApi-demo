from uuid import UUID

from sqlmodel import Session, select

from app.core.models.user_model import UserModel


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: UUID) -> UserModel | None:
        return self.session.get(UserModel, user_id)

    def get_by_email(self, email: str) -> UserModel | None:
        return self.session.exec(select(UserModel).where(UserModel.email == email)).first()

    def list(self, skip: int, limit: int) -> list[UserModel]:
        return list(self.session.exec(select(UserModel).offset(skip).limit(limit)))

    def save(self, user: UserModel) -> UserModel:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: UserModel) -> None:
        self.session.delete(user)
        self.session.commit()
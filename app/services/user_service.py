from uuid import UUID, uuid4

from app.core.schemas.user_schema import UserCreate, UserUpdate
from app.core.models.user_model import UserModel
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create(self, data: UserCreate) -> UserModel:
        if self.repository.get_by_email(str(data.email)):
            raise ValueError("A user with this email already exists")
        user = UserModel(
            id=uuid4(),
            firstname=data.firstname,
            lastname=data.lastname,
            email=str(data.email),
            disabled=data.disabled,
            password=hash_password(data.password),
        )
        return self.repository.save(user)

    def update(self, user_id: UUID, data: UserUpdate) -> UserModel | None:
        user = self.repository.get_by_id(user_id)
        if not user:
            return None
        values = data.model_dump(exclude_unset=True)
        if "email" in values:
            existing = self.repository.get_by_email(str(values["email"]))
            if existing and existing.id != user_id:
                raise ValueError("A user with this email already exists")
            values["email"] = str(values["email"])
        if "password" in values:
            values["password"] = hash_password(values["password"])
        for field, value in values.items():
            setattr(user, field, value)
        return self.repository.save(user)
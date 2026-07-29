from sqlalchemy.orm import Session

from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.user import UserCreate
from backend.core.security import hash_password, verify_password


class UserService:

    @staticmethod
    def register_user(
        db: Session,
        user_data: UserCreate,
    ):
        if UserRepository.get_by_email(
            db,
            user_data.email,
        ):
            raise ValueError("Email already exists")

        if UserRepository.get_by_username(
            db,
            user_data.username,
        ):
            raise ValueError("Username already exists")

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(
                user_data.password
            ),
        )

        return UserRepository.create(
            db,
            user,
        )

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
    ):
        user = UserRepository.get_by_email(
            db,
            email,
        )

        if not user:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        if not user.is_active:
            return None

        return user
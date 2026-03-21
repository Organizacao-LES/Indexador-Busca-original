from sqlalchemy.orm import Session
from app.exceptions.user_exceptions import (
    UserConflictException,
    UserNotFoundException,
)

from app.domain.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import hash_password


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, db: Session, user_create: UserCreate) -> User:
        """
        Creates a new user.

        Args:
            db: The database session.
            user_create: The user creation data.

        Returns:
            The created user.

        Raises:
            UserConflictException: If a user with the same login or email already exists.
        """
        if self.user_repository.get_by_login(db, user_create.login):
            raise UserConflictException(detail="Login already in use.")

        if self.user_repository.get_by_email(db, user_create.email):
            raise UserConflictException(detail="Email already in use.")

        hashed_password = hash_password(user_create.senha)
        db_user = User(
            **user_create.model_dump(exclude={"senha"}),
            senha_hash=hashed_password
        )
        return self.user_repository.create(db, db_user)

    def get_user_by_id(self, db: Session, user_id: int) -> User:
        """
        Retrieves a user by their ID.

        Args:
            db: The database session.
            user_id: The ID of the user to retrieve.

        Returns:
            The user.

        Raises:
            UserNotFoundException: If the user is not found.
        """
        user = self.user_repository.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundException(detail="User not found.")
        return user

    def get_all_users(self, db: Session, skip: int, limit: int) -> list[User]:
        """
        Retrieves a list of all users.

        Args:
            db: The database session.
            skip: The number of users to skip.
            limit: The maximum number of users to return.

        Returns:
            A list of users.
        """
        return self.user_repository.get_all(db, skip, limit)

    def update_user(
        self, db: Session, user_id: int, user_update: UserUpdate
    ) -> User:
        """
        Updates a user.

        Args:
            db: The database session.
            user_id: The ID of the user to update.
            user_update: The user update data.

        Returns:
            The updated user.

        Raises:
            UserConflictException: If the new login/email is already in use.
        """
        user = self.get_user_by_id(db, user_id)

        update_data = user_update.model_dump(exclude_unset=True)

        if "login" in update_data and update_data["login"] != user.login:
            if self.user_repository.get_by_login(db, update_data["login"]):
                raise UserConflictException(detail="Login already in use.")

        if "email" in update_data and update_data["email"] != user.email:
            if self.user_repository.get_by_email(db, update_data["email"]):
                raise UserConflictException(detail="Email already in use.")

        if "senha" in update_data:
            update_data["senha_hash"] = hash_password(update_data.pop("senha"))

        return self.user_repository.update(db, user, UserUpdate(**update_data))

    def delete_user(self, db: Session, user_id: int) -> User:
        """
        Deletes a user by marking them as inactive.

        Args:
            db: The database session.
            user_id: The ID of the user to delete.

        Returns:
            The deactivated user.
        """
        user = self.get_user_by_id(db, user_id)
        user_update = UserUpdate(ativo=False)
        return self.user_repository.update(db, user, user_update)


user_service = UserService(UserRepository())

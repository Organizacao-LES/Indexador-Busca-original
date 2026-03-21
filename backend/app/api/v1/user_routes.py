from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domain.user import User
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure the current user is an administrator.
    """
    if current_user.perfil != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted.",
        )
    return current_user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_admin_user)],
)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user. (Admin only)
    """
    return user_service.create_user(db, user_create)


@router.get("/", response_model=List[UserResponse], dependencies=[Depends(get_admin_user)])
def read_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve all users. (Admin only)
    """
    return user_service.get_all_users(db, skip, limit)


@router.get(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(get_admin_user)]
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single user by ID. (Admin only)
    """
    return user_service.get_user_by_id(db, user_id)


@router.put(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(get_admin_user)]
)
def update_user(
    user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)
):
    """
    Update a user. (Admin only)
    """
    return user_service.update_user(db, user_id, user_update)


@router.delete(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(get_admin_user)]
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deactivate a user. (Admin only)
    """
    return user_service.delete_user(db, user_id)

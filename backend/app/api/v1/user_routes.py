from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.domain.user_role import UserRole
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user_create)


@router.get(
    "/",
    response_model=List[UserResponse],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    print(f"Admin user is retrieving users with skip={skip} and limit={limit}.")
    """
    Retrieve all users. (Admin only)
    """
    return user_service.get_all_users(db, skip, limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(db, user_id, user_update)


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.delete_user(db, user_id)

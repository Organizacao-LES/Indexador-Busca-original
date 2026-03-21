import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.domain.user import User


@pytest.fixture
def user_repository_mock():
    return MagicMock(spec=UserRepository)


@pytest.fixture
def user_service(user_repository_mock):
    return UserService(user_repository_mock)


@pytest.fixture
def db_session_mock():
    return MagicMock(spec=Session)


def test_create_user_success(
    user_service: UserService, user_repository_mock, db_session_mock
):
    # Arrange
    user_create = UserCreate(
        nome="Test User",
        login="testuser",
        email="test@example.com",
        senha="password123",
        perfil="USER",
    )
    user_repository_mock.get_by_login.return_value = None
    user_repository_mock.get_by_email.return_value = None
    user_repository_mock.create.return_value = User(
        cod_usuario=1,
        nome=user_create.nome,
        login=user_create.login,
        email=user_create.email,
        perfil=user_create.perfil,
    )

    # Act
    with patch("app.core.security.get_password_hash", return_value="hashed_password"):
        created_user = user_service.create_user(db_session_mock, user_create)

    # Assert
    assert created_user is not None
    assert created_user.login == user_create.login
    user_repository_mock.create.assert_called_once()


def test_create_user_login_conflict(
    user_service: UserService, user_repository_mock, db_session_mock
):
    # Arrange
    user_create = UserCreate(
        nome="Test User",
        login="existinguser",
        email="test@example.com",
        senha="password123",
        perfil="USER",
    )
    user_repository_mock.get_by_login.return_value = User(login="existinguser")

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        user_service.create_user(db_session_mock, user_create)
    assert excinfo.value.status_code == 409
    assert "Login already in use" in excinfo.value.detail


def test_get_user_by_id_success(
    user_service: UserService, user_repository_mock, db_session_mock
):
    # Arrange
    user_id = 1
    expected_user = User(cod_usuario=user_id, nome="Found User", login="found")
    user_repository_mock.get_by_id.return_value = expected_user

    # Act
    found_user = user_service.get_user_by_id(db_session_mock, user_id)

    # Assert
    assert found_user is not None
    assert found_user.cod_usuario == user_id
    user_repository_mock.get_by_id.assert_called_with(db_session_mock, user_id)


def test_get_user_by_id_not_found(
    user_service: UserService, user_repository_mock, db_session_mock
):
    # Arrange
    user_id = 999
    user_repository_mock.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        user_service.get_user_by_id(db_session_mock, user_id)
    assert excinfo.value.status_code == 404
    assert "User not found" in excinfo.value.detail

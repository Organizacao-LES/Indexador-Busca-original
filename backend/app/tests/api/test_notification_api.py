from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.main as main_module
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.domain.user import User
from app.domain.user_role import UserRole
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    db: Session = TestingSessionLocal()
    admin = User(
        nome="Administrador",
        login="admin",
        email="admin@ifes.edu.br",
        senha_hash=hash_password("admin123"),
        perfil=UserRole.ADMIN.value,
        ativo=True,
    )
    db.add(admin)
    db.commit()
    db.close()

    original_engine = main_module.engine
    main_module.engine = engine

    def override_get_db() -> Generator[Session, None, None]:
        override_db = TestingSessionLocal()
        try:
            yield override_db
        finally:
            override_db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    main_module.engine = original_engine
    Base.metadata.drop_all(bind=engine)


def login(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ifes.edu.br", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()


def test_user_can_receive_and_read_notification(client: TestClient):
    session = login(client)
    headers = {"Authorization": f"Bearer {session['token']}"}

    create_response = client.post(
        "/api/v1/notifications",
        headers=headers,
        json={
            "userId": session["id"],
            "title": "Mensagem do sistema",
            "message": "O IFESDOC enviou uma nova mensagem.",
            "type": "info",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert len(created) == 1
    assert created[0]["title"] == "Mensagem do sistema"
    assert created[0]["read"] is False

    list_response = client.get("/api/v1/notifications", headers=headers)
    assert list_response.status_code == 200
    notifications = list_response.json()
    assert notifications[0]["message"] == "O IFESDOC enviou uma nova mensagem."

    count_response = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert count_response.status_code == 200
    assert count_response.json()["unread"] == 1

    read_response = client.patch(
        f"/api/v1/notifications/{created[0]['id']}/read",
        headers=headers,
    )
    assert read_response.status_code == 200
    assert read_response.json()["read"] is True

    count_after_read = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert count_after_read.json()["unread"] == 0

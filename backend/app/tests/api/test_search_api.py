from collections.abc import Generator
from pathlib import Path

import app.main as main_module
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.domain.user import User
from app.domain.user_role import UserRole
from app.main import app
from app.services.document_service import document_service


def _login(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ifes.edu.br", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


def _upload(client: TestClient, token: str, file_name: str, content: bytes, category: str):
    response = client.post(
        "/api/v1/ingestion/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (file_name, content, "text/plain")},
        data={"category": category},
    )
    assert response.status_code == 201


def _client_fixture(tmp_path: Path) -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = testing_session_local()
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
    original_storage_dir = document_service.storage_dir
    document_service.storage_dir = tmp_path / "documents"
    main_module.engine = engine

    def override_get_db() -> Generator[Session, None, None]:
        override_db = testing_session_local()
        try:
            yield override_db
        finally:
            override_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    main_module.engine = original_engine
    document_service.storage_dir = original_storage_dir
    Base.metadata.drop_all(bind=engine)


def test_search_returns_ranked_documents_and_recent_history(tmp_path: Path):
    for client in _client_fixture(tmp_path):
        token = _login(client)
        _upload(client, token, "resolucao.txt", b"A resolucao institucional do IFES trata de pesquisa aplicada.", "administrativo")
        _upload(client, token, "ata.txt", b"A ata de reuniao descreve pesquisa e extensao no IFES.", "academico")

        search_response = client.get(
            "/api/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": "pesquisa ifes", "limit": 10, "page": 1},
        )

        assert search_response.status_code == 200
        payload = search_response.json()
        assert payload["query"] == "pesquisa ifes"
        assert payload["total"] >= 2
        assert payload["items"][0]["relevance"] >= payload["items"][-1]["relevance"]
        assert payload["items"][0]["type"] == "TXT"

        history_response = client.get(
            "/api/v1/search/history",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert history_response.status_code == 200
        history_payload = history_response.json()
        assert history_payload[0]["term"] == "pesquisa ifes"

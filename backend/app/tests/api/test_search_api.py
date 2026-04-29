from contextlib import asynccontextmanager
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


def _upload_with_metadata(
    client: TestClient,
    token: str,
    file_name: str,
    content: bytes,
    *,
    category: str,
    author: str | None = None,
    document_type: str | None = None,
    document_date: str | None = None,
):
    data = {"category": category}
    if author:
        data["author"] = author
    if document_type:
        data["document_type"] = document_type
    if document_date:
        data["document_date"] = document_date
    response = client.post(
        "/api/v1/ingestion/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (file_name, content, "text/plain")},
        data=data,
    )
    assert response.status_code == 201
    return response.json()


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
    original_lifespan = app.router.lifespan_context
    document_service.storage_dir = tmp_path / "documents"
    main_module.engine = engine

    @asynccontextmanager
    async def no_op_lifespan(_: object):
        yield

    def override_get_db() -> Generator[Session, None, None]:
        override_db = testing_session_local()
        try:
            yield override_db
        finally:
            override_db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = no_op_lifespan
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    app.router.lifespan_context = original_lifespan
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


def test_search_supports_author_filter_and_detailed_history(tmp_path: Path):
    for client in _client_fixture(tmp_path):
        token = _login(client)
        _upload_with_metadata(
            client,
            token,
            "relatorio-extensao.txt",
            b"Relatorio anual de extensao do IFES com projetos institucionais.",
            category="pesquisa",
            author="Maria de Souza",
            document_type="Relatorio",
            document_date="2026-04-10",
        )
        _upload_with_metadata(
            client,
            token,
            "relatorio-ensino.txt",
            b"Relatorio anual de extensao do IFES com projetos institucionais.",
            category="academico",
            author="Joao Pereira",
            document_type="Relatorio",
            document_date="2026-04-12",
        )

        search_response = client.get(
            "/api/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "q": "relatorio extensao ifes",
                "author": "Maria de Souza",
                "category": "pesquisa",
                "documentType": "Relatorio",
                "dateFrom": "2026-04-01",
                "dateTo": "2026-04-30",
            },
        )

        assert search_response.status_code == 200
        payload = search_response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["author"] == "Maria de Souza"
        assert payload["items"][0]["category"] == "pesquisa"

        history_response = client.get(
            "/api/v1/search/history/entries",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 10, "page": 1},
        )

        assert history_response.status_code == 200
        history_payload = history_response.json()
        assert history_payload["total"] == 1
        assert history_payload["items"][0]["query"] == "relatorio extensao ifes"
        assert history_payload["items"][0]["resultCount"] == 1
        assert history_payload["items"][0]["user"] == "admin@ifes.edu.br"
        assert history_payload["items"][0]["filters"]["author"] == "Maria de Souza"
        assert history_payload["items"][0]["filters"]["category"] == "pesquisa"
        assert history_payload["items"][0]["filters"]["documentType"] == "Relatorio"
        assert history_payload["items"][0]["filters"]["dateFrom"] == "2026-04-01"
        assert history_payload["items"][0]["filters"]["dateTo"] == "2026-04-30"

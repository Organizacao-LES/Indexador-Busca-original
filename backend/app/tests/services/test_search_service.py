from datetime import date
from io import BytesIO

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.datastructures import UploadFile

from app.core.database import Base
from app.domain.user import User
from app.domain.user_role import UserRole
from app.services.document_service import document_service
from app.services.search_service import search_service


def test_search_service_applies_author_filter_and_records_history(tmp_path):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_local()
    original_storage_dir = document_service.storage_dir
    document_service.storage_dir = tmp_path / "documents"

    try:
        user = User(
            nome="Administrador",
            login="admin",
            email="admin@ifes.edu.br",
            senha_hash="hash",
            perfil=UserRole.ADMIN.value,
            ativo=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        uploads = [
            (
                "relatorio-extensao.txt",
                "Maria de Souza",
                "pesquisa",
                date(2026, 4, 10),
            ),
            (
                "relatorio-ensino.txt",
                "Joao Pereira",
                "academico",
                date(2026, 4, 12),
            ),
        ]
        for file_name, author, category, document_date in uploads:
            upload = UploadFile(
                filename=file_name,
                file=BytesIO(
                    b"Relatorio anual de extensao do IFES com projetos institucionais."
                ),
            )
            upload.headers = {"content-type": "text/plain"}
            document_service.upload_document(
                db,
                file=upload,
                category=category,
                uploaded_by=user,
                document_date=document_date,
                author=author,
                document_type="Relatorio",
            )

        result = search_service.search(
            db,
            query="relatorio extensao ifes",
            user_id=user.cod_usuario,
            category="pesquisa",
            document_type="Relatorio",
            author="Maria de Souza",
            date_from="2026-04-01",
            date_to="2026-04-30",
            limit=10,
            page=1,
        )

        assert result["total"] == 1
        assert result["responseTimeMs"] >= 0
        assert result["items"][0]["author"] == "Maria de Souza"
        assert result["items"][0]["category"] == "pesquisa"

        history = search_service.list_search_history(
            db,
            current_user=user,
            limit=10,
            page=1,
        )

        assert history["total"] == 1
        assert history["items"][0]["query"] == "relatorio extensao ifes"
        assert history["items"][0]["user"] == "admin@ifes.edu.br"
        assert history["items"][0]["resultCount"] == 1
        assert history["items"][0]["responseTimeMs"] >= 0
        assert history["items"][0]["filters"]["author"] == "Maria de Souza"
        assert history["items"][0]["filters"]["category"] == "pesquisa"
        assert history["items"][0]["filters"]["documentType"] == "Relatorio"
        assert history["items"][0]["filters"]["dateFrom"] == "2026-04-01"
        assert history["items"][0]["filters"]["dateTo"] == "2026-04-30"
    finally:
        document_service.storage_dir = original_storage_dir
        db.close()
        Base.metadata.drop_all(bind=engine)

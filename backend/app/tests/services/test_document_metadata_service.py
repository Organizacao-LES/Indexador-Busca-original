from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.main  # noqa: F401
from app.core.database import Base
from app.domain.document import Document
from app.domain.document_category import DocumentCategory
from app.domain.document_history import DocumentHistory
from app.domain.document_metadata import DocumentMetadata
from app.domain.user import User
from app.domain.user_role import UserRole
from app.repositories.document_repository import DocumentRepository
from app.services.index_service import index_service
from app.services.search_service import search_service


def test_document_metadata_is_retrieved_and_indexed(tmp_path):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_local()

    try:
        file_path = tmp_path / "edital.txt"
        file_path.write_text("Conteúdo institucional sobre bolsas.", encoding="utf-8")

        user = User(
            nome="Administrador",
            login="admin",
            email="admin@ifes.edu.br",
            senha_hash="hash",
            perfil=UserRole.ADMIN.value,
            ativo=True,
        )
        category = DocumentCategory(nome_categoria="pesquisa")
        db.add_all([user, category])
        db.flush()

        document = Document(
            cod_categoria=category.cod_categoria,
            titulo="Edital de Bolsas",
            tipo="TXT",
            data_publicacao=datetime(2026, 3, 24),
            ativo=True,
            cod_usuario_criador=user.cod_usuario,
        )
        db.add(document)
        db.flush()

        db.add(
            DocumentMetadata(
                cod_documento=document.cod_documento,
                autor="Maria Silva",
                tipo_documento="Edital",
                nome_arquivo_original="edital_bolsas.txt",
                mime_type="text/plain",
                tamanho_bytes=file_path.stat().st_size,
                hash_arquivo="a" * 64,
            )
        )
        history = DocumentHistory(
            cod_documento=document.cod_documento,
            cod_usuario=user.cod_usuario,
            numero_versao=1,
            caminho_arquivo=str(file_path),
            texto_extraido="Conteúdo institucional sobre bolsas.",
            texto_processado="Conteúdo institucional sobre bolsas.",
            versao_ativa=True,
        )
        db.add(history)
        db.commit()

        payload = DocumentRepository.get_document_payload(db, document.cod_documento)
        assert payload["author_name"] == "Maria Silva"
        assert payload["file_name"] == "edital_bolsas.txt"
        assert payload["document_type"] == "Edital"
        assert payload["file_hash"] == "a" * 64

        index_service.process_document(
            db,
            document_id=document.cod_documento,
            triggered_by=user,
        )
        result = search_service.search(
            db,
            query="maria edital",
            user_id=user.cod_usuario,
            limit=10,
            page=1,
        )

        assert result["total"] == 1
        assert result["items"][0]["author"] == "Maria Silva"
        assert result["items"][0]["fileName"] == "edital_bolsas.txt"
        assert result["items"][0]["documentType"] == "Edital"
        assert result["items"][0]["size"]
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

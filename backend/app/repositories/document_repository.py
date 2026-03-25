from pathlib import Path

from sqlalchemy.orm import Session

from app.domain.document import Document
from app.domain.document_category import DocumentCategory
from app.domain.document_history import DocumentHistory
from app.domain.ingestion_history import IngestionHistory
from app.domain.ingestion_status import IngestionStatus
from app.domain.user import User


class DocumentRepository:
    @staticmethod
    def _active_history_query(db: Session):
        return (
            db.query(
                Document.cod_documento.label("id"),
                Document.titulo.label("title"),
                Document.tipo.label("type"),
                Document.data_publicacao.label("document_date"),
                Document.criado_em.label("uploaded_at"),
                DocumentCategory.nome_categoria.label("category"),
                DocumentHistory.numero_versao.label("version"),
                DocumentHistory.caminho_arquivo.label("file_path"),
                DocumentHistory.texto_extraido.label("content"),
                IngestionStatus.estado_ingestao.label("ingestion_status"),
                User.nome.label("author_name"),
            )
            .join(DocumentCategory, DocumentCategory.cod_categoria == Document.cod_categoria)
            .join(
                DocumentHistory,
                (DocumentHistory.cod_documento == Document.cod_documento)
                & (DocumentHistory.versao_ativa.is_(True)),
            )
            .join(User, User.cod_usuario == Document.cod_usuario_criador)
            .outerjoin(IngestionHistory, IngestionHistory.cod_documento == Document.cod_documento)
            .outerjoin(IngestionStatus, IngestionStatus.cod_status_ingestao == IngestionHistory.cod_status_ingestao)
        )

    @classmethod
    def get_document_payload(cls, db: Session, document_id: int) -> dict | None:
        row = (
            cls._active_history_query(db)
            .filter(Document.cod_documento == document_id)
            .order_by(IngestionHistory.criado_em.desc(), DocumentHistory.numero_versao.desc())
            .first()
        )
        return cls._row_to_payload(row) if row is not None else None

    @classmethod
    def list_ingestion_history(cls, db: Session, limit: int = 20) -> list[dict]:
        rows = (
            cls._active_history_query(db)
            .order_by(IngestionHistory.criado_em.desc(), Document.cod_documento.desc())
            .limit(limit)
            .all()
        )
        return [cls._row_to_payload(row) for row in rows]

    @classmethod
    def list_batch_files(cls, db: Session, limit: int = 10) -> list[dict]:
        rows = (
            cls._active_history_query(db)
            .order_by(IngestionHistory.criado_em.desc(), Document.cod_documento.desc())
            .limit(limit)
            .all()
        )
        return [cls._row_to_payload(row) for row in rows]

    @staticmethod
    def _row_to_payload(row) -> dict:
        file_name = Path(row.file_path).name
        return {
            "id": row.id,
            "title": row.title,
            "type": row.type,
            "category": row.category,
            "document_date": row.document_date,
            "uploaded_at": row.uploaded_at,
            "version": row.version,
            "file_path": row.file_path,
            "file_name": file_name,
            "content": row.content,
            "ingestion_status": row.ingestion_status or "concluido",
            "author_name": row.author_name,
            "size_bytes": Path(row.file_path).stat().st_size if Path(row.file_path).exists() else 0,
        }

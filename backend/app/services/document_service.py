from __future__ import annotations

import time
from datetime import date, datetime
from mimetypes import guess_type
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.adapters.document_adapter_registry import document_adapter_registry
from app.core.config import settings
from app.domain.document import Document
from app.domain.document_category import DocumentCategory
from app.domain.document_history import DocumentHistory
from app.domain.ingestion_history import IngestionHistory
from app.domain.ingestion_status import IngestionStatus
from app.domain.invalid_document import InvalidDocument
from app.domain.user import User
from app.exceptions.document_exceptions import (
    DocumentNotFoundException,
    DocumentValidationException,
)
from app.repositories.document_repository import DocumentRepository
from app.services.administrative_history_service import administrative_history_service
from app.services.index_service import index_service


class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
        self.adapter_registry = document_adapter_registry
        self.allowed_extensions = {
            extension.lower() for extension in settings.DOCUMENT_ALLOWED_EXTENSIONS
        }
        self.max_size_bytes = settings.DOCUMENT_MAX_FILE_SIZE_MB * 1024 * 1024
        self.storage_dir = Path(settings.DOCUMENT_UPLOAD_DIR)

    def upload_document(
        self,
        db: Session,
        *,
        file: UploadFile,
        category: str,
        uploaded_by: User,
        document_date: date | None = None,
    ) -> dict:
        started_at = time.perf_counter()
        filename = file.filename or ""
        normalized_category = category.strip()

        try:
            extension = self._extract_extension(filename)
            self._validate_extension(extension)
            adapter = self.adapter_registry.get(extension)
            if not normalized_category:
                raise DocumentValidationException("Informe uma categoria válida para o documento.")

            content = file.file.read()
            self._validate_size(content)
            adapter.validate_integrity(content)
            extracted_content = adapter.extract_text(content)
        except DocumentValidationException as exc:
            self._register_invalid_document(db, uploaded_by, filename, exc.detail)
            raise
        finally:
            file.file.close()

        storage_path = self._store_file(content, extension)
        title = Path(filename).stem or f"documento-{uuid4().hex[:8]}"
        category_row = self._get_or_create_category(db, normalized_category)
        processing_status = self._get_or_create_status(db, "processando")

        document = Document(
            cod_categoria=category_row.cod_categoria,
            titulo=title,
            tipo=extension.upper(),
            data_publicacao=self._coerce_document_datetime(document_date),
            ativo=True,
            cod_usuario_criador=uploaded_by.cod_usuario,
        )
        db.add(document)
        db.flush()

        history_document = DocumentHistory(
            cod_documento=document.cod_documento,
            cod_usuario=uploaded_by.cod_usuario,
            numero_versao=1,
            caminho_arquivo=str(storage_path),
            texto_extraido=extracted_content,
            texto_processado=extracted_content,
            versao_ativa=True,
        )
        db.add(history_document)
        db.flush()

        ingestion_history = IngestionHistory(
            cod_usuario=uploaded_by.cod_usuario,
            cod_documento=document.cod_documento,
            cod_status_ingestao=processing_status.cod_status_ingestao,
            tipo_ingestao="manual",
            mensagem_erro=None,
            tempo_processamento_ms=0,
        )
        db.add(ingestion_history)
        db.flush()

        try:
            index_service.process_document(
                db,
                document_id=document.cod_documento,
                triggered_by=uploaded_by,
                trigger_label="Ingestão",
            )
            completed_status = self._get_or_create_status(db, "concluido")
            ingestion_history.cod_status_ingestao = completed_status.cod_status_ingestao
            ingestion_history.mensagem_erro = None
        except Exception as exc:
            failed_status = self._get_or_create_status(db, "falha")
            ingestion_history.cod_status_ingestao = failed_status.cod_status_ingestao
            ingestion_history.mensagem_erro = str(exc)[:255]
            ingestion_history.tempo_processamento_ms = int(
                (time.perf_counter() - started_at) * 1000
            )
            db.commit()
            raise

        ingestion_history.tempo_processamento_ms = int((time.perf_counter() - started_at) * 1000)
        db.commit()
        administrative_history_service.log_action(
            db,
            actor=uploaded_by,
            description=f"Upload do documento {title}.{extension} concluído.",
            action_type="Ingestão",
            entity_type="documento",
            entity_id=document.cod_documento,
        )

        return self.get_document_payload(db, document.cod_documento)

    def upload_documents_batch(
        self,
        db: Session,
        *,
        files: list[UploadFile],
        category: str,
        uploaded_by: User,
        document_date: date | None = None,
    ) -> dict:
        items: list[dict] = []
        success_count = 0

        for file in files:
            try:
                payload = self.upload_document(
                    db,
                    file=file,
                    category=category,
                    uploaded_by=uploaded_by,
                    document_date=document_date,
                )
                items.append(
                    {
                        "fileName": payload["file_name"],
                        "status": "indexed",
                        "message": "Documento validado, extraído e armazenado com sucesso.",
                        "documentId": payload["id"],
                        "extractedCharacters": len(payload["content"] or ""),
                        "sizeLabel": self._format_size(payload["size_bytes"]),
                    }
                )
                success_count += 1
            except DocumentValidationException as exc:
                items.append(
                    {
                        "fileName": file.filename or "arquivo-sem-nome",
                        "status": "error",
                        "message": exc.detail,
                        "documentId": None,
                        "extractedCharacters": 0,
                        "sizeLabel": None,
                    }
                )
            except Exception:
                self._register_invalid_document(
                    db,
                    uploaded_by,
                    file.filename or "arquivo-sem-nome",
                    "Falha inesperada no processamento em lote.",
                )
                items.append(
                    {
                        "fileName": file.filename or "arquivo-sem-nome",
                        "status": "error",
                        "message": "Falha inesperada no processamento do arquivo.",
                        "documentId": None,
                        "extractedCharacters": 0,
                        "sizeLabel": None,
                    }
                )

        total_files = len(files)
        if total_files > 0:
            administrative_history_service.log_action(
                db,
                actor=uploaded_by,
                description=(
                    f"Upload em lote processado: {success_count} sucesso(s), "
                    f"{total_files - success_count} falha(s)."
                ),
                action_type="Ingestão",
                entity_type="lote_documento",
                entity_id=total_files,
            )
        return {
            "totalFiles": total_files,
            "successCount": success_count,
            "failureCount": total_files - success_count,
            "items": items,
        }

    def get_document_payload(self, db: Session, document_id: int) -> dict:
        payload = self.document_repository.get_document_payload(db, document_id)
        if payload is None:
            raise DocumentNotFoundException()
        return payload

    def get_document_file(self, db: Session, document_id: int) -> tuple[Path, str, str]:
        payload = self.get_document_payload(db, document_id)
        file_path = Path(payload["file_path"])
        if not file_path.exists() or not file_path.is_file():
            raise DocumentNotFoundException("Arquivo físico do documento não encontrado.")

        file_name = payload["file_name"]
        media_type = guess_type(file_name)[0] or self._get_mime_type(payload["type"].lower())
        return file_path, file_name, media_type

    def reindex_document(self, db: Session, *, document_id: int, triggered_by: User) -> dict:
        return index_service.reindex_document(
            db,
            document_id=document_id,
            triggered_by=triggered_by,
        )

    def list_ingestion_history(self, db: Session, limit: int = 20) -> list[dict]:
        return self.document_repository.list_ingestion_history(db, limit=limit)

    def list_batch_files(self, db: Session, limit: int = 10) -> list[dict]:
        return self.document_repository.list_batch_files(db, limit=limit)

    def to_upload_response(self, payload: dict) -> dict:
        document_date = payload["document_date"].date() if payload["document_date"] else None
        extracted_characters = len(payload["content"] or "")
        return {
            "id": payload["id"],
            "title": payload["title"],
            "fileName": payload["file_name"],
            "category": payload["category"],
            "type": payload["type"],
            "mimeType": self._get_mime_type(payload["type"].lower()),
            "sizeBytes": payload["size_bytes"],
            "sizeLabel": self._format_size(payload["size_bytes"]),
            "date": document_date,
            "uploadedAt": payload["uploaded_at"],
            "validated": True,
            "integrityOk": True,
            "hash": "",
            "extracted": True,
            "extractedCharacters": extracted_characters,
        }

    def to_history_response(self, payload: dict) -> dict:
        created_at = payload["uploaded_at"]
        extracted_characters = len(payload["content"] or "")
        details = (
            f"Validado ({payload['type']}) • Extraído {extracted_characters} caracteres • "
            f"Status {payload['ingestion_status']}"
        )
        return {
            "date": created_at.strftime("%Y-%m-%d %H:%M") if created_at else "",
            "file": payload["file_name"],
            "type": "Individual",
            "result": "Sucesso" if payload["ingestion_status"] == "concluido" else "Falha",
            "details": details,
        }

    def to_batch_response(self, payload: dict) -> dict:
        status = "indexed" if payload["ingestion_status"] == "concluido" else "error"
        return {
            "name": payload["file_name"],
            "size": self._format_size(payload["size_bytes"]),
            "status": status,
        }

    def to_details_response(self, payload: dict) -> dict:
        document_date = (
            payload["document_date"].isoformat()
            if payload["document_date"]
            else payload["uploaded_at"].isoformat()
        )
        extracted_characters = len(payload["content"] or "")
        return {
            "id": payload["id"],
            "title": payload["title"],
            "category": payload["category"],
            "type": payload["type"],
            "date": document_date,
            "author": payload["author_name"],
            "format": payload["type"],
            "pages": 1,
            "version": int(payload["version"]),
            "indexedAt": payload["uploaded_at"].isoformat(),
            "size": self._format_size(payload["size_bytes"]),
            "downloadUrl": f"/api/v1/documents/{payload['id']}/download",
            "content": payload["content"] or "Pré-visualização indisponível para este formato.",
            "extractedCharacters": extracted_characters,
        }

    def _get_or_create_category(self, db: Session, category_name: str) -> DocumentCategory:
        category = (
            db.query(DocumentCategory)
            .filter(DocumentCategory.nome_categoria.ilike(category_name))
            .first()
        )
        if category is not None:
            return category

        category = DocumentCategory(nome_categoria=category_name)
        db.add(category)
        db.flush()
        return category

    def _get_or_create_status(self, db: Session, status_name: str) -> IngestionStatus:
        status = (
            db.query(IngestionStatus)
            .filter(IngestionStatus.estado_ingestao == status_name)
            .first()
        )
        if status is not None:
            return status

        status = IngestionStatus(estado_ingestao=status_name)
        db.add(status)
        db.flush()
        return status

    def _register_invalid_document(
        self, db: Session, uploaded_by: User, filename: str, reason: str
    ) -> None:
        invalid_document = InvalidDocument(
            cod_usuario=uploaded_by.cod_usuario,
            nome_arquivo=filename or "arquivo-sem-nome",
            motivo_erro=reason[:255],
        )
        db.add(invalid_document)
        db.commit()

    def _coerce_document_datetime(self, value: date | None) -> datetime | None:
        if value is None:
            return None
        return datetime.combine(value, datetime.min.time())

    def _extract_extension(self, filename: str) -> str:
        extension = Path(filename).suffix.lower().lstrip(".")
        if not extension:
            raise DocumentValidationException("O arquivo enviado não possui extensão suportada.")
        return extension

    def _validate_extension(self, extension: str) -> None:
        if extension not in self.allowed_extensions:
            allowed = ", ".join(sorted(ext.upper() for ext in self.allowed_extensions))
            raise DocumentValidationException(
                f"Tipo de arquivo inválido. Formatos aceitos: {allowed}."
            )

    def _validate_size(self, content: bytes) -> None:
        if not content:
            raise DocumentValidationException("O arquivo enviado está vazio.")
        if len(content) > self.max_size_bytes:
            raise DocumentValidationException(
                f"Arquivo excede o tamanho máximo permitido de {settings.DOCUMENT_MAX_FILE_SIZE_MB} MB."
            )

    def _store_file(self, content: bytes, extension: str) -> Path:
        now = datetime.utcnow()
        target_dir = self.storage_dir / str(now.year) / f"{now.month:02d}" / extension.lower()
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{uuid4().hex}.{extension}"
        target.write_bytes(content)
        return target

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _get_mime_type(self, extension: str) -> str:
        return self.adapter_registry.get(extension).mime_type


document_service = DocumentService(DocumentRepository())

from __future__ import annotations

import json
import hashlib
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
from app.domain.document_metadata import DocumentMetadata
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


    def update_document(
        self,
        db: Session,
        *,
        document_id: int,
        file: UploadFile,
        updated_by: User,
    ):
        # Busca o documento ativo
        document = db.query(Document).filter(
        Document.cod_documento == document_id,
        Document.ativo.is_(True)
        ).first()

       # Se não existir, lança exceção
        if not document:
            raise DocumentNotFoundException()

        filename = file.filename or ""

        try:
               
                #  Extrai e valida extensão do arquivo
                extension = self._extract_extension(filename)
                self._validate_extension(extension)
                
                # Obtém adapter responsável pelo tipo de documento
                adapter = self.adapter_registry.get(extension)

                # Lê conteúdo do arquivo
                content = file.file.read()
                # Valida tamanho do arquivo
                self._validate_size(content)
                # Valida integridade do arquivo (ex: PDF válido)
                adapter.validate_integrity(content)

                # Extrai texto do documento
                extracted_content = adapter.extract_text(content)

        finally:
             #  Garante fechamento do arquivo
                file.file.close()
                
                
         #  desativa versão atual do documento
        current_version = db.query(DocumentHistory).filter(
            DocumentHistory.cod_documento == document_id,
            DocumentHistory.versao_ativa.is_(True)
        ).first()

        if current_version:
            current_version.versao_ativa = False
            
            
        # calcula nova versão
        # Busca última versão para calcular próxima
        last_version = db.query(DocumentHistory).filter(
            DocumentHistory.cod_documento == document_id
        ).order_by(DocumentHistory.numero_versao.desc()).first()

        # Incrementa número da versão
        new_version_number = (last_version.numero_versao if last_version else 0) + 1

        # Armazena novo arquivo no sistema
        storage_path = self._store_file(content, extension)

        # Cria nova versão no histórico
        new_history = DocumentHistory(
            cod_documento=document_id,
            cod_usuario=updated_by.cod_usuario,
            numero_versao=new_version_number,
            caminho_arquivo=str(storage_path),
            texto_extraido=extracted_content,
            texto_processado=extracted_content,
            versao_ativa=True,
        )

        db.add(new_history)
        db.flush()
        
    
        # Reindexa documento (atualiza índice invertido)
        index_service.reindex_document(
            db,
            document_id=document_id,
            triggered_by=updated_by
        )

        #  Persiste alterações
        db.commit()
        
        # Registra ação administrativa
        administrative_history_service.log_action(
        db,
        actor=updated_by,
        description=f"Documento {document.titulo} atualizado para versão {new_version_number}.",
        action_type="Atualização",
        entity_type="documento",
        entity_id=document_id,
        )

        # Retorna payload atualizado
        return self.get_document_payload(db, document_id)


    def delete_document(
        self,
        db: Session,
        *,
        document_id: int,
        deleted_by: User,
    ):
        #  Busca documento ativo
        document = db.query(Document).filter(
        Document.cod_documento == document_id,
        Document.ativo.is_(True)
        ).first()

        # Se não existir
        if not document:
            raise DocumentNotFoundException()

        # 🚫 Marca como inativo (remoção lógica)
        document.ativo = False
        
        # reindexa (remove do índice)
        # Atualiza índice para remover documento das buscas
        index_service.reindex_document(
            db,
            document_id=document_id,
            triggered_by=deleted_by
        )

        # Salva alterações
        db.commit()
        
        # Log administrativo
        administrative_history_service.log_action(
            db,
            actor=deleted_by,
            description=f"Documento {document.titulo} removido logicamente.",
            action_type="Remoção",
            entity_type="documento",
            entity_id=document_id,
        )

        return {"message": "Documento removido com sucesso."}


    def list_versions(self, db: Session, document_id: int):
        
          # Busca todas versões do documento
        versions = db.query(DocumentHistory).filter(
            DocumentHistory.cod_documento == document_id
        ).order_by(DocumentHistory.numero_versao.desc()).all()


        # Formata resposta
        return [
            {
                "version": int(v.numero_versao),
                "createdAt": v.criado_em,
                "active": v.versao_ativa,
            }
            for v in versions
        ]
        
        
    def restore_version(
        self,
        db: Session,
        *,
        document_id: int,
        version_number: int,
        restored_by: User,
    ):
        # Busca versão desejada
        target_version = db.query(DocumentHistory).filter(
        DocumentHistory.cod_documento == document_id,
        DocumentHistory.numero_versao == version_number
        ).first()

        # Se não existir
        if not target_version:
            raise DocumentNotFoundException("Versão não encontrada.")
        
        
        # Desativa versão atual
        db.query(DocumentHistory).filter(
            DocumentHistory.cod_documento == document_id,
            DocumentHistory.versao_ativa.is_(True)
        ).update({"versao_ativa": False})

        # Ativa versão escolhida
        target_version.versao_ativa = True
        
        
        # reindexa com conteúdo restaurado
        index_service.reindex_document(
            db,
            document_id=document_id,
            triggered_by=restored_by
        )

        # Salva alterações
        db.commit()
        
        # Log administrativo
        administrative_history_service.log_action(
        db,
        actor=restored_by,
        description=f"Documento restaurado para versão {version_number}.",
        action_type="Restauração",
        entity_type="documento",
        entity_id=document_id,
        )
        # Retorna documento atualizado
        return self.get_document_payload(db, document_id)



    def upload_document(
        self,
        db: Session,
        *,
        file: UploadFile,
        category: str,
        uploaded_by: User,
        document_date: date | None = None,
        title: str | None = None,
        author: str | None = None,
        document_type: str | None = None,
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
        document_title = self._normalize_metadata_value(
            title,
            fallback=Path(filename).stem or f"documento-{uuid4().hex[:8]}",
            max_length=255,
        )
        document_author = self._normalize_metadata_value(
            author,
            fallback=uploaded_by.nome,
            max_length=255,
        )
        metadata_document_type = self._normalize_metadata_value(
            document_type,
            fallback=extension.upper(),
            max_length=100,
        )
        original_file_name = self._normalize_metadata_value(
            filename,
            fallback=f"{document_title}.{extension}",
            max_length=255,
        )
        mime_type = self._normalize_metadata_value(
            file.content_type,
            fallback=adapter.mime_type,
            max_length=255,
        )
        file_hash = hashlib.sha256(content).hexdigest()
        category_row = self._get_or_create_category(db, normalized_category)
        processing_status = self._get_or_create_status(db, "processando")

        document = Document(
            cod_categoria=category_row.cod_categoria,
            titulo=document_title,
            tipo=extension.upper(),
            data_publicacao=self._coerce_document_datetime(document_date),
            ativo=True,
            cod_usuario_criador=uploaded_by.cod_usuario,
        )
        db.add(document)
        db.flush()

        metadata = DocumentMetadata(
            cod_documento=document.cod_documento,
            autor=document_author,
            tipo_documento=metadata_document_type,
            nome_arquivo_original=original_file_name,
            mime_type=mime_type,
            tamanho_bytes=len(content),
            hash_arquivo=file_hash,
        )
        db.add(metadata)
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
            description=f"Upload do documento {document_title}.{extension} concluído.",
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
        author: str | None = None,
        document_type: str | None = None,
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
                    author=author,
                    document_type=document_type,
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
        media_type = payload["mime_type"] or guess_type(file_name)[0] or self._get_mime_type(payload["type"].lower())
        return file_path, file_name, media_type

    def export_document(self, db: Session, *, document_id: int, export_format: str) -> tuple[str, str, str]:
        payload = self.get_document_payload(db, document_id)
        safe_title = self._safe_export_filename(payload["title"])

        if export_format == "json":
            content = json.dumps(
                self.to_details_response(payload),
                ensure_ascii=False,
                indent=2,
            )
            return content, f"{safe_title}.json", "application/json; charset=utf-8"

        metadata = [
            f"Título: {payload['title']}",
            f"Categoria: {payload['category']}",
            f"Tipo documental: {payload['document_type']}",
            f"Formato: {payload['type']}",
            f"Autor: {payload['author_name']}",
            f"Enviado por: {payload['uploaded_by_name']}",
            f"Arquivo original: {payload['file_name']}",
            f"MIME: {payload['mime_type'] or self._get_mime_type(payload['type'].lower())}",
            f"Hash SHA-256: {payload['file_hash']}",
            f"Versão: {payload['version']}",
            f"Data do documento: {payload['document_date'] or payload['uploaded_at']}",
            "",
            "Conteúdo extraído:",
            payload["content"] or "Pré-visualização indisponível para este formato.",
        ]
        return "\n".join(metadata), f"{safe_title}.txt", "text/plain; charset=utf-8"

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
        file_path = Path(payload["file_path"])
        download_url = (
            f"/api/v1/documents/{payload['id']}/download"
            if file_path.exists() and file_path.is_file()
            else None
        )
        return {
            "id": payload["id"],
            "title": payload["title"],
            "fileName": payload["file_name"],
            "category": payload["category"],
            "type": payload["type"],
            "documentType": payload["document_type"],
            "author": payload["author_name"],
            "mimeType": payload["mime_type"] or self._get_mime_type(payload["type"].lower()),
            "sizeBytes": payload["size_bytes"],
            "sizeLabel": self._format_size(payload["size_bytes"]),
            "date": document_date,
            "uploadedAt": payload["uploaded_at"],
            "validated": True,
            "integrityOk": True,
            "hash": payload["file_hash"],
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
        file_path = Path(payload["file_path"])
        download_url = (
            f"/api/v1/documents/{payload['id']}/download"
            if file_path.exists() and file_path.is_file()
            else None
        )
        return {
            "id": payload["id"],
            "title": payload["title"],
            "fileName": payload["file_name"],
            "category": payload["category"],
            "type": payload["type"],
            "documentType": payload["document_type"],
            "date": document_date,
            "author": payload["author_name"],
            "uploadedBy": payload["uploaded_by_name"],
            "format": payload["type"],
            "mimeType": payload["mime_type"] or self._get_mime_type(payload["type"].lower()),
            "pages": 1,
            "version": int(payload["version"]),
            "indexedAt": payload["uploaded_at"].isoformat(),
            "sizeBytes": payload["size_bytes"],
            "size": self._format_size(payload["size_bytes"]),
            "hash": payload["file_hash"],
            "downloadUrl": download_url,
            "content": payload["content"] or "Pré-visualização indisponível para este formato.",
            "extractedCharacters": extracted_characters,
        }

    def to_metadata_response(self, payload: dict) -> dict:
        document_date = (
            payload["document_date"].isoformat()
            if payload["document_date"]
            else None
        )
        return {
            "id": payload["id"],
            "title": payload["title"],
            "author": payload["author_name"],
            "uploadedBy": payload["uploaded_by_name"],
            "category": payload["category"],
            "documentType": payload["document_type"],
            "fileFormat": payload["type"],
            "fileName": payload["file_name"],
            "mimeType": payload["mime_type"] or self._get_mime_type(payload["type"].lower()),
            "sizeBytes": payload["size_bytes"],
            "sizeLabel": self._format_size(payload["size_bytes"]),
            "hash": payload["file_hash"],
            "publicationDate": document_date,
            "uploadedAt": payload["uploaded_at"],
            "version": int(payload["version"]),
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

    def _safe_export_filename(self, value: str) -> str:
        safe = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value.strip())
        return safe.strip("_") or "documento"

    def _normalize_metadata_value(
        self,
        value: str | None,
        *,
        fallback: str,
        max_length: int,
    ) -> str:
        normalized = (value or "").strip() or fallback.strip()
        return normalized[:max_length]







document_service = DocumentService(DocumentRepository())

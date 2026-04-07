from __future__ import annotations

import time

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.domain.document import Document
from app.domain.document_history import DocumentHistory
from app.domain.index_history import IndexHistory
from app.domain.ingestion_history import IngestionHistory
from app.domain.ingestion_status import IngestionStatus
from app.domain.user import User
from app.exceptions.document_exceptions import DocumentNotFoundException
from app.pipeline.document_ingestion_pipeline import DocumentIngestionPipeline
from app.pipeline.stages import (
    RelationalIndexPersistStage,
    TextPreprocessStage,
    TextTokenizeStage,
)
from app.services.administrative_history_service import administrative_history_service


class IndexService:
    def __init__(self):
        self.pipeline = DocumentIngestionPipeline(
            [
                TextPreprocessStage(),
                TextTokenizeStage(),
                RelationalIndexPersistStage(),
            ]
        )

    def process_document(
        self,
        db: Session,
        *,
        document_id: int,
        triggered_by: User,
        trigger_label: str = "Ingestão",
    ) -> dict:
        document = (
            db.query(Document)
            .filter(Document.cod_documento == document_id, Document.ativo.is_(True))
            .first()
        )
        if document is None:
            raise DocumentNotFoundException()

        document_history = (
            db.query(DocumentHistory)
            .filter(
                DocumentHistory.cod_documento == document_id,
                DocumentHistory.versao_ativa.is_(True),
            )
            .order_by(DocumentHistory.numero_versao.desc())
            .first()
        )
        if document_history is None:
            raise DocumentNotFoundException("Versão ativa do documento não encontrada.")

        started_at = time.perf_counter()
        context = {
            "document_id": document.cod_documento,
            "document_history": document_history,
            "extracted_text": document_history.texto_extraido or "",
        }

        try:
            with db.begin_nested():
                result = self.pipeline.run(db, context)
                db.add(
                    IndexHistory(
                        cod_historico_documento=document_history.cod_historico_documento,
                        tempo_indexacao_ms=int((time.perf_counter() - started_at) * 1000),
                        mensagem_erro=None,
                    )
                )
            db.flush()
            db.commit()
        except Exception as exc:
            db.add(
                IndexHistory(
                    cod_historico_documento=document_history.cod_historico_documento,
                    tempo_indexacao_ms=int((time.perf_counter() - started_at) * 1000),
                    mensagem_erro=str(exc)[:255],
                )
            )
            db.commit()
            raise

        administrative_history_service.log_action(
            db,
            actor=triggered_by,
            description=(
                f"{trigger_label} do documento {document.titulo} concluída com "
                f"{result['term_count']} termos indexados."
            ),
            action_type=trigger_label,
            entity_type="documento",
            entity_id=document.cod_documento,
        )
        return {
            "documentId": document.cod_documento,
            "termCount": result["term_count"],
            "tokenCount": result["token_count"],
        }

    def reindex_document(self, db: Session, *, document_id: int, triggered_by: User) -> dict:
        return self.process_document(
            db,
            document_id=document_id,
            triggered_by=triggered_by,
            trigger_label="Reindexação",
        )

    def reindex_all_documents(self, db: Session, *, triggered_by: User) -> dict:
        document_ids = [
            row.cod_documento
            for row in db.query(Document.cod_documento)
            .filter(Document.ativo.is_(True))
            .order_by(Document.cod_documento.asc())
            .all()
        ]

        success_count = 0
        failure_count = 0
        for document_id in document_ids:
            try:
                self.reindex_document(db, document_id=document_id, triggered_by=triggered_by)
                success_count += 1
            except Exception:
                db.rollback()
                failure_count += 1

        return {
            "processedDocuments": len(document_ids),
            "successCount": success_count,
            "failureCount": failure_count,
            "message": (
                f"Reindexação concluída: {success_count} sucesso(s), "
                f"{failure_count} falha(s)."
            ),
        }

    def get_status_snapshot(self, db: Session) -> dict:
        total_runs = db.query(func.count(IndexHistory.cod_historico_indexacao)).scalar() or 0
        success_runs = (
            db.query(func.count(IndexHistory.cod_historico_indexacao))
            .filter(IndexHistory.mensagem_erro.is_(None))
            .scalar()
            or 0
        )
        error_runs = total_runs - success_runs
        average_ms = (
            db.query(func.avg(IndexHistory.tempo_indexacao_ms))
            .filter(IndexHistory.mensagem_erro.is_(None))
            .scalar()
        )
        indexed_documents = (
            db.query(func.count(func.distinct(DocumentHistory.cod_documento)))
            .join(
                IndexHistory,
                IndexHistory.cod_historico_documento == DocumentHistory.cod_historico_documento,
            )
            .filter(DocumentHistory.versao_ativa.is_(True))
            .filter(IndexHistory.mensagem_erro.is_(None))
            .scalar()
            or 0
        )

        ingestion_summary = (
            db.query(
                func.sum(
                    case((IngestionStatus.estado_ingestao == "concluido", 1), else_=0)
                ).label("completed"),
                func.sum(
                    case((IngestionStatus.estado_ingestao == "processando", 1), else_=0)
                ).label("processing"),
                func.sum(
                    case((IngestionStatus.estado_ingestao == "falha", 1), else_=0)
                ).label("failed"),
            )
            .select_from(IngestionHistory)
            .join(
                IngestionStatus,
                IngestionStatus.cod_status_ingestao == IngestionHistory.cod_status_ingestao,
            )
            .first()
        )

        recent_logs = (
            db.query(
                IndexHistory.criado_em,
                IndexHistory.mensagem_erro,
                Document.titulo,
            )
            .join(
                DocumentHistory,
                DocumentHistory.cod_historico_documento == IndexHistory.cod_historico_documento,
            )
            .join(Document, Document.cod_documento == DocumentHistory.cod_documento)
            .order_by(
                IndexHistory.criado_em.desc(),
                IndexHistory.cod_historico_indexacao.desc(),
            )
            .limit(20)
            .all()
        )

        return {
            "indexedDocuments": indexed_documents,
            "averageTime": self._format_duration(average_ms),
            "successRate": f"{round((success_runs / total_runs) * 100, 1) if total_runs else 0:.1f}%",
            "errors": error_runs,
            "currentProgress": 100 if total_runs else 0,
            "remainingEstimate": "0 min",
            "summary": {
                "completed": int(ingestion_summary.completed or 0) if ingestion_summary else 0,
                "processing": int(ingestion_summary.processing or 0) if ingestion_summary else 0,
                "failed": int(ingestion_summary.failed or 0) if ingestion_summary else 0,
            },
            "logs": [
                {
                    "time": row.criado_em.strftime("%H:%M:%S") if row.criado_em else "",
                    "message": (
                        f"{row.titulo} indexado com sucesso."
                        if row.mensagem_erro is None
                        else f"{row.titulo} falhou: {row.mensagem_erro}"
                    ),
                    "type": "success" if row.mensagem_erro is None else "error",
                }
                for row in recent_logs
            ],
        }

    def _format_duration(self, duration_ms: float | None) -> str:
        if duration_ms is None:
            return "0 ms"
        duration_ms = float(duration_ms)
        if duration_ms >= 1000:
            return f"{duration_ms / 1000:.2f}s"
        return f"{duration_ms:.0f} ms"


index_service = IndexService()

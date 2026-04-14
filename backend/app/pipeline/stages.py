from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.domain.document_history import DocumentHistory
from app.exceptions.document_exceptions import DocumentValidationException
from app.pipeline.pipeline_stage import PipelineStage
from app.services.inverted_index_service import inverted_index_service
from app.utils.text_processing import preprocess_for_indexing


class TextPreprocessStage(PipelineStage):
    def execute(self, db: Session, context: dict) -> dict:
        del db
        extracted_text = context.get("extracted_text", "")
        preprocessed = preprocess_for_indexing(extracted_text)
        if not preprocessed["normalized_text"]:
            raise DocumentValidationException(
                "Não foi possível gerar conteúdo processável para indexação."
            )
        context["normalized_text"] = preprocessed["normalized_text"]
        context["preprocessed_output"] = preprocessed
        return context


class TextTokenizeStage(PipelineStage):
    def execute(self, db: Session, context: dict) -> dict:
        del db
        preprocessed = context.get("preprocessed_output") or preprocess_for_indexing(
            context.get("extracted_text", "")
        )
        tokens = preprocessed["tokens"]
        if not tokens:
            raise DocumentValidationException(
                "O documento não contém termos válidos para indexação."
            )
        context["processed_text"] = preprocessed["processed_text"]
        context["tokens"] = tokens
        context["index_payload"] = preprocessed
        return context


class RelationalIndexPersistStage(PipelineStage):
    def execute(self, db: Session, context: dict) -> dict:
        history: DocumentHistory = context["document_history"]
        processed_text: str = context["processed_text"]

        index_payload = context.get("index_payload") or {
            "positions_by_term": defaultdict(list)
        }
        positions_by_term: dict[str, list[int]] = index_payload["positions_by_term"]
        result = inverted_index_service.persist_document_terms(
            db,
            history=history,
            processed_text=processed_text,
            positions_by_term=positions_by_term,
        )

        context["term_count"] = index_payload.get("term_count", result["term_count"])
        context["token_count"] = index_payload.get("token_count", result["token_count"])
        return context

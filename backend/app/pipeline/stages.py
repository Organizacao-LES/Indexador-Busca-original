from __future__ import annotations

import math
from collections import defaultdict

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.domain.document import Document
from app.domain.document_field import DocumentField
from app.domain.document_history import DocumentHistory
from app.domain.field_type import FieldType
from app.domain.inverted_index import InvertedIndex
from app.domain.term import Term
from app.exceptions.document_exceptions import DocumentValidationException
from app.pipeline.pipeline_stage import PipelineStage
from app.utils.text_processing import normalize_text, tokenize_text


class TextPreprocessStage(PipelineStage):
    def execute(self, db: Session, context: dict) -> dict:
        del db
        extracted_text = context.get("extracted_text", "")
        processed_text = normalize_text(extracted_text)
        if not processed_text:
            raise DocumentValidationException(
                "Não foi possível gerar conteúdo processável para indexação."
            )
        context["processed_text"] = processed_text
        return context


class TextTokenizeStage(PipelineStage):
    def execute(self, db: Session, context: dict) -> dict:
        del db
        tokens = tokenize_text(context.get("processed_text", ""))
        if not tokens:
            raise DocumentValidationException(
                "O documento não contém termos válidos para indexação."
            )
        context["tokens"] = tokens
        return context


class RelationalIndexPersistStage(PipelineStage):
    def execute(self, db: Session, context: dict) -> dict:
        history: DocumentHistory = context["document_history"]
        processed_text: str = context["processed_text"]
        tokens: list[str] = context["tokens"]

        history.texto_processado = processed_text

        field_type = (
            db.query(FieldType)
            .filter(FieldType.tipo_campo == "conteudo")
            .first()
        )
        if field_type is None:
            field_type = FieldType(tipo_campo="conteudo")
            db.add(field_type)
            db.flush()

        existing_field_ids = [
            row.cod_campo_documento
            for row in db.query(DocumentField.cod_campo_documento)
            .filter(DocumentField.cod_historico_documento == history.cod_historico_documento)
            .all()
        ]
        affected_term_ids: set[int] = set()
        if existing_field_ids:
            affected_term_ids.update(
                row.cod_termo
                for row in db.query(InvertedIndex.cod_termo)
                .filter(InvertedIndex.cod_campo_documento.in_(existing_field_ids))
                .distinct()
                .all()
            )
            db.query(InvertedIndex).filter(
                InvertedIndex.cod_campo_documento.in_(existing_field_ids)
            ).delete(synchronize_session=False)
            db.query(DocumentField).filter(
                DocumentField.cod_campo_documento.in_(existing_field_ids)
            ).delete(synchronize_session=False)

        document_field = DocumentField(
            cod_historico_documento=history.cod_historico_documento,
            cod_tipo_campo=field_type.cod_tipo_campo,
            conteudo=processed_text,
        )
        db.add(document_field)
        db.flush()

        positions_by_term: dict[str, list[int]] = defaultdict(list)
        for position, token in enumerate(tokens):
            positions_by_term[token].append(position)

        touched_terms: list[Term] = []
        for token, positions in positions_by_term.items():
            term = db.query(Term).filter(Term.texto_termo == token).first()
            if term is None:
                term = Term(texto_termo=token, df=0, idf=0)
                db.add(term)
                db.flush()

            db.add(
                InvertedIndex(
                    cod_termo=term.cod_termo,
                    cod_campo_documento=document_field.cod_campo_documento,
                    tf=len(positions),
                    posicao_inicial=positions[0],
                )
            )
            touched_terms.append(term)
            affected_term_ids.add(term.cod_termo)

        db.flush()

        active_document_count = (
            db.query(func.count(Document.cod_documento))
            .filter(Document.ativo.is_(True))
            .scalar()
            or 0
        )

        for term_id in affected_term_ids:
            term = db.query(Term).filter(Term.cod_termo == term_id).first()
            if term is None:
                continue

            document_frequency = (
                db.query(func.count(distinct(Document.cod_documento)))
                .select_from(InvertedIndex)
                .join(
                    DocumentField,
                    DocumentField.cod_campo_documento == InvertedIndex.cod_campo_documento,
                )
                .join(
                    DocumentHistory,
                    DocumentHistory.cod_historico_documento == DocumentField.cod_historico_documento,
                )
                .join(Document, Document.cod_documento == DocumentHistory.cod_documento)
                .filter(InvertedIndex.cod_termo == term.cod_termo)
                .filter(Document.ativo.is_(True))
                .filter(DocumentHistory.versao_ativa.is_(True))
                .scalar()
                or 0
            )

            term.df = document_frequency
            if document_frequency > 0 and active_document_count > 0:
                scaled_idf = math.log((active_document_count + 1) / (document_frequency + 1) + 1)
                term.idf = max(int(round(scaled_idf * 1000)), 1)
            else:
                term.idf = 0

        context["term_count"] = len(positions_by_term)
        context["token_count"] = len(tokens)
        return context

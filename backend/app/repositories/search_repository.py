from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.document_category import DocumentCategory
from app.domain.document_field import DocumentField
from app.domain.inverted_index import InvertedIndex
from app.domain.document import Document
from app.domain.document_history import DocumentHistory
from app.domain.document_metadata import DocumentMetadata
from app.domain.search_history import SearchHistory
from app.domain.term import Term


class SearchRepository:
    def search_terms(
        self,
        db: Session,
        *,
        terms: list[str],
        category: str | None = None,
        document_type: str | None = None,
        author: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        query = (
            db.query(
                Document.cod_documento.label("document_id"),
                Document.titulo.label("title"),
                Document.tipo.label("document_type"),
                DocumentMetadata.tipo_documento.label("metadata_document_type"),
                Document.data_publicacao.label("document_date"),
                DocumentCategory.nome_categoria.label("category"),
                Term.texto_termo.label("term"),
                Term.idf.label("idf"),
                InvertedIndex.tf.label("tf"),
                InvertedIndex.posicao_inicial.label("posicao_inicial"),
            )
            .select_from(InvertedIndex)
            .join(Term, Term.cod_termo == InvertedIndex.cod_termo)
            .join(
                DocumentField,
                DocumentField.cod_campo_documento == InvertedIndex.cod_campo_documento,
            )
            .join(
                DocumentHistory,
                DocumentHistory.cod_historico_documento == DocumentField.cod_historico_documento,
            )
            .join(Document, Document.cod_documento == DocumentHistory.cod_documento)
            .join(DocumentCategory, DocumentCategory.cod_categoria == Document.cod_categoria)
            .outerjoin(DocumentMetadata, DocumentMetadata.cod_documento == Document.cod_documento)
            .filter(Term.texto_termo.in_(terms))
            .filter(Document.ativo.is_(True))
            .filter(DocumentHistory.versao_ativa.is_(True))
        )

        if category:
            query = query.filter(DocumentCategory.nome_categoria.ilike(category.strip()))
        if document_type:
            normalized_document_type = f"%{document_type.strip()}%"
            query = query.filter(
                (Document.tipo.ilike(normalized_document_type))
                | (DocumentMetadata.tipo_documento.ilike(normalized_document_type))
            )
        if author:
            query = query.filter(DocumentMetadata.autor.ilike(f"%{author.strip()}%"))
        if date_from:
            query = query.filter(Document.data_publicacao >= date_from)
        if date_to:
            query = query.filter(Document.data_publicacao <= date_to)

        return query.all()

    def create_search_history(
        self,
        db: Session,
        *,
        user_id: int,
        query: str,
        filters: str | None,
        result_count: int,
        response_time_ms: int,
    ) -> SearchHistory:
        history = SearchHistory(
            cod_usuario=user_id,
            consulta_texto=query,
            filtros=filters,
            quantidade_resultados=result_count,
            tempo_resposta_ms=response_time_ms,
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    def list_recent_searches(self, db: Session, *, user_id: int, limit: int = 10) -> list[SearchHistory]:
        return (
            db.query(SearchHistory)
            .filter(SearchHistory.cod_usuario == user_id)
            .order_by(
                SearchHistory.criado_em.desc(),
                SearchHistory.cod_historico_busca.desc(),
            )
            .limit(limit)
            .all()
        )

    def list_search_history(
        self,
        db: Session,
        *,
        user_id: int,
        query_text: str | None = None,
        performed_from: datetime | None = None,
        performed_to: datetime | None = None,
        limit: int = 20,
        page: int = 1,
    ) -> tuple[list[SearchHistory], int]:
        base_query = db.query(SearchHistory).filter(SearchHistory.cod_usuario == user_id)

        if query_text:
            base_query = base_query.filter(
                SearchHistory.consulta_texto.ilike(f"%{query_text.strip()}%")
            )
        if performed_from:
            base_query = base_query.filter(SearchHistory.criado_em >= performed_from)
        if performed_to:
            base_query = base_query.filter(SearchHistory.criado_em <= performed_to)

        total = base_query.count()
        rows = (
            base_query.order_by(
                SearchHistory.criado_em.desc(),
                SearchHistory.cod_historico_busca.desc(),
            )
            .offset(max(page - 1, 0) * limit)
            .limit(limit)
            .all()
        )
        return rows, total

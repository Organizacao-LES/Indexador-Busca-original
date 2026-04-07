from sqlalchemy.orm import Session
from sqlalchemy import func

from app.domain.inverted_index import InvertedIndex
from app.domain.term import Term
from app.domain.document_history import DocumentHistory
from app.domain.document import Document


class SearchRepository:

    def search_terms(self, db: Session, terms: list[str]):

        return (
            db.query(
                Document.cod_documento.label("document_id"),
                Document.titulo.label("title"),
                Term.texto_termo.label("term"),           
                Term.idf.label("idf"),
                InvertedIndex.tf.label("tf"),
            )
            .join(DocumentHistory, DocumentHistory.cod_historico_documento == InvertedIndex.cod_campo_documento)
            .join(Document, Document.cod_documento == DocumentHistory.cod_documento)
            .join(Term, Term.cod_termo == InvertedIndex.cod_termo)
            .filter(Term.texto_termo.in_(terms))
            .filter(DocumentHistory.versao_ativa.is_(True))
            .group_by(Document.cod_documento, Document.titulo)
            .order_by(func.sum(InvertedIndex.tf).desc())
            .all()
        )
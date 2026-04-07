import math
import time
from collections import defaultdict

from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.repositories.search_repository import SearchRepository
from app.utils.text_processing import preprocess_for_indexing


class SearchService:
    def __init__(self, repository: SearchRepository):
        self.repository = repository
        self.document_repository = DocumentRepository()

    def search(
        self,
        db: Session,
        *,
        query: str,
        user_id: int,
        limit: int = 10,
        page: int = 1,
        category: str | None = None,
        document_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        sort_by: str | None = None,
    ) -> dict:
        started_at = time.perf_counter()
        if not query or not query.strip():
            return self._empty_response(query=query, page=page, per_page=limit)

        terms = self._process_query(query)
        if not terms:
            response = self._empty_response(query=query, page=page, per_page=limit)
            self._register_search(
                db,
                user_id=user_id,
                query=query,
                filters=self._serialize_filters(category, document_type, date_from, date_to, sort_by),
                result_count=0,
                started_at=started_at,
            )
            return response

        rows = self.repository.search_terms(
            db,
            terms=terms,
            category=category,
            document_type=document_type,
            date_from=date_from,
            date_to=date_to,
        )

        scores = defaultdict(float)
        matched_terms_by_document: dict[int, set[str]] = defaultdict(set)
        for row in rows:
            tf = row.tf or 0
            idf = row.idf or 1
            score = tf * idf
            scores[row.document_id] += score
            matched_terms_by_document[row.document_id].add(row.term)

        ranked_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        if sort_by == "data-desc":
            ranked_docs = self._sort_by_date(db, ranked_docs, reverse=True)
        elif sort_by == "data-asc":
            ranked_docs = self._sort_by_date(db, ranked_docs, reverse=False)
        elif sort_by == "titulo":
            ranked_docs = self._sort_by_title(db, ranked_docs)

        start = max((page - 1) * limit, 0)
        end = start + limit
        paginated = ranked_docs[start:end]
        top_score = ranked_docs[0][1] if ranked_docs else 0
        items = []

        for doc_id, score in paginated:
            payload = self.document_repository.get_document_payload(db, doc_id)
            if payload:
                items.append(
                    {
                        "id": payload["id"],
                        "title": payload["title"],
                        "snippet": self._build_snippet(payload["content"] or "", list(matched_terms_by_document[doc_id])),
                        "category": payload["category"],
                        "type": payload["type"],
                        "date": (
                            payload["document_date"].isoformat()
                            if payload["document_date"]
                            else payload["uploaded_at"].isoformat()
                        ),
                        "relevance": self._normalize_relevance(score, top_score),
                    }
                )

        response = {
            "query": query,
            "total": len(ranked_docs),
            "page": page,
            "perPage": limit,
            "totalPages": max(math.ceil(len(ranked_docs) / limit), 1),
            "items": items,
        }
        self._register_search(
            db,
            user_id=user_id,
            query=query,
            filters=self._serialize_filters(category, document_type, date_from, date_to, sort_by),
            result_count=len(ranked_docs),
            started_at=started_at,
        )
        return response

    def _process_query(self, query: str) -> list[str]:
        return preprocess_for_indexing(query)["tokens"]

    def list_recent_searches(self, db: Session, *, user_id: int, limit: int = 10) -> list[dict]:
        rows = self.repository.list_recent_searches(db, user_id=user_id, limit=limit)
        return [
            {
                "id": row.cod_historico_busca,
                "term": row.consulta_texto,
            }
            for row in rows
        ]

    def _build_snippet(self, content: str, matched_terms: list[str]) -> str:
        snippet = (content or "").strip().replace("\n", " ")
        snippet = snippet[:240]
        for term in matched_terms:
            snippet = snippet.replace(term, f"<mark>{term}</mark>")
            snippet = snippet.replace(term.capitalize(), f"<mark>{term.capitalize()}</mark>")
        return snippet

    def _normalize_relevance(self, score: float, top_score: float) -> int:
        if top_score <= 0:
            return 0
        return min(max(int(round((score / top_score) * 100)), 1), 100)

    def _sort_by_date(self, db: Session, ranked_docs: list[tuple[int, float]], *, reverse: bool) -> list[tuple[int, float]]:
        def key_fn(item: tuple[int, float]):
            payload = self.document_repository.get_document_payload(db, item[0])
            date_value = payload["document_date"] or payload["uploaded_at"]
            return date_value

        return sorted(ranked_docs, key=key_fn, reverse=reverse)

    def _sort_by_title(self, db: Session, ranked_docs: list[tuple[int, float]]) -> list[tuple[int, float]]:
        def key_fn(item: tuple[int, float]):
            payload = self.document_repository.get_document_payload(db, item[0])
            return payload["title"].lower()

        return sorted(ranked_docs, key=key_fn)

    def _register_search(
        self,
        db: Session,
        *,
        user_id: int,
        query: str,
        filters: str | None,
        result_count: int,
        started_at: float,
    ) -> None:
        self.repository.create_search_history(
            db,
            user_id=user_id,
            query=query,
            filters=filters,
            result_count=result_count,
            response_time_ms=int((time.perf_counter() - started_at) * 1000),
        )

    def _serialize_filters(
        self,
        category: str | None,
        document_type: str | None,
        date_from: str | None,
        date_to: str | None,
        sort_by: str | None,
    ) -> str | None:
        filters = {
            "category": category,
            "documentType": document_type,
            "dateFrom": date_from,
            "dateTo": date_to,
            "sortBy": sort_by,
        }
        filtered_items = [f"{key}={value}" for key, value in filters.items() if value]
        return ";".join(filtered_items) if filtered_items else None

    def _empty_response(self, *, query: str, page: int, per_page: int) -> dict:
        return {
            "query": query,
            "total": 0,
            "page": page,
            "perPage": per_page,
            "totalPages": 1,
            "items": [],
        }


search_service = SearchService(SearchRepository())

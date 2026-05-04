from datetime import date, datetime, time as dt_time
import math
import time

from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.repositories.search_repository import SearchRepository
from app.domain.user import User
from app.strategies.search_ranking_strategy import SearchRankingStrategy
from app.utils.text_processing import preprocess_for_indexing


class SearchService:
    def __init__(self, repository: SearchRepository):
        self.repository = repository
        self.document_repository = DocumentRepository()
        self.ranking_strategy = SearchRankingStrategy()

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
        author: str | None = None,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
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
                filters=self._serialize_filters(
                    category,
                    document_type,
                    author,
                    date_from,
                    date_to,
                    sort_by,
                ),
                result_count=0,
                started_at=started_at,
            )
            return response

        normalized_date_from = self._coerce_date_boundary(date_from, end_of_day=False)
        normalized_date_to = self._coerce_date_boundary(date_to, end_of_day=True)
        rows = self.repository.search_terms(
            db,
            terms=terms,
            category=category,
            document_type=document_type,
            author=author,
            date_from=normalized_date_from,
            date_to=normalized_date_to,
        )

        ranked_items = self.ranking_strategy.rank(rows, terms)
        ranked_docs = [
            (item["document_id"], item["score"], item["matched_terms"])
            for item in ranked_items
        ]
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

        for doc_id, score, matched_terms in paginated:
            payload = self.document_repository.get_document_payload(db, doc_id)
            if payload:
                snippet_source = self._searchable_result_text(payload)
                items.append(
                    {
                        "id": payload["id"],
                        "title": payload["title"],
                        "snippet": self._build_snippet(snippet_source, list(matched_terms)),
                        "category": payload["category"],
                        "type": payload["type"],
                        "documentType": payload["document_type"],
                        "author": payload["author_name"],
                        "fileName": payload["file_name"],
                        "mimeType": payload["mime_type"] or "",
                        "size": self._format_size(payload["size_bytes"]),
                        "date": (
                            payload["document_date"].isoformat()
                            if payload["document_date"]
                            else payload["uploaded_at"].isoformat()
                        ),
                        "relevance": self._normalize_relevance(score, top_score),
                    }
                )

        response_time_ms = int((time.perf_counter() - started_at) * 1000)
        response = {
            "query": query,
            "total": len(ranked_docs),
            "page": page,
            "perPage": limit,
            "totalPages": max(math.ceil(len(ranked_docs) / limit), 1),
            "responseTimeMs": response_time_ms,
            "items": items,
        }
        self._register_search(
            db,
            user_id=user_id,
            query=query,
            filters=self._serialize_filters(
                category,
                document_type,
                author,
                date_from,
                date_to,
                sort_by,
            ),
            result_count=len(ranked_docs),
            response_time_ms=response_time_ms,
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

    def list_search_history(
        self,
        db: Session,
        *,
        current_user: User,
        limit: int = 20,
        page: int = 1,
        query: str | None = None,
        performed_from: date | str | None = None,
        performed_to: date | str | None = None,
    ) -> dict:
        normalized_from = self._coerce_date_boundary(performed_from, end_of_day=False)
        normalized_to = self._coerce_date_boundary(performed_to, end_of_day=True)
        rows, total = self.repository.list_search_history(
            db,
            user_id=current_user.cod_usuario,
            query_text=query,
            performed_from=normalized_from,
            performed_to=normalized_to,
            limit=limit,
            page=page,
        )

        items = [
            {
                "id": row.cod_historico_busca,
                "query": row.consulta_texto,
                "createdAt": row.criado_em.isoformat() if row.criado_em else "",
                "resultCount": int(row.quantidade_resultados or 0),
                "responseTimeMs": int(row.tempo_resposta_ms or 0),
                "user": current_user.email,
                "filters": self._deserialize_filters(row.filtros),
            }
            for row in rows
        ]
        return {
            "total": total,
            "page": page,
            "perPage": limit,
            "totalPages": max(math.ceil(total / limit), 1),
            "items": items,
        }

    def _build_snippet(self, content: str, matched_terms: list[str]) -> str:
        snippet = (content or "").strip().replace("\n", " ")
        snippet = snippet[:240]
        for term in matched_terms:
            snippet = snippet.replace(term, f"<mark>{term}</mark>")
            snippet = snippet.replace(term.capitalize(), f"<mark>{term.capitalize()}</mark>")
        return snippet

    def _searchable_result_text(self, payload: dict) -> str:
        values = [
            payload.get("title"),
            payload.get("author_name"),
            payload.get("category"),
            payload.get("document_type"),
            payload.get("file_name"),
            payload.get("content"),
        ]
        return "\n".join(str(value) for value in values if value)

    def _normalize_relevance(self, score: float, top_score: float) -> int:
        if top_score <= 0:
            return 0
        return min(max(int(round((score / top_score) * 100)), 1), 100)

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _sort_by_date(self, db: Session, ranked_docs: list[tuple[int, float, set[str]]], *, reverse: bool) -> list[tuple[int, float, set[str]]]:
        def key_fn(item: tuple[int, float, set[str]]):
            payload = self.document_repository.get_document_payload(db, item[0])
            date_value = payload["document_date"] or payload["uploaded_at"]
            return date_value

        return sorted(ranked_docs, key=key_fn, reverse=reverse)

    def _sort_by_title(self, db: Session, ranked_docs: list[tuple[int, float, set[str]]]) -> list[tuple[int, float, set[str]]]:
        def key_fn(item: tuple[int, float, set[str]]):
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
        response_time_ms: int,
    ) -> None:
        self.repository.create_search_history(
            db,
            user_id=user_id,
            query=query,
            filters=filters,
            result_count=result_count,
            response_time_ms=response_time_ms,
        )

    def _serialize_filters(
        self,
        category: str | None,
        document_type: str | None,
        author: str | None,
        date_from: date | str | None,
        date_to: date | str | None,
        sort_by: str | None,
    ) -> str | None:
        filters = {
            "category": category,
            "documentType": document_type,
            "author": author,
            "dateFrom": self._stringify_date_filter(date_from),
            "dateTo": self._stringify_date_filter(date_to),
            "sortBy": sort_by,
        }
        filtered_items = [f"{key}={value}" for key, value in filters.items() if value]
        return ";".join(filtered_items) if filtered_items else None

    def _deserialize_filters(self, serialized_filters: str | None) -> dict:
        filters = {
            "category": None,
            "documentType": None,
            "author": None,
            "dateFrom": None,
            "dateTo": None,
            "sortBy": None,
        }
        if not serialized_filters:
            return filters

        for item in serialized_filters.split(";"):
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            if key in filters and value:
                filters[key] = value
        return filters

    def _coerce_date_boundary(
        self,
        value: date | str | None,
        *,
        end_of_day: bool,
    ) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            value = date.fromisoformat(value)
        boundary_time = dt_time.max if end_of_day else dt_time.min
        return datetime.combine(value, boundary_time)

    def _stringify_date_filter(self, value: date | str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return value.isoformat()

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

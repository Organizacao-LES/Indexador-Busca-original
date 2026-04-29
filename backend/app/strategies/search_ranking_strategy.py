from __future__ import annotations

import math
from datetime import datetime

from app.utils.text_processing import preprocess_for_indexing


class SearchRankingStrategy:
    def rank(self, rows: list, query_terms: list[str]) -> list[dict]:
        unique_query_terms = set(query_terms)
        documents: dict[int, dict] = {}

        for row in rows:
            document = documents.setdefault(
                row.document_id,
                {
                    "document_id": row.document_id,
                    "score": 0.0,
                    "matched_terms": set(),
                    "title": row.title or "",
                    "document_date": row.document_date,
                },
            )
            document["score"] += self._row_score(row)
            document["matched_terms"].add(row.term)

        for document in documents.values():
            document["score"] *= self._coverage_weight(
                document["matched_terms"],
                unique_query_terms,
            )
            document["score"] *= self._title_weight(document["title"], document["matched_terms"])
            document["score"] *= self._recency_weight(document["document_date"])

        return sorted(documents.values(), key=lambda item: item["score"], reverse=True)

    def _row_score(self, row) -> float:
        tf = float(row.tf or 0)
        idf = float(row.idf or 1)
        position = int(row.posicao_inicial or 0)
        position_weight = 1.0 / math.sqrt(position + 1)
        return tf * idf * position_weight

    def _coverage_weight(self, matched_terms: set[str], query_terms: set[str]) -> float:
        if not query_terms:
            return 1.0
        coverage = len(matched_terms) / len(query_terms)
        return 1.0 + (coverage * 0.45)

    def _title_weight(self, title: str, matched_terms: set[str]) -> float:
        title_tokens = set(preprocess_for_indexing(title)["tokens"])
        if not title_tokens:
            return 1.0
        title_matches = len(title_tokens.intersection(matched_terms))
        return 1.0 + min(title_matches * 0.12, 0.36)

    def _recency_weight(self, document_date) -> float:
        if document_date is None:
            return 1.0
        if isinstance(document_date, str):
            try:
                document_date = datetime.fromisoformat(document_date)
            except ValueError:
                return 1.0
        age_days = max((datetime.utcnow() - document_date.replace(tzinfo=None)).days, 0)
        if age_days <= 365:
            return 1.08
        if age_days <= 1095:
            return 1.03
        return 1.0

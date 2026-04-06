import re
from collections import defaultdict
from sqlalchemy.orm import Session

from app.repositories.search_repository import SearchRepository
from app.repositories.document_repository import DocumentRepository

class SearchService:

    def __init__(self, repository: SearchRepository):
        self.repository = repository
        self.document_repository = DocumentRepository()

    def search(self, db: Session, query: str, limit: int = 10):

        if not query or not query.strip():
            return []

        # 🔹 processamento básico (igual pipeline)
        terms = self._process_query(query)

        if not terms:
            return []

        rows = self.repository.search_terms(db, terms)
        
        scores = defaultdict(float)
        
        for row in rows:
            tf = row.tf or 0
            idf = row.idf or 1
            score = tf * idf
            scores[row.document_id] += score
            
        
        # ordenar por score
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        
        for doc_id, score in ranked_docs[:limit]:
            payload = self.document_repository.get_document_payload(db, doc_id)

            if payload:
                results.append({
                    "id": payload["id"],
                    "title": payload["title"],
                    "category": payload["category"],
                    "score": round(score, 4),
                    "snippet": (payload["content"] or "")[:200]
                })

        return results



        

    def _process_query(self, query: str) -> list[str]:
        
        # lowercase + tokenização simples
        query = query.lower()
        tokens = re.findall(r"\w+", query)

        return tokens
        
        
       


search_service = SearchService(SearchRepository())
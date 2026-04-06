from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domain.user import User
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
def search_documents(
    q: str = Query(..., min_length=1, description="Consulta de busca"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    results = search_service.search(db, query=q, limit=limit)
    return {
        "query": q,
        "total": len(results),
        "results": results,
    }
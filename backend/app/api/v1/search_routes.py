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
    category: str | None = Query(default=None),
    documentType: str | None = Query(default=None),
    dateFrom: str | None = Query(default=None),
    dateTo: str | None = Query(default=None),
    sortBy: str | None = Query(default=None),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return search_service.search(
        db,
        query=q,
        user_id=current_user.cod_usuario,
        category=category,
        document_type=documentType,
        date_from=dateFrom,
        date_to=dateTo,
        sort_by=sortBy,
        limit=limit,
        page=page,
    )


@router.get("/history")
def list_recent_searches(
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return search_service.list_recent_searches(
        db,
        user_id=current_user.cod_usuario,
        limit=limit,
    )

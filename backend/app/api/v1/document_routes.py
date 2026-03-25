from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.document_schema import DocumentDetailsResponse
from app.services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/{document_id}", response_model=DocumentDetailsResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    payload = document_service.get_document_payload(db, document_id)
    return document_service.to_details_response(payload)

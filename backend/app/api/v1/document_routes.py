from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domain.user import User
from app.schemas.document_schema import DocumentDetailsResponse
from app.services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/{document_id}", response_model=DocumentDetailsResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    payload = document_service.get_document_payload(db, document_id)
    return document_service.to_details_response(payload)


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    file_path, file_name, media_type = document_service.get_document_file(db, document_id)
    return FileResponse(path=file_path, filename=file_name, media_type=media_type)

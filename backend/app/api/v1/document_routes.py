from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.domain.user import User
from app.domain.user_role import UserRole
from app.schemas.document_schema import DocumentDetailsResponse
from app.schemas.index_schema import ReindexResponse
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


@router.get("/{document_id}/export")
def export_document(
    document_id: int,
    format: str = Query("txt", pattern="^(txt|json)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    content, file_name, media_type = document_service.export_document(
        db,
        document_id=document_id,
        export_format=format,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.post("/{document_id}/reindex", response_model=ReindexResponse)
def reindex_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    result = document_service.reindex_document(
        db,
        document_id=document_id,
        triggered_by=current_user,
    )
    return {
        "processedDocuments": 1,
        "successCount": 1,
        "failureCount": 0,
        "message": (
            f"Documento {document_id} reindexado com "
            f"{result['termCount']} termos."
        ),
    }

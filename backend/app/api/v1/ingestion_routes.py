from datetime import date

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domain.user import User
from app.schemas.document_schema import (
    BatchUploadResponse,
    DocumentUploadResponse,
    IngestionBatchFileResponse,
    IngestionHistoryEntryResponse,
)
from app.services.document_service import document_service

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    document_date: date | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = document_service.upload_document(
        db,
        file=file,
        category=category,
        uploaded_by=current_user,
        document_date=document_date,
    )
    return document_service.to_upload_response(document)


@router.post(
    "/upload-batch",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_documents_batch(
    files: list[UploadFile] = File(...),
    category: str = Form(...),
    document_date: date | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return document_service.upload_documents_batch(
        db,
        files=files,
        category=category,
        uploaded_by=current_user,
        document_date=document_date,
    )


@router.get("/batch", response_model=list[IngestionBatchFileResponse])
def get_batch_files(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    documents = document_service.list_batch_files(db)
    return [document_service.to_batch_response(document) for document in documents]


@router.get("/history", response_model=list[IngestionHistoryEntryResponse])
def get_ingestion_history(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    documents = document_service.list_ingestion_history(db)
    return [document_service.to_history_response(document) for document in documents]

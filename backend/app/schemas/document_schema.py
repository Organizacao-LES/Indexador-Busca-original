from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    id: int
    title: str
    fileName: str
    category: str
    type: str
    mimeType: str
    sizeBytes: int
    sizeLabel: str
    date: date | None
    uploadedAt: datetime
    validated: bool
    integrityOk: bool
    hash: str


class DocumentDetailsResponse(BaseModel):
    id: int
    title: str
    category: str
    type: str
    date: str
    author: str
    format: str
    pages: int
    version: int
    indexedAt: str
    size: str
    downloadUrl: str | None = None
    content: str


class IngestionBatchFileResponse(BaseModel):
    name: str
    size: str
    status: str


class IngestionHistoryEntryResponse(BaseModel):
    date: str
    file: str
    type: str
    result: str
    details: str

    model_config = ConfigDict(from_attributes=True)

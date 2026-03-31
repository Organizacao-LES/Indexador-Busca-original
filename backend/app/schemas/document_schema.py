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
    extracted: bool
    extractedCharacters: int


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
    extractedCharacters: int


class IngestionBatchFileResponse(BaseModel):
    name: str
    size: str
    status: str


class BatchUploadItemResponse(BaseModel):
    fileName: str
    status: str
    message: str
    documentId: int | None = None
    extractedCharacters: int = 0
    sizeLabel: str | None = None


class BatchUploadResponse(BaseModel):
    totalFiles: int
    successCount: int
    failureCount: int
    items: list[BatchUploadItemResponse]


class IngestionHistoryEntryResponse(BaseModel):
    date: str
    file: str
    type: str
    result: str
    details: str

    model_config = ConfigDict(from_attributes=True)

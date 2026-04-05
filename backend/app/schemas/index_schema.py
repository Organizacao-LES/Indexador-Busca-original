from pydantic import BaseModel


class IndexLogEntryResponse(BaseModel):
    time: str
    message: str
    type: str


class IndexSummaryResponse(BaseModel):
    completed: int
    processing: int
    failed: int


class IndexStatusResponse(BaseModel):
    indexedDocuments: int
    averageTime: str
    successRate: str
    errors: int
    currentProgress: int
    remainingEstimate: str
    summary: IndexSummaryResponse
    logs: list[IndexLogEntryResponse]


class ReindexResponse(BaseModel):
    processedDocuments: int
    successCount: int
    failureCount: int
    message: str

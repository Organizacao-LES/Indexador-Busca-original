from pydantic import BaseModel


class SearchResultResponse(BaseModel):
    id: int
    title: str
    snippet: str
    category: str
    type: str
    date: str
    relevance: int


class SearchResponse(BaseModel):
    query: str
    total: int
    page: int
    perPage: int
    totalPages: int
    items: list[SearchResultResponse]


class SearchHistoryItemResponse(BaseModel):
    id: int
    term: str

from pydantic import BaseModel


class AdministrativeHistoryResponse(BaseModel):
    date: str
    user: str
    action: str
    details: str
    status: str

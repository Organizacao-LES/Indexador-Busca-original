from pydantic import BaseModel, Field


class AppSettingsResponse(BaseModel):
    instanceName: str = Field(min_length=1)
    apiBaseUrl: str = Field(min_length=1)
    autoIndexing: bool
    ocrEnabled: bool
    maxFileSizeMb: int = Field(ge=1, le=500)
    emailNotifications: bool
    weeklyReport: bool

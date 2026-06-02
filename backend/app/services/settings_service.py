from __future__ import annotations

from app.core.config import settings
from app.schemas.settings_schema import AppSettingsResponse


class SettingsService:
    def __init__(self) -> None:
        self._settings = AppSettingsResponse(
            instanceName="IFESDOC",
            apiBaseUrl="http://localhost:8000",
            autoIndexing=True,
            ocrEnabled=False,
            maxFileSizeMb=settings.DOCUMENT_MAX_FILE_SIZE_MB,
            emailNotifications=False,
            weeklyReport=True,
        )

    def get_settings(self) -> AppSettingsResponse:
        return self._settings

    def update_settings(self, payload: AppSettingsResponse) -> AppSettingsResponse:
        self._settings = payload
        return self._settings


settings_service = SettingsService()

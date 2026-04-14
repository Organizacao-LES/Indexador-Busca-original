from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.domain.user import User
from app.schemas.settings_schema import AppSettingsResponse
from app.services.settings_service import settings_service

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=AppSettingsResponse)
@router.get("/", response_model=AppSettingsResponse)
def get_settings(_: User = Depends(get_current_user)):
    return settings_service.get_settings()


@router.put("", response_model=AppSettingsResponse)
@router.put("/", response_model=AppSettingsResponse)
def update_settings(
    payload: AppSettingsResponse,
    _: User = Depends(get_current_user),
):
    return settings_service.update_settings(payload)

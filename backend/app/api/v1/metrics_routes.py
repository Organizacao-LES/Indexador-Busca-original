from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.domain.user import User
from app.domain.user_role import UserRole
from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("")
def get_metrics_snapshot(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    return metrics_service.snapshot(db)

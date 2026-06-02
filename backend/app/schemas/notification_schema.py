from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


NotificationType = Literal["info", "success", "warning", "error"]


class NotificationCreate(BaseModel):
    userId: int | None = None
    broadcast: bool = False
    title: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=2000)
    type: NotificationType = "info"

    @model_validator(mode="after")
    def validate_target(self):
        if not self.broadcast and self.userId is None:
            raise ValueError("Informe o usuário de destino ou habilite o envio para todos.")
        return self


class NotificationResponse(BaseModel):
    id: int
    userId: int
    title: str
    message: str
    type: NotificationType
    origin: str
    read: bool
    createdAt: datetime
    readAt: datetime | None = None


class NotificationUnreadCountResponse(BaseModel):
    unread: int

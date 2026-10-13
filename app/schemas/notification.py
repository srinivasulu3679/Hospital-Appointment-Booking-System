
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    appointment_id: int | None = Field(default=None, gt=0)
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=1)
    notification_type: str = Field(default="General", max_length=50)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    appointment_id: int | None
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationReadUpdate(BaseModel):
    is_read: bool = True

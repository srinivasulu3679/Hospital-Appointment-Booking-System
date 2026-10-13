
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmailLogCreate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    appointment_id: int | None = Field(default=None, gt=0)
    recipient_email: EmailStr
    subject: str = Field(..., min_length=1, max_length=255)
    status: str = Field(default="Pending", max_length=30)
    error_message: str | None = None


class EmailLogResponse(BaseModel):
    id: int
    user_id: int | None
    appointment_id: int | None
    recipient_email: EmailStr
    subject: str
    status: str
    error_message: str | None
    sent_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

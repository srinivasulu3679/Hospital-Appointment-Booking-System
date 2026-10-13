
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AppointmentReminderCreate(BaseModel):
    appointment_id: int = Field(..., gt=0)
    reminder_type: str = Field(default="Appointment Reminder", max_length=50)


class AppointmentReminderResponse(BaseModel):
    id: int
    appointment_id: int
    reminder_type: str
    status: str
    sent_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

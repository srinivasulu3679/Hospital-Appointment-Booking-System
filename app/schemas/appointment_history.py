
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AppointmentHistoryCreate(BaseModel):
    appointment_id: int = Field(..., gt=0)
    changed_by: int | None = Field(default=None, gt=0)
    old_status: str | None = Field(default=None, max_length=30)
    new_status: str = Field(..., min_length=2, max_length=30)
    remarks: str | None = None


class AppointmentHistoryResponse(BaseModel):
    id: int
    appointment_id: int
    changed_by: int | None
    old_status: str | None
    new_status: str
    remarks: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

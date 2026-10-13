
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DoctorQueueCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    appointment_id: int = Field(..., gt=0)
    token_number: int = Field(..., gt=0)


class DoctorQueueStatusUpdate(BaseModel):
    status: Literal["Waiting", "In Progress", "Completed", "Skipped"]


class DoctorQueueResponse(BaseModel):
    id: int
    doctor_id: int
    appointment_id: int
    token_number: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

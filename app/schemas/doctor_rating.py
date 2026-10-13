
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DoctorRatingCreate(BaseModel):
    appointment_id: int = Field(..., gt=0)
    doctor_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    review: str | None = Field(default=None, max_length=2000)


class DoctorRatingResponse(BaseModel):
    id: int
    appointment_id: int
    doctor_id: int
    patient_id: int
    rating: int
    review: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

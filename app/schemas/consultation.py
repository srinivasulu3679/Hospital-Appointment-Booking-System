
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsultationCreate(BaseModel):
    appointment_id: int = Field(..., gt=0)
    doctor_id: int = Field(..., gt=0)
    patient_id: int = Field(..., gt=0)
    symptoms: str | None = None
    diagnosis: str = Field(..., min_length=2)
    treatment_notes: str | None = None
    follow_up_notes: str | None = None


class ConsultationUpdate(BaseModel):
    symptoms: str | None = None
    diagnosis: str | None = Field(default=None, min_length=2)
    treatment_notes: str | None = None
    follow_up_notes: str | None = None


class ConsultationResponse(BaseModel):
    id: int
    appointment_id: int
    doctor_id: int
    patient_id: int
    symptoms: str | None
    diagnosis: str
    treatment_notes: str | None
    follow_up_notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

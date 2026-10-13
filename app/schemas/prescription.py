
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PrescriptionCreate(BaseModel):
    consultation_id: int = Field(..., gt=0)
    patient_id: int = Field(..., gt=0)
    medicines: str = Field(..., min_length=2)
    instructions: str | None = None


class PrescriptionUpdate(BaseModel):
    medicines: str | None = Field(default=None, min_length=2)
    instructions: str | None = None


class PrescriptionResponse(BaseModel):
    id: int
    consultation_id: int
    doctor_id: int
    patient_id: int
    medicines: str
    instructions: str | None
    pdf_path: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

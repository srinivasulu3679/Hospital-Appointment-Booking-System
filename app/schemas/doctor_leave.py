
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DoctorLeaveCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    start_date: date
    end_date: date
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
        return self


class DoctorLeaveResponse(BaseModel):
    id: int
    doctor_id: int
    start_date: date
    end_date: date
    reason: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

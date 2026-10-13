
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DoctorAvailabilityCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    available_date: date
    start_time: time
    end_time: time
    is_available: bool = True

    @model_validator(mode="after")
    def validate_times(self):
        if self.available_date < date.today():
            raise ValueError("Availability date cannot be in the past")
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class DoctorAvailabilityUpdate(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    is_available: bool | None = None


class DoctorAvailabilityResponse(BaseModel):
    id: int
    doctor_id: int
    available_date: date
    start_time: time
    end_time: time
    is_available: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

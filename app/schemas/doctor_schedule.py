
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DoctorScheduleCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    break_start: time | None = None
    break_end: time | None = None
    slot_duration_minutes: int = Field(default=30, ge=5, le=240)

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")

        if (self.break_start is None) != (self.break_end is None):
            raise ValueError("Both break_start and break_end must be provided")

        if self.break_start is not None and self.break_end is not None:
            if not (
                self.start_time <= self.break_start
                < self.break_end <= self.end_time
            ):
                raise ValueError("Break must be within the schedule")

        return self


class DoctorScheduleResponse(BaseModel):
    id: int
    doctor_id: int
    day_of_week: int
    start_time: time
    end_time: time
    break_start: time | None
    break_end: time | None
    slot_duration_minutes: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

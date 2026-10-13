
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    appointment_date: date
    appointment_time: time

    @model_validator(mode="after")
    def validate_appointment_date(self):
        if self.appointment_date < date.today():
            raise ValueError("Appointment date cannot be in the past")
        return self


class AppointmentStatusUpdate(BaseModel):
    status: Literal[
        "Booked",
        "Confirmed",
        "Completed",
        "Cancelled",
        "No Show",
    ]
    cancellation_reason: str | None = Field(default=None, max_length=500)


class AppointmentReschedule(BaseModel):
    appointment_date: date
    appointment_time: time

    @model_validator(mode="after")
    def validate_appointment_date(self):
        if self.appointment_date < date.today():
            raise ValueError("Appointment date cannot be in the past")
        return self


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    consultation_fee: float
    status: str
    token_number: int | None
    reschedule_count: int
    cancellation_reason: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

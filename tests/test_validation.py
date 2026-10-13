import pytest
from pydantic import ValidationError

from app.schemas.appointment import AppointmentCreate
from app.schemas.doctor_schedule import DoctorScheduleCreate
from app.schemas.doctor_rating import DoctorRatingCreate


def test_appointment_date_cannot_be_in_the_past():
    with pytest.raises(ValidationError):
        AppointmentCreate(
            doctor_id=1,
            appointment_date="2020-01-01",
            appointment_time="10:00:00",
        )


def test_schedule_day_of_week_must_be_valid():
    with pytest.raises(ValidationError):
        DoctorScheduleCreate(
            doctor_id=1,
            day_of_week=8,
            start_time="09:00:00",
            end_time="17:00:00",
            slot_duration_minutes=30,
        )


def test_rating_must_be_between_one_and_five():
    with pytest.raises(ValidationError):
        DoctorRatingCreate(
            appointment_id=1,
            rating=6,
            review="Test review",
        )

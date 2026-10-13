
from datetime import date, datetime, time, timezone

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now():
    """Return current UTC time as a naive datetime for database compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "appointment_date",
            "appointment_time",
            name="uq_doctor_appointment_slot",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"), nullable=False, index=True
    )

    appointment_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )
    appointment_time: Mapped[time] = mapped_column(
        Time, nullable=False
    )

    consultation_fee: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default="Booked", nullable=False, index=True
    )
    token_number: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    reschedule_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    cancellation_reason: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    patient = relationship("User")
    doctor = relationship("Doctor")

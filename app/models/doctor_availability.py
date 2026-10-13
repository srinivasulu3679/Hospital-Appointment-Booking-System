
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "available_date",
            "start_time",
            name="uq_doctor_availability_slot",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"), nullable=False, index=True
    )
    available_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    doctor = relationship("Doctor")

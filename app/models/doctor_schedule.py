
from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"), nullable=False, index=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    break_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    slot_duration_minutes: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    doctor = relationship("Doctor")

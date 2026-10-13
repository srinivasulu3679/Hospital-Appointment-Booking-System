
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AppointmentReminder(Base):
    __tablename__ = "appointment_reminders"

    __table_args__ = (
        UniqueConstraint(
            "appointment_id",
            "reminder_type",
            name="uq_appointment_reminder_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"), nullable=False, index=True
    )

    reminder_type: Mapped[str] = mapped_column(
        String(50), default="Appointment Reminder", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default="Pending", nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    appointment = relationship("Appointment")

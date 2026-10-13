
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DoctorQueue(Base):
    __tablename__ = "doctor_queue"

    __table_args__ = (
        UniqueConstraint(
            "appointment_id",
            name="uq_doctor_queue_appointment",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"), nullable=False, index=True
    )
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"), nullable=False, index=True
    )

    token_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="Waiting", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    doctor = relationship("Doctor")
    appointment = relationship("Appointment")

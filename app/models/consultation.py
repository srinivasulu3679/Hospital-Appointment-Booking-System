
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"), unique=True, nullable=False
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"), nullable=False, index=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)
    treatment_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    appointment = relationship("Appointment")
    doctor = relationship("Doctor")
    patient = relationship("User")

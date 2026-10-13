
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DoctorRating(Base):
    __tablename__ = "doctor_ratings"

    __table_args__ = (
        UniqueConstraint(
            "appointment_id",
            name="uq_doctor_rating_appointment",
        ),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"), nullable=False
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"), nullable=False, index=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    appointment = relationship("Appointment")
    doctor = relationship("Doctor")
    patient = relationship("User")

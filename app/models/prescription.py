
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    consultation_id: Mapped[int] = mapped_column(
        ForeignKey("consultations.id"), nullable=False, index=True
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"), nullable=False, index=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    medicines: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    consultation = relationship("Consultation")
    doctor = relationship("Doctor")
    patient = relationship("User")


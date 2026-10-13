
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AppointmentHistory(Base):
    __tablename__ = "appointment_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"), nullable=False, index=True
    )
    changed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    old_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    appointment = relationship("Appointment")
    user = relationship("User")


from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False, index=True
    )

    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[str] = mapped_column(String(200), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consultation_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    department = relationship("Department", back_populates="doctors")
    user = relationship("User")

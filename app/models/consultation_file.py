
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConsultationFile(Base):
    __tablename__ = "consultation_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultation_id: Mapped[int] = mapped_column(
        ForeignKey("consultations.id"), nullable=False, index=True
    )
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    consultation = relationship("Consultation")
    uploader = relationship("User")

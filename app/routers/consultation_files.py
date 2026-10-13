
import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.consultation import Consultation
from app.models.consultation_file import ConsultationFile
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.consultation_file import ConsultationFileResponse

router = APIRouter(
    prefix="/consultation-files",
    tags=["Consultation Files"],
)

UPLOAD_DIR = "uploads/consultations"
ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/{consultation_id}", response_model=ConsultationFileResponse, status_code=201)
def upload_consultation_file(
    consultation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Doctor", "Admin")),
):
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor or doctor.id != consultation.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG, and PNG files are allowed",
        )

    content = file.file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 5 MB",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    original_name = os.path.basename(file.filename or "upload")
    extension = os.path.splitext(original_name)[1].lower()

    stored_name = f"{uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)

    try:
        with open(file_path, "wb") as output:
            output.write(content)

        record = ConsultationFile(
            consultation_id=consultation.id,
            uploaded_by=current_user.id,
            original_filename=original_name,
            stored_filename=stored_name,
            file_path=file_path,
            content_type=file.content_type,
            file_size=len(content),
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    except Exception:
        db.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        raise


@router.get("/{consultation_id}", response_model=list[ConsultationFileResponse])
def list_consultation_files(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if current_user.role == "Patient" and consultation.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor or doctor.id != consultation.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return db.query(ConsultationFile).filter(
        ConsultationFile.consultation_id == consultation_id
    ).order_by(ConsultationFile.created_at.desc()).all()

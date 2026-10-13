from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.consultation import Consultation
from app.models.doctor import Doctor
from app.models.prescription import Prescription
from app.models.user import User
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionResponse,
)

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


def get_doctor_profile(db: Session, user_id: int):
    return db.query(Doctor).filter(Doctor.user_id == user_id).first()


@router.post("/", response_model=PrescriptionResponse, status_code=201)
def create_prescription(
    data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Doctor", "Admin")),
):
    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == data.consultation_id)
        .first()
    )

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        if not doctor or doctor.id != consultation.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    existing = (
        db.query(Prescription)
        .filter(Prescription.consultation_id == consultation.id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Prescription already exists for this consultation",
        )

    prescription = Prescription(
        consultation_id=consultation.id,
        doctor_id=consultation.doctor_id,
        patient_id=consultation.patient_id,
        medicines=data.medicines,
        instructions=data.instructions,
    )

    try:
        db.add(prescription)
        db.commit()
        db.refresh(prescription)
        return prescription
    except Exception:
        db.rollback()
        raise


@router.get("/", response_model=list[PrescriptionResponse])
def list_prescriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Prescription)

    if current_user.role == "Patient":
        query = query.filter(Prescription.patient_id == current_user.id)

    elif current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        if not doctor:
            return []
        query = query.filter(Prescription.doctor_id == doctor.id)

    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return query.order_by(Prescription.created_at.desc()).all()


@router.get("/my", response_model=list[PrescriptionResponse])
def list_my_prescriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Prescription)

    if current_user.role == "Patient":
        query = query.filter(Prescription.patient_id == current_user.id)

    elif current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        if not doctor:
            return []
        query = query.filter(Prescription.doctor_id == doctor.id)

    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return query.order_by(Prescription.created_at.desc()).all()


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prescription = (
        db.query(Prescription)
        .filter(Prescription.id == prescription_id)
        .first()
    )

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    if current_user.role == "Patient":
        if prescription.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        if not doctor or doctor.id != prescription.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return prescription


@router.patch("/{prescription_id}", response_model=PrescriptionResponse)
def update_prescription(
    prescription_id: int,
    data: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Doctor", "Admin")),
):
    prescription = (
        db.query(Prescription)
        .filter(Prescription.id == prescription_id)
        .first()
    )

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    if current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        if not doctor or doctor.id != prescription.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prescription, field, value)

    try:
        db.commit()
        db.refresh(prescription)
        return prescription
    except Exception:
        db.rollback()
        raise
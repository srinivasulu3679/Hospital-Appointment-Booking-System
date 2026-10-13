from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.appointment import Appointment
from app.models.consultation import Consultation
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.consultation import (
    ConsultationCreate,
    ConsultationUpdate,
    ConsultationResponse,
)

router = APIRouter(prefix="/consultations", tags=["Consultations"])


def get_doctor_profile(db: Session, user_id: int):
    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return doctor


@router.post("/", response_model=ConsultationResponse, status_code=201)
def create_consultation(
    data: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Doctor", "Admin")),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == data.appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status != "Completed":
        raise HTTPException(
            status_code=400,
            detail="Consultation can be created only for completed appointments",
        )

    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()

    if current_user.role == "Doctor":
        if not doctor or doctor.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can manage consultations only for your appointments",
            )

    existing = (
        db.query(Consultation)
        .filter(Consultation.appointment_id == appointment.id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Consultation already exists for this appointment",
        )

    consultation = Consultation(
        appointment_id=appointment.id,
        doctor_id=appointment.doctor_id,
        patient_id=appointment.patient_id,
        symptoms=data.symptoms,
        diagnosis=data.diagnosis,
        treatment_notes=data.treatment_notes,
        follow_up_notes=data.follow_up_notes,
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


@router.get("/", response_model=list[ConsultationResponse])
def list_consultations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Consultation)

    if current_user.role == "Patient":
        query = query.filter(Consultation.patient_id == current_user.id)

    elif current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        query = query.filter(Consultation.doctor_id == doctor.id)

    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return query.order_by(Consultation.created_at.desc()).all()


@router.get("/my", response_model=list[ConsultationResponse])
def list_my_consultations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Consultation)

    if current_user.role == "Patient":
        query = query.filter(Consultation.patient_id == current_user.id)

    elif current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        query = query.filter(Consultation.doctor_id == doctor.id)

    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return query.order_by(Consultation.created_at.desc()).all()


@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .first()
    )

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if current_user.role == "Patient":
        if consultation.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        if consultation.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return consultation


@router.patch("/{consultation_id}", response_model=ConsultationResponse)
def update_consultation(
    consultation_id: int,
    data: ConsultationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Doctor", "Admin")),
):
    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .first()
    )

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if current_user.role == "Doctor":
        doctor = get_doctor_profile(db, current_user.id)
        if consultation.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Access denied")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(consultation, field, value)

    db.commit()
    db.refresh(consultation)
    return consultation
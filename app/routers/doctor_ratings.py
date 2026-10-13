
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.doctor_rating import DoctorRating
from app.models.user import User
from app.schemas.doctor_rating import (
    DoctorRatingCreate,
    DoctorRatingResponse,
)

router = APIRouter(prefix="/doctor-ratings", tags=["Doctor Ratings"])


@router.post("/", response_model=DoctorRatingResponse, status_code=201)
def create_doctor_rating(
    data: DoctorRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "Patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can submit doctor ratings",
        )

    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id,
        Appointment.patient_id == current_user.id,
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Your appointment was not found",
        )

    if appointment.status != "Completed":
        raise HTTPException(
            status_code=400,
            detail="You can rate a doctor only after a completed appointment",
        )

    existing = db.query(DoctorRating).filter(
        DoctorRating.appointment_id == appointment.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="You have already rated this appointment",
        )

    rating = DoctorRating(
        appointment_id=appointment.id,
        doctor_id=appointment.doctor_id,
        patient_id=current_user.id,
        rating=data.rating,
        review=data.review,
    )

    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.get("/doctor/{doctor_id}", response_model=list[DoctorRatingResponse])
def list_doctor_ratings(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return db.query(DoctorRating).filter(
        DoctorRating.doctor_id == doctor_id
    ).order_by(DoctorRating.created_at.desc()).all()


@router.get("/my", response_model=list[DoctorRatingResponse])
def list_my_ratings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "Patient":
        return db.query(DoctorRating).filter(
            DoctorRating.patient_id == current_user.id
        ).order_by(DoctorRating.created_at.desc()).all()

    if current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor:
            return []

        return db.query(DoctorRating).filter(
            DoctorRating.doctor_id == doctor.id
        ).order_by(DoctorRating.created_at.desc()).all()

    return db.query(DoctorRating).order_by(
        DoctorRating.created_at.desc()
    ).all()

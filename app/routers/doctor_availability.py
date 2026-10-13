
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.doctor import Doctor
from app.models.doctor_availability import DoctorAvailability
from app.models.user import User
from app.schemas.doctor_availability import (
    DoctorAvailabilityCreate,
    DoctorAvailabilityUpdate,
    DoctorAvailabilityResponse,
)

router = APIRouter(
    prefix="/doctor-availability",
    tags=["Doctor Availability"],
)


@router.post("/", response_model=DoctorAvailabilityResponse, status_code=201)
def create_availability(
    data: DoctorAvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "Doctor")),
):
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Active doctor not found")

    if current_user.role == "Doctor" and doctor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can manage only your availability")

    if data.available_date < date.today():
        raise HTTPException(status_code=400, detail="Availability date cannot be in the past")

    if data.start_time >= data.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    availability = DoctorAvailability(**data.model_dump())
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return availability


@router.get("/{doctor_id}", response_model=list[DoctorAvailabilityResponse])
def list_availability(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.available_date >= date.today(),
        DoctorAvailability.is_available.is_(True),
    ).order_by(
        DoctorAvailability.available_date,
        DoctorAvailability.start_time,
    ).all()


@router.patch("/{availability_id}", response_model=DoctorAvailabilityResponse)
def update_availability(
    availability_id: int,
    data: DoctorAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "Doctor")),
):
    availability = db.query(DoctorAvailability).filter(
        DoctorAvailability.id == availability_id
    ).first()

    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")

    if current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor or doctor.id != availability.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    changes = data.model_dump(exclude_unset=True)
    new_start = changes.get("start_time", availability.start_time)
    new_end = changes.get("end_time", availability.end_time)

    if new_start >= new_end:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    for field, value in changes.items():
        setattr(availability, field, value)

    db.commit()
    db.refresh(availability)
    return availability

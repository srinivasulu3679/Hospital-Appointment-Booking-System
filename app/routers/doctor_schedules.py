
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.schemas.doctor_schedule import (
    DoctorScheduleCreate,
    DoctorScheduleResponse,
)
from app.auth.dependencies import require_roles

router = APIRouter(
    prefix="/doctor-schedules",
    tags=["Doctor Schedules"],
)


@router.post("/", response_model=DoctorScheduleResponse, status_code=201)
def create_schedule(
    data: DoctorScheduleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin", "Doctor")),
):
    if current_user.role == "Doctor":
        own_doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not own_doctor or own_doctor.id != data.doctor_id:
            raise HTTPException(
                status_code=403,
                detail="You can manage only your own schedule",
            )

    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Active doctor not found")

    existing = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == data.doctor_id,
        DoctorSchedule.day_of_week == data.day_of_week,
        DoctorSchedule.is_active.is_(True),
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An active schedule already exists for this day",
        )

    schedule = DoctorSchedule(**data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/{doctor_id}", response_model=list[DoctorScheduleResponse])
def get_doctor_schedules(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.is_active.is_(True),
    ).order_by(DoctorSchedule.day_of_week).all()

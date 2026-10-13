
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.doctor_queue import DoctorQueue
from app.models.user import User
from app.schemas.doctor_queue import (
    DoctorQueueCreate,
    DoctorQueueStatusUpdate,
    DoctorQueueResponse,
)

router = APIRouter(prefix="/doctor-queue", tags=["Doctor Queue"])


@router.post("/", response_model=DoctorQueueResponse, status_code=201)
def add_to_queue(
    data: DoctorQueueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "Doctor")),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status not in ("Booked", "Confirmed"):
        raise HTTPException(
            status_code=400,
            detail="Only booked or confirmed appointments can enter the queue",
        )

    if current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor or doctor.id != appointment.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    existing = db.query(DoctorQueue).filter(
        DoctorQueue.appointment_id == appointment.id
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Appointment is already in the queue")

    queue_entry = DoctorQueue(
        doctor_id=appointment.doctor_id,
        appointment_id=appointment.id,
        token_number=data.token_number,
        status="Waiting",
    )

    db.add(queue_entry)
    db.commit()
    db.refresh(queue_entry)
    return queue_entry


@router.get("/doctor/{doctor_id}", response_model=list[DoctorQueueResponse])
def get_doctor_queue(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor or doctor.id != doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    if current_user.role == "Patient":
        raise HTTPException(
            status_code=403,
            detail="Patients cannot view the entire doctor queue",
        )

    return db.query(DoctorQueue).filter(
        DoctorQueue.doctor_id == doctor_id,
        DoctorQueue.status.in_(["Waiting", "In Progress"]),
    ).order_by(DoctorQueue.token_number.asc()).all()


@router.patch("/{queue_id}/status", response_model=DoctorQueueResponse)
def update_queue_status(
    queue_id: int,
    data: DoctorQueueStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "Doctor")),
):
    queue_entry = db.query(DoctorQueue).filter(
        DoctorQueue.id == queue_id
    ).first()

    if not queue_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    if current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor or doctor.id != queue_entry.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    queue_entry.status = data.status
    db.commit()
    db.refresh(queue_entry)
    return queue_entry

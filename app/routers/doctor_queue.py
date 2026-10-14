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
from app.utils.connection_manager import manager

router = APIRouter(prefix="/doctor-queue", tags=["Doctor Queue"])


def verify_doctor_access(
    doctor_id: int,
    current_user: User,
    db: Session,
):
    if current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor or doctor.id != doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role not in ("Admin", "Doctor"):
        raise HTTPException(status_code=403, detail="Access denied")


@router.post("/", response_model=DoctorQueueResponse, status_code=201)
async def add_to_queue(
    data: DoctorQueueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "Doctor")),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    verify_doctor_access(appointment.doctor_id, current_user, db)

    if data.doctor_id != appointment.doctor_id:
        raise HTTPException(
            status_code=400,
            detail="Doctor does not match the appointment",
        )

    if appointment.status not in ("Booked", "Confirmed"):
        raise HTTPException(
            status_code=400,
            detail="Only booked or confirmed appointments can enter the queue",
        )

    existing = db.query(DoctorQueue).filter(
        DoctorQueue.appointment_id == appointment.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Appointment is already in the queue",
        )

    duplicate_token = db.query(DoctorQueue).filter(
        DoctorQueue.doctor_id == appointment.doctor_id,
        DoctorQueue.token_number == data.token_number,
        DoctorQueue.status.in_(["Waiting", "In Progress"]),
    ).first()

    if duplicate_token:
        raise HTTPException(
            status_code=409,
            detail="Token number is already active for this doctor",
        )

    queue_entry = DoctorQueue(
        doctor_id=appointment.doctor_id,
        appointment_id=appointment.id,
        token_number=data.token_number,
        status="Waiting",
    )

    try:
        db.add(queue_entry)
        db.commit()
        db.refresh(queue_entry)
    except Exception:
        db.rollback()
        raise

    await manager.send_to_user(
        appointment.patient_id,
        {
            "event": "queue_updated",
            "message": "You have been added to the doctor queue",
            "queue_id": queue_entry.id,
            "token_number": queue_entry.token_number,
            "status": queue_entry.status,
        },
    )

    doctor = db.query(Doctor).filter(
        Doctor.id == appointment.doctor_id
    ).first()

    if doctor:
        await manager.send_to_user(
            doctor.user_id,
            {
                "event": "queue_updated",
                "queue_id": queue_entry.id,
                "token_number": queue_entry.token_number,
                "status": queue_entry.status,
            },
        )

    return queue_entry


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[DoctorQueueResponse],
)
def get_doctor_queue(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_doctor_access(doctor_id, current_user, db)

    return db.query(DoctorQueue).filter(
        DoctorQueue.doctor_id == doctor_id,
        DoctorQueue.status.in_(["Waiting", "In Progress"]),
    ).order_by(DoctorQueue.token_number.asc()).all()


@router.post(
    "/doctor/{doctor_id}/call-next",
    response_model=DoctorQueueResponse,
)
async def call_next_patient(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "Doctor")),
):
    verify_doctor_access(doctor_id, current_user, db)

    in_progress = db.query(DoctorQueue).filter(
        DoctorQueue.doctor_id == doctor_id,
        DoctorQueue.status == "In Progress",
    ).first()

    if in_progress:
        raise HTTPException(
            status_code=409,
            detail="A patient is already in progress",
        )

    next_patient = db.query(DoctorQueue).filter(
        DoctorQueue.doctor_id == doctor_id,
        DoctorQueue.status == "Waiting",
    ).order_by(
        DoctorQueue.token_number.asc(),
        DoctorQueue.id.asc(),
    ).with_for_update().first()

    if not next_patient:
        raise HTTPException(
            status_code=404,
            detail="No patients are waiting in the queue",
        )

    next_patient.status = "In Progress"

    try:
        db.commit()
        db.refresh(next_patient)
    except Exception:
        db.rollback()
        raise

    appointment = db.query(Appointment).filter(
        Appointment.id == next_patient.appointment_id
    ).first()

    if appointment:
        await manager.send_to_user(
            appointment.patient_id,
            {
                "event": "patient_called",
                "message": "It is your turn. Please proceed to the doctor.",
                "queue_id": next_patient.id,
                "token_number": next_patient.token_number,
                "status": next_patient.status,
            },
        )

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor:
        await manager.send_to_user(
            doctor.user_id,
            {
                "event": "queue_updated",
                "queue_id": next_patient.id,
                "token_number": next_patient.token_number,
                "status": next_patient.status,
            },
        )

    return next_patient


@router.patch("/{queue_id}/status", response_model=DoctorQueueResponse)
async def update_queue_status(
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

    verify_doctor_access(queue_entry.doctor_id, current_user, db)

    allowed_transitions = {
        "Waiting": {"In Progress", "Skipped"},
        "In Progress": {"Completed", "Skipped"},
        "Completed": set(),
        "Skipped": set(),
    }

    if data.status not in allowed_transitions.get(queue_entry.status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change queue status from {queue_entry.status} to {data.status}",
        )

    queue_entry.status = data.status

    try:
        db.commit()
        db.refresh(queue_entry)
    except Exception:
        db.rollback()
        raise

    appointment = db.query(Appointment).filter(
        Appointment.id == queue_entry.appointment_id
    ).first()

    if appointment:
        await manager.send_to_user(
            appointment.patient_id,
            {
                "event": "queue_updated",
                "queue_id": queue_entry.id,
                "token_number": queue_entry.token_number,
                "status": queue_entry.status,
            },
        )

    doctor = db.query(Doctor).filter(
        Doctor.id == queue_entry.doctor_id
    ).first()

    if doctor:
        await manager.send_to_user(
            doctor.user_id,
            {
                "event": "queue_updated",
                "queue_id": queue_entry.id,
                "token_number": queue_entry.token_number,
                "status": queue_entry.status,
            },
        )

    return queue_entry
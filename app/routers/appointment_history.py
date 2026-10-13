
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.appointment import Appointment
from app.models.appointment_history import AppointmentHistory
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.appointment_history import AppointmentHistoryResponse

router = APIRouter(
    prefix="/appointment-history",
    tags=["Appointment History"],
)


@router.get("/{appointment_id}", response_model=list[AppointmentHistoryResponse])
def get_appointment_history(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role == "Patient":
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor or doctor.id != appointment.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return db.query(AppointmentHistory).filter(
        AppointmentHistory.appointment_id == appointment_id
    ).order_by(AppointmentHistory.created_at.desc()).all()

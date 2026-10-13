from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.appointment_reminder import AppointmentReminder

router = APIRouter(
    prefix="/appointment-reminders",
    tags=["Appointment Reminders"],
)


@router.get("/")
def list_appointment_reminders(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return (
        db.query(AppointmentReminder)
        .order_by(AppointmentReminder.created_at.desc())
        .all()
    )

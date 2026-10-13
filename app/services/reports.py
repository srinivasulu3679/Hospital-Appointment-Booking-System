
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.doctor import Doctor
from app.models.user import User
from app.services.report_service import (
    get_dashboard_report,
    get_doctor_appointment_report,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard")
def dashboard_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin")),
):
    return get_dashboard_report(db)


@router.get("/doctors/{doctor_id}/appointments")
def doctor_appointment_report(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin")),
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return get_doctor_appointment_report(db, doctor_id)

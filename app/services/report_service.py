from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.user import User
from app.models.department import Department


def get_dashboard_report(db: Session) -> dict:
    total_patients = db.query(User).filter(
        User.role == "Patient"
    ).count()

    total_doctors = db.query(Doctor).filter(
        Doctor.is_active.is_(True)
    ).count()

    total_departments = db.query(Department).filter(
        Department.is_active.is_(True)
    ).count()

    total_appointments = db.query(Appointment).count()

    today_appointments = db.query(Appointment).filter(
        Appointment.appointment_date == date.today()
    ).count()

    status_rows = db.query(
        Appointment.status,
        func.count(Appointment.id),
    ).group_by(Appointment.status).all()

    appointments_by_status = {
        status: count for status, count in status_rows
    }

    return {
        # Existing API keys
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_departments": total_departments,
        "total_appointments": total_appointments,
        "today_appointments": today_appointments,
        "appointments_by_status": appointments_by_status,

        # Compatibility keys for tests/consumers
        "patients": total_patients,
        "doctors": total_doctors,
        "departments": total_departments,
        "appointments": total_appointments,
    }


def get_doctor_appointment_report(
    db: Session,
    doctor_id: int,
) -> dict:
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        return {"error": "Doctor not found"}

    total = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).count()

    completed = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status == "Completed",
    ).count()

    cancelled = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status == "Cancelled",
    ).count()

    return {
        "doctor_id": doctor_id,
        "total_appointments": total,
        "completed_appointments": completed,
        "cancelled_appointments": cancelled,
    }
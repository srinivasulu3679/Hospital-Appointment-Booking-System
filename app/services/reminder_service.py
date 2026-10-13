
from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.appointment_reminder import AppointmentReminder


def create_upcoming_reminders(db: Session) -> int:
    today = date.today()
    tomorrow = today + timedelta(days=1)

    appointments = db.query(Appointment).filter(
        Appointment.appointment_date == tomorrow,
        Appointment.status.in_(["Booked", "Confirmed"]),
    ).all()

    created_count = 0

    for appointment in appointments:
        existing = db.query(AppointmentReminder).filter(
            AppointmentReminder.appointment_id == appointment.id,
            AppointmentReminder.reminder_type == "One Day Before",
        ).first()

        if existing:
            continue

        reminder = AppointmentReminder(
            appointment_id=appointment.id,
            reminder_type="One Day Before",
            status="Pending",
        )

        db.add(reminder)
        created_count += 1

    db.commit()
    return created_count


def get_pending_reminders(db: Session):
    return db.query(AppointmentReminder).join(
        Appointment,
        Appointment.id == AppointmentReminder.appointment_id,
    ).filter(
        AppointmentReminder.status == "Pending",
        Appointment.appointment_date >= date.today(),
        Appointment.status.in_(["Booked", "Confirmed"]),
    ).all()


def mark_reminder_sent(db: Session, reminder: AppointmentReminder) -> None:
    reminder.status = "Sent"
    reminder.sent_at = datetime.now()
    db.commit()

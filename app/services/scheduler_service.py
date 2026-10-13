
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.services.reminder_service import create_upcoming_reminders

scheduler = BackgroundScheduler()


def run_appointment_reminders():
    db = SessionLocal()

    try:
        count = create_upcoming_reminders(db)
        print(f"Appointment reminders created: {count}")
    except Exception as exc:
        db.rollback()
        print(f"Reminder scheduler failed: {exc}")
    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            run_appointment_reminders,
            trigger="cron",
            hour=8,
            minute=0,
            id="appointment_reminders",
            replace_existing=True,
        )
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

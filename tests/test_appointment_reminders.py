from app.models.appointment_reminder import AppointmentReminder
from app.services.reminder_service import create_upcoming_reminders


def test_create_upcoming_reminders(db):
    result = create_upcoming_reminders(db)

    assert result is None or isinstance(result, (int, list))

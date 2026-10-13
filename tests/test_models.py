from app.models import (
    User,
    Department,
    Doctor,
    Appointment,
    Notification,
    AuditLog,
)


def test_all_models_are_registered():
    expected_tables = {
        "users",
        "departments",
        "doctors",
        "appointments",
        "notifications",
        "audit_logs",
    }

    actual_tables = set(User.metadata.tables.keys())

    assert expected_tables.issubset(actual_tables)


def test_user_model_has_expected_fields():
    assert hasattr(User, "email")
    assert hasattr(User, "hashed_password")
    assert hasattr(User, "role")
    assert hasattr(User, "is_active")


def test_appointment_model_has_expected_fields():
    assert hasattr(Appointment, "doctor_id")
    assert hasattr(Appointment, "patient_id")
    assert hasattr(Appointment, "appointment_date")
    assert hasattr(Appointment, "status")

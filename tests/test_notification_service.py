from app.models.notification import Notification
from app.models.user import User
from app.services.notification_service import create_notification


def test_create_notification(db):
    # Create a test user first
    user = User(
        full_name="Test Patient",
        email="notification.test@example.com",
        hashed_password="test_hash",
        role="Patient",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    notification = create_notification(
        db=db,
        user_id=user.id,
        title="Test Notification",
        message="Appointment reminder test",
        notification_type="General",
    )

    db.commit()

    saved_notification = (
        db.query(Notification)
        .filter(Notification.title == "Test Notification")
        .first()
    )

    assert saved_notification is not None
    assert saved_notification.user_id == user.id
    assert saved_notification.message == "Appointment reminder test"
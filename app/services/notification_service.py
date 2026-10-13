from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "General",
    appointment_id: int | None = None,
) -> Notification:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    notification = Notification(
        user_id=user_id,
        appointment_id=appointment_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_read=False,
    )

    db.add(notification)
    db.flush()

    return notification


def get_unread_count(db: Session, user_id: int) -> int:
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read.is_(False),
    ).count()


def mark_all_as_read(db: Session, user_id: int) -> int:
    updated_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read.is_(False),
    ).update(
        {Notification.is_read: True},
        synchronize_session=False,
    )

    db.flush()
    return updated_count

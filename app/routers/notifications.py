
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationReadUpdate,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )

    if unread_only:
        query = query.filter(Notification.is_read.is_(False))

    return query.order_by(Notification.created_at.desc()).all()


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    data: NotificationReadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    notification.is_read = data.is_read
    db.commit()
    db.refresh(notification)
    return notification


@router.patch("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    ).update(
        {Notification.is_read: True},
        synchronize_session=False,
    )

    db.commit()
    return {"message": "All notifications marked as read"}

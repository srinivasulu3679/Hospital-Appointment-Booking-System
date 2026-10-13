from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.email_log import EmailLog

router = APIRouter(
    prefix="/email-logs",
    tags=["Email Logs"],
)


@router.get("/")
def list_email_logs(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return (
        db.query(EmailLog)
        .order_by(EmailLog.created_at.desc())
        .all()
    )

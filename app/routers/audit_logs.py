
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=list[AuditLogResponse])
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin")),
):
    limit = max(1, min(limit, 200))
    skip = max(0, skip)

    return db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).offset(skip).limit(limit).all()


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin")),
):
    from fastapi import HTTPException

    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return log

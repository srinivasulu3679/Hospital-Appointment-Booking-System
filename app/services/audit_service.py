
import json

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    user_id: int | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details or {}, default=str),
        ip_address=ip_address,
    )

    db.add(log)
    db.flush()

    return log


def list_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
):
    safe_skip = max(0, skip)
    safe_limit = max(1, min(limit, 200))

    return db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).offset(safe_skip).limit(safe_limit).all()

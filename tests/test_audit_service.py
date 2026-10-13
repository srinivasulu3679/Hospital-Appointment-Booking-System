from app.models.audit_log import AuditLog
from app.services.audit_service import create_audit_log


def test_create_audit_log(db):
    log = create_audit_log(
        db=db,
        action="TEST_ACTION",
        entity_type="TestEntity",
        entity_id=1,
        details={"message": "Test audit log"},
    )

    db.commit()

    saved_log = db.query(AuditLog).filter(
        AuditLog.action == "TEST_ACTION"
    ).first()

    assert saved_log is not None
    assert saved_log.entity_type == "TestEntity"

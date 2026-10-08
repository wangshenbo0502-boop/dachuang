from sqlalchemy.orm import Session
from ..models import AdminAuditLog


def record(db: Session, admin_id, action: str, *, target_type="", target_id=None, result="success", detail=None,
           command_id=None, event_kind="local"):
    db.add(AdminAuditLog(actor_id=admin_id, action=action, target_type=target_type,
                         target_id=str(target_id) if target_id is not None else None, result=result, detail=detail or {},
                         command_id=command_id, event_kind=event_kind))

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .db import get_db
from .dependencies import require_permission
from .errors import envelope
from .models import AdminAuditLog

router = APIRouter(tags=["audit"])


@router.get("/audit-logs")
def audit(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), actor_id: str = "",
          action: str = "", resource_type: str = "", resource_id: str = "", outcome: str = "",
          from_time: datetime | None = Query(None, alias="from"), to_time: datetime | None = Query(None, alias="to"),
          admin=Depends(require_permission("audit:read")), db: Session = Depends(get_db)):
    stmt = select(AdminAuditLog)
    for field, value in (("actor_id", actor_id), ("action", action), ("target_type", resource_type),
                         ("target_id", resource_id), ("result", outcome)):
        if value:
            stmt = stmt.where(getattr(AdminAuditLog, field) == value)
    if from_time:
        stmt = stmt.where(AdminAuditLog.created_at >= from_time)
    if to_time:
        stmt = stmt.where(AdminAuditLog.created_at <= to_time)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(AdminAuditLog.created_at.desc(), AdminAuditLog.id.desc()).offset((page-1)*page_size).limit(page_size)).all()
    fields = ("id", "actor_id", "action", "command_id", "event_kind", "request_id", "created_at")
    return envelope({"items": [{**{key: getattr(x, key) for key in fields}, "resource_type": x.target_type,
                               "resource_id": x.target_id, "outcome": x.result, "changes": x.detail} for x in rows],
                     "total": total, "page": page, "page_size": page_size})

from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .db import get_db
from .dependencies import require_permission, csrf_guard
from .errors import envelope
from .models import AdminCommand
from .schemas import StatusCommand, ModerationCommand
from .services.commands import accept_command, dispatch_command, reconcile_command, retry_command, dto, TERMINAL

router = APIRouter(tags=["commands"])


def result(key):
    from .db import SessionLocal
    with SessionLocal() as db:
        row = db.get(AdminCommand, key)
        return JSONResponse(status_code=200 if row.status in TERMINAL else 202, content=envelope(dto(row)))


@router.post("/accounts/{account_id}/status", dependencies=[Depends(csrf_guard)])
async def account_status(account_id: int, body: StatusCommand, key: UUID = Header(alias="Idempotency-Key"),
                         admin=Depends(require_permission("accounts:status_write"))):
    accept_command(admin, "accounts", account_id, body.model_dump(), str(key))
    await dispatch_command(str(key))
    return result(str(key))


@router.post("/jobs/{job_id}/moderation", dependencies=[Depends(csrf_guard)])
async def job_moderation(job_id: int, body: ModerationCommand, key: UUID = Header(alias="Idempotency-Key"),
                         admin=Depends(require_permission("jobs:moderate"))):
    accept_command(admin, "jobs", job_id, body.model_dump(), str(key))
    await dispatch_command(str(key))
    return result(str(key))


@router.get("/commands")
def commands(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
             state: str = "", admin=Depends(require_permission("commands:read")), db: Session = Depends(get_db)):
    stmt = select(AdminCommand)
    if admin.role == "operator":
        stmt = stmt.where(AdminCommand.actor_id == admin.id)
    if state:
        stmt = stmt.where(AdminCommand.status == state)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(AdminCommand.created_at.desc(), AdminCommand.command_id.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return envelope({"items": [dto(x) for x in rows], "total": total, "page": page, "page_size": page_size})


@router.get("/commands/{command_id}")
async def command(command_id: UUID, admin=Depends(require_permission("commands:read")), db: Session = Depends(get_db)):
    key = str(command_id)
    row = db.get(AdminCommand, key)
    if not row or (admin.role == "operator" and row.actor_id != admin.id):
        raise HTTPException(404, "命令不存在")
    db.rollback()
    await reconcile_command(key)
    return result(key)


@router.post("/commands/{command_id}/retry", dependencies=[Depends(csrf_guard)])
async def retry(command_id: UUID, admin=Depends(require_permission("commands:read"))):
    await retry_command(str(command_id), admin)
    return result(str(command_id))

import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import get_db
from .dependencies import require_permission, csrf_guard
from .errors import envelope
from .models import AdminAccount, AdminSecurityLock, AdminSession
from .schemas import CreateAdmin, UpdateAdmin, ReasonBody
from .security import hash_password
from .services.audit import record

router = APIRouter(prefix="/administrators", tags=["administrators"])
manage = require_permission("administrators:manage")


def dto(row):
    return {"id": row.id, "username": row.username, "role": row.role, "is_active": row.is_active,
            "session_version": row.session_version, "created_at": row.created_at}


@router.get("")
def list_admins(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
               admin=Depends(manage), db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(AdminAccount))
    rows = db.scalars(select(AdminAccount).order_by(AdminAccount.created_at.desc(), AdminAccount.id.desc())
                      .offset((page-1)*page_size).limit(page_size)).all()
    return envelope({"items": [dto(x) for x in rows], "total": total, "page": page, "page_size": page_size})


@router.post("", status_code=201, dependencies=[Depends(csrf_guard)])
def create_admin(body: CreateAdmin, admin=Depends(manage), db: Session = Depends(get_db)):
    row = AdminAccount(username=body.username, password_hash=hash_password(body.password), role=body.role)
    db.add(row)
    try:
        db.flush()
        record(db, admin.id, "administrators.create", target_type="administrator", target_id=row.id,
               detail={"reason": body.reason, "after": {"username": row.username, "role": row.role}})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "管理员账号已存在") from None
    return envelope(dto(row))


@router.patch("/{admin_id}", dependencies=[Depends(csrf_guard)])
def update_admin(admin_id: str, body: UpdateAdmin, admin=Depends(manage), db: Session = Depends(get_db)):
    db.execute(update(AdminSecurityLock).where(AdminSecurityLock.id == 1).values(revision=AdminSecurityLock.revision + 1))
    row = db.get(AdminAccount, admin_id)
    if not row:
        raise HTTPException(404, "管理员不存在")
    db.refresh(row)
    if row.session_version != body.expected_version:
        raise HTTPException(409, "管理员账号已变化，请刷新")
    old = {"role": row.role, "is_active": row.is_active, "session_version": row.session_version}
    role = body.role if body.role is not None else row.role
    active = body.is_active if body.is_active is not None else row.is_active
    if row.role == "super_admin" and row.is_active and (role != "super_admin" or not active):
        count = db.scalar(select(func.count()).select_from(AdminAccount).where(
            AdminAccount.role == "super_admin", AdminAccount.is_active.is_(True)))
        if count <= 1:
            raise HTTPException(409, "不能停用或降级最后一个超级管理员")
    row.role, row.is_active, row.session_version = role, active, row.session_version + 1
    db.execute(update(AdminSession).where(AdminSession.admin_id == row.id).values(revoked_at=int(time.time())))
    record(db, admin.id, "administrators.update", target_type="administrator", target_id=row.id,
           detail={"reason": body.reason, "before": old, "after": {"role": role, "is_active": active}})
    db.commit()
    return envelope(dto(row))


@router.post("/{admin_id}/revoke-sessions", dependencies=[Depends(csrf_guard)])
def revoke(admin_id: str, body: ReasonBody, admin=Depends(manage), db: Session = Depends(get_db)):
    changed = db.execute(update(AdminAccount).where(AdminAccount.id == admin_id).values(session_version=AdminAccount.session_version + 1))
    if not changed.rowcount:
        raise HTTPException(404, "管理员不存在")
    db.execute(update(AdminSession).where(AdminSession.admin_id == admin_id).values(revoked_at=int(time.time())))
    record(db, admin.id, "administrators.revoke_sessions", target_type="administrator", target_id=admin_id,
           detail={"reason": body.reason})
    db.commit()
    return envelope()

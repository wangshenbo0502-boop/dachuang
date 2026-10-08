import hashlib
import time
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import update
from sqlalchemy.orm import Session
from .config import get_settings
from .db import get_db
from .dependencies import current_admin, csrf_guard, require_origin
from .errors import envelope
from .models import AdminAccount, AdminLoginLimit, AdminSession, AdminSecurityLock
from .permissions import ROLE_PERMISSIONS
from .schemas import LoginBody, PasswordBody
from .security import dummy_hash, hash_password, issue_session, set_cookie, verify_password
from .services.audit import record

router = APIRouter(prefix="/auth", tags=["auth"])


def identity(admin, csrf):
    return {"admin": {"id": admin.id, "username": admin.username, "role": admin.role},
            "permissions": sorted(ROLE_PERMISSIONS[admin.role]), "csrf_token": csrf}


@router.post("/login", dependencies=[Depends(require_origin)])
async def login(body: LoginBody, request: Request, response: Response, db: Session = Depends(get_db)):
    if request.headers.get("content-type", "").split(";")[0] != "application/json":
        raise HTTPException(422, "需要 JSON 请求")
    if len(await request.body()) > 4096:
        raise HTTPException(422, "请求过大")
    db.execute(update(AdminSecurityLock).where(AdminSecurityLock.id == 1).values(revision=AdminSecurityLock.revision + 1))
    key = hashlib.sha256(f"{body.username}|{request.client.host if request.client else ''}".encode()).hexdigest()
    now = int(time.time())
    limit = db.get(AdminLoginLimit, key)
    if limit and now - limit.window_start < 900 and limit.attempts >= 10:
        db.rollback()
        raise HTTPException(429, "登录尝试过于频繁，请稍后重试")
    if not limit:
        limit = AdminLoginLimit(key=key, window_start=now, attempts=0)
        db.add(limit)
    elif now - limit.window_start >= 900:
        limit.window_start, limit.attempts = now, 0
    limit.attempts += 1
    admin = db.query(AdminAccount).filter_by(username=body.username).first()
    valid = verify_password(body.password, admin.password_hash if admin else dummy_hash)
    if not admin or not valid or not admin.is_active:
        record(db, None, "auth.login", result="rejected")
        db.commit()
        raise HTTPException(401, "管理员凭证无效")
    limit.attempts = 0
    raw, csrf = issue_session(db, admin)
    record(db, admin.id, "auth.login")
    db.commit()
    set_cookie(response, raw)
    return envelope(identity(admin, csrf))


@router.get("/me")
def me(request: Request, response: Response, admin=Depends(current_admin)):
    response.headers["Cache-Control"] = "no-store"
    return envelope(identity(admin, request.state.admin_session.csrf_token))


@router.post("/logout", dependencies=[Depends(csrf_guard)])
def logout(request: Request, response: Response, admin=Depends(current_admin), db: Session = Depends(get_db)):
    request.state.admin_session.revoked_at = int(time.time())
    record(db, admin.id, "auth.logout")
    db.commit()
    response.delete_cookie(get_settings().cookie_name, path="/admin-api/v1", secure=get_settings().cookie_secure,
                           httponly=True, samesite="strict")
    response.headers["Cache-Control"] = "no-store"
    return envelope()


@router.post("/change-password", dependencies=[Depends(csrf_guard)])
def change_password(body: PasswordBody, response: Response, admin=Depends(current_admin), db: Session = Depends(get_db)):
    if not verify_password(body.current_password, admin.password_hash):
        raise HTTPException(422, "当前密码不正确")
    changed = db.execute(update(AdminAccount).where(AdminAccount.id == admin.id,
                        AdminAccount.session_version == admin.session_version).values(
                        password_hash=hash_password(body.new_password), session_version=AdminAccount.session_version + 1))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "管理员账号已变化")
    db.execute(update(AdminSession).where(AdminSession.admin_id == admin.id).values(revoked_at=int(time.time())))
    record(db, admin.id, "auth.change_password")
    db.commit()
    response.delete_cookie(get_settings().cookie_name, path="/admin-api/v1")
    response.headers["Cache-Control"] = "no-store"
    return envelope()

import secrets
import time
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .config import get_settings
from .db import get_db
from .models import AdminAccount, AdminSession
from .permissions import can
from .security import token_hash


def require_origin(request: Request):
    if request.headers.get("origin") != get_settings().origin:
        raise HTTPException(403, "请求来源不允许")


def current_admin(request: Request, db: Session = Depends(get_db)):
    raw = request.cookies.get(get_settings().cookie_name, "")
    if not raw or len(raw) > 256:
        raise HTTPException(401, "请先登录管理员系统")
    session = db.get(AdminSession, token_hash(raw))
    admin = db.get(AdminAccount, session.admin_id) if session else None
    if not session or session.revoked_at is not None or session.expires_at <= time.time() or not admin or not admin.is_active or admin.session_version != session.version:
        raise HTTPException(401, "管理员会话已失效")
    request.state.admin_session = session
    return admin


def csrf_guard(request: Request, admin=Depends(current_admin)):
    require_origin(request)
    supplied = request.headers.get("x-csrf-token", "")
    if not supplied or not secrets.compare_digest(supplied, request.state.admin_session.csrf_token):
        raise HTTPException(403, "CSRF 校验失败")


def require_permission(permission):
    def dependency(admin=Depends(current_admin)):
        if not can(admin.role, permission):
            raise HTTPException(403, "没有该操作权限")
        return admin
    return dependency

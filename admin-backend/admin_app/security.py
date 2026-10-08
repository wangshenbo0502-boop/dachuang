import hashlib
import secrets
import time
from uuid import uuid4
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from .models import AdminSession
from .config import get_settings

hasher = PasswordHasher()
dummy_hash = hasher.hash(secrets.token_urlsafe(32))


def hash_password(password):
    return hasher.hash(password)


def verify_password(password, password_hash):
    try:
        return hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def token_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def issue_session(db, admin):
    raw, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    db.add(AdminSession(token_hash=token_hash(raw), admin_id=admin.id,
                        version=admin.session_version, csrf_token=csrf,
                        expires_at=int(time.time()) + 28800))
    return raw, csrf


def set_cookie(response, raw):
    cfg = get_settings()
    response.set_cookie(cfg.cookie_name, raw, httponly=True, secure=cfg.cookie_secure,
                        samesite="strict", max_age=28800, path="/admin-api/v1")
    response.headers["Cache-Control"] = "no-store"


def request_id():
    return str(uuid4())

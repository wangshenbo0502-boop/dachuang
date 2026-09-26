"""Password hashing and signed access tokens."""
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from app.config import get_settings
from app.utils.exceptions import AppException

hasher = PasswordHasher()

def secret() -> str:
    value = get_settings().JWT_SECRET
    if len(value) < 32:
        raise AppException("服务端 JWT_SECRET 未配置或长度不足", code=5100, status_code=503)
    return value

def hash_password(password: str) -> str:
    return hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False

def hash_code(email: str, purpose: str, code: str) -> str:
    message = f"{email}:{purpose}:{code}".encode()
    return hmac.new(secret().encode(), message, hashlib.sha256).hexdigest()

def issue_token(account_id: int, version: int) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(account_id), "ver": version, "iat": now, "exp": now + timedelta(minutes=get_settings().JWT_ACCESS_MINUTES)}, secret(), algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, secret(), algorithms=["HS256"], options={"require": ["sub", "exp", "iat"]})
    except jwt.ExpiredSignatureError as exc:
        raise AppException("登录已过期，请重新登录", code=5101, status_code=401) from exc
    except jwt.InvalidTokenError as exc:
        raise AppException("登录凭证无效", code=5102, status_code=401) from exc

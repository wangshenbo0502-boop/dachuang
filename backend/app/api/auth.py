"""QQ email registration and JWT login."""
from datetime import datetime, timedelta, timezone
import logging
import secrets
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_account
from app.auth.security import hash_code, hash_password, issue_token, verify_password
from app.config import get_settings
from app.database.session import get_db
from app.models.account import Account, EmailCode
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, ResetPasswordRequest, SendCodeRequest
from app.utils.exceptions import AppException
from app.utils.response import success

router = APIRouter(prefix="/api/auth", tags=["身份认证"])
logger = logging.getLogger(__name__)

def _as_utc(value: datetime) -> datetime:
    # SQLite drops timezone info; PostgreSQL preserves it.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

def public_user(account: Account) -> dict:
    return {"id": account.id, "email": account.email, "profile_id": account.profile_id, "email_verified": account.email_verified}

def _send_mail(email: str, code: str, purpose: str) -> None:
    settings = get_settings()
    if settings.DEV_EMAIL_CODE_MODE:
        logger.warning("[DEV] verification code sent to %s: %s", email, code)
        return
    if not all((settings.SMTP_HOST, settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.SMTP_FROM)):
        raise AppException("邮箱发送服务未配置", code=5201, status_code=503)
    message = EmailMessage()
    message["Subject"] = "就业成长平台邮箱验证码"
    message["From"] = settings.SMTP_FROM
    message["To"] = email
    message.set_content(f"您的{'注册' if purpose == 'REGISTER' else '重置密码'}验证码是 {code}，5 分钟内有效。")
    try:
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise AppException("验证码发送失败，请稍后重试", code=5202, status_code=503) from exc

@router.post("/email/send-code")
def send_code(body: SendCodeRequest, db: Session = Depends(get_db)) -> dict:
    existing_account = db.scalar(select(Account.id).where(Account.email == body.email))
    if body.purpose == "REGISTER" and existing_account:
        raise AppException("该邮箱已注册，请直接登录", code=5203, status_code=409)
    if body.purpose == "RESET_PASSWORD" and not existing_account:
        return success({"expires_in": 300}, message="如邮箱已注册，验证码将发送至该邮箱")
    now = datetime.now(timezone.utc)
    row = db.scalar(select(EmailCode).where(EmailCode.email == body.email, EmailCode.purpose == body.purpose))
    if row and now - _as_utc(row.sent_at) < timedelta(seconds=60):
        raise AppException("发送过于频繁，请 60 秒后重试", code=5204, status_code=429)
    count = row.daily_count if row and row.day == now.date().isoformat() else 0
    if count >= 10:
        raise AppException("今日验证码发送次数已达上限", code=5205, status_code=429)
    code = f"{secrets.randbelow(1_000_000):06d}"
    code_digest = hash_code(body.email, body.purpose, code)
    _send_mail(body.email, code, body.purpose)
    if row is None:
        row = EmailCode(email=body.email, purpose=body.purpose, code_hash="", expires_at=now, sent_at=now, day=now.date().isoformat())
        db.add(row)
    row.code_hash = code_digest
    row.expires_at = now + timedelta(minutes=5)
    row.sent_at = now
    row.day = now.date().isoformat()
    row.daily_count = count + 1
    row.failed_attempts = 0
    db.commit()
    return success({"expires_in": 300}, message="验证码已发送")

@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    if body.password != body.confirm_password:
        raise AppException("两次输入的密码不一致", code=5206)
    if db.scalar(select(Account.id).where(Account.email == body.email)):
        raise AppException("该邮箱已注册，请直接登录", code=5203, status_code=409)
    row = db.scalar(select(EmailCode).where(EmailCode.email == body.email, EmailCode.purpose == "REGISTER"))
    now = datetime.now(timezone.utc)
    if not row or _as_utc(row.expires_at) < now:
        raise AppException("验证码已过期，请重新获取", code=5207)
    if row.failed_attempts >= 5:
        raise AppException("验证码错误次数过多，请重新获取", code=5208, status_code=429)
    if not secrets.compare_digest(row.code_hash, hash_code(body.email, "REGISTER", body.code)):
        row.failed_attempts += 1
        db.commit()
        raise AppException("验证码错误", code=5209)
    try:
        profile = User(name=body.name or "新同学", school="待完善", major="待完善", grade="待完善", email=body.email)
        db.add(profile)
        db.flush()
        account = Account(username=body.email.split("@")[0], email=body.email, password_hash=hash_password(body.password), profile_id=profile.id, email_verified=True)
        db.add(account)
        db.delete(row)
        db.commit()
        db.refresh(account)
    except IntegrityError as exc:
        db.rollback()
        raise AppException("该邮箱已注册，请直接登录", code=5203, status_code=409) from exc
    return success({"access_token": issue_token(account.id, account.token_version), "token_type": "bearer", "user": public_user(account)}, message="注册成功")

@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    if body.password != body.confirm_password:
        raise AppException("两次输入的密码不一致", code=5206)
    account = db.scalar(select(Account).where(Account.email == body.email))
    row = db.scalar(select(EmailCode).where(EmailCode.email == body.email, EmailCode.purpose == "RESET_PASSWORD"))
    now = datetime.now(timezone.utc)
    if not account or not row or _as_utc(row.expires_at) < now:
        raise AppException("验证码已过期，请重新获取", code=5207)
    if row.failed_attempts >= 5:
        raise AppException("验证码错误次数过多，请重新获取", code=5208, status_code=429)
    if not secrets.compare_digest(row.code_hash, hash_code(body.email, "RESET_PASSWORD", body.code)):
        row.failed_attempts += 1
        db.commit()
        raise AppException("验证码错误", code=5209)
    account.password_hash = hash_password(body.password)
    account.token_version += 1
    db.delete(row)
    db.commit()
    return success(None, message="密码已重置，请重新登录")

@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)) -> dict:
    account = db.scalar(select(Account).where(Account.email == body.email))
    if not account or not verify_password(body.password, account.password_hash):
        raise AppException("邮箱或密码错误", code=5210, status_code=401)
    if not account.is_active:
        raise AppException("账号已禁用", code=5104, status_code=403)
    account.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return success({"access_token": issue_token(account.id, account.token_version), "token_type": "bearer", "user": public_user(account)}, message="登录成功")

@router.get("/me")
def me(account: Account = Depends(get_current_account)) -> dict:
    return success(public_user(account))

@router.post("/logout")
def logout(account: Account = Depends(get_current_account), db: Session = Depends(get_db)) -> dict:
    account.token_version += 1
    db.commit()
    return success(None, message="已退出登录")

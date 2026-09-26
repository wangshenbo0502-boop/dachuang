"""Shared FastAPI identity and ownership dependencies."""
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.user import User
from app.auth.security import decode_token
from app.utils.exceptions import AppException

bearer = HTTPBearer(auto_error=False)

def get_current_account(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> Account:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppException("请先登录", code=5103, status_code=401)
    payload = decode_token(credentials.credentials)
    try:
        account_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AppException("登录凭证无效", code=5102, status_code=401) from exc
    account = db.get(Account, account_id)
    if not account or account.token_version != payload.get("ver"):
        raise AppException("登录凭证无效", code=5102, status_code=401)
    if not account.is_active:
        raise AppException("账号已禁用", code=5104, status_code=403)
    return account

def get_current_user(request: Request, account: Account = Depends(get_current_account), db: Session = Depends(get_db)) -> User:
    user = db.get(User, account.profile_id)
    if not user:
        raise AppException("学生档案不存在", code=5105, status_code=404)
    requested_id = request.path_params.get("user_id")
    if requested_id is not None:
        require_owner(int(requested_id), user)
    return user

def require_owner(requested_id: int | None, current_user: User) -> None:
    if requested_id != current_user.id:
        raise AppException("无权限访问其他用户数据", code=5106, status_code=403)

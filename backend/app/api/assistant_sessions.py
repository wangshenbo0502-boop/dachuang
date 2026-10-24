"""Server-side storage for AI career assistant conversations.

Conversations are private: every query is scoped to the logged-in student, so a
session id belonging to someone else behaves exactly like one that does not exist.
Recruiters cannot reach these routes because get_current_user is student-only.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Path
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.assistant_session import AssistantSession
from app.models.user import User
from app.schemas.assistant import SESSION_ID_PATTERN, AssistantSessionPayload
from app.utils.exceptions import AppException, ResourceNotFoundError
from app.utils.response import success

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/chat/sessions", tags=["AI求职助手会话"])

MAX_SESSIONS_PER_USER = 200
SessionId = Path(pattern=SESSION_ID_PATTERN)


def _iso(value: datetime) -> str:
    # SQLite 读回时会丢失时区信息，统一按 UTC 输出
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _summary(row: AssistantSession) -> dict:
    return {
        "id": row.session_id,
        "title": row.title,
        "mode": row.mode,
        "createdAt": _iso(row.created_at),
        "updatedAt": _iso(row.updated_at),
    }


def _detail(row: AssistantSession) -> dict:
    return {
        **_summary(row),
        "target": row.target,
        "consultMessages": row.consult_messages,
        "profileMessages": row.profile_messages,
        "draft": row.draft,
        "suggestedAction": row.suggested_action,
    }


def _owned(db: Session, user: User, session_id: str) -> AssistantSession | None:
    return db.scalar(
        select(AssistantSession).where(
            AssistantSession.user_id == user.id,
            AssistantSession.session_id == session_id,
        )
    )


@router.get("")
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    rows = db.scalars(
        select(AssistantSession)
        .where(AssistantSession.user_id == current_user.id)
        .order_by(AssistantSession.updated_at.desc())
    ).all()
    return success([_summary(row) for row in rows], message="获取对话列表成功")


@router.get("/{session_id}")
def get_session(
    session_id: str = SessionId,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    row = _owned(db, current_user, session_id)
    if row is None:
        raise ResourceNotFoundError("对话不存在")
    return success(_detail(row), message="获取对话成功")


@router.put("/{session_id}")
def save_session(
    body: AssistantSessionPayload,
    session_id: str = SessionId,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        row = _write_session(db, current_user, session_id, body)
    except IntegrityError:
        # 同一新对话的两次保存并发到达，后到的一次改为更新已插入的记录
        db.rollback()
        row = _write_session(db, current_user, session_id, body)
    return success(_summary(row), message="对话已保存")


def _write_session(db: Session, current_user: User, session_id: str, body: AssistantSessionPayload) -> AssistantSession:
    now = datetime.now(timezone.utc)
    row = _owned(db, current_user, session_id)
    if row is None:
        count = db.scalar(select(func.count()).where(AssistantSession.user_id == current_user.id))
        if count >= MAX_SESSIONS_PER_USER:
            raise AppException(
                f"最多保存 {MAX_SESSIONS_PER_USER} 个对话，请先删除不需要的对话",
                code=4231,
                status_code=409,
            )
        row = AssistantSession(user_id=current_user.id, session_id=session_id, created_at=now)
        db.add(row)
    row.title = body.title
    row.mode = body.mode
    row.target = body.target
    row.consult_messages = [item.model_dump() for item in body.consultMessages]
    row.profile_messages = [item.model_dump() for item in body.profileMessages]
    row.draft = body.draft
    row.suggested_action = body.suggestedAction
    row.updated_at = now
    db.commit()
    return row


@router.delete("/{session_id}")
def delete_session(
    session_id: str = SessionId,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    row = _owned(db, current_user, session_id)
    if row is not None:
        db.delete(row)
        db.commit()
    return success(None, message="对话已删除")

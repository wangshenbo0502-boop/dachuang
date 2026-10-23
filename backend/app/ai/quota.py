"""Per-student daily AI request quota.

The global cost budget in DeepSeekClient caps platform spend; this quota stops a
single account from using up that budget for everyone else.
"""
from datetime import date

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.ai_usage import AIUsageDaily
from app.models.user import User
from app.utils.exceptions import AppException
from app.utils.response import ErrorCode


def _quota_applies() -> bool:
    """Mock 模式不产生费用，不占用额度，避免影响本地演示。"""
    settings = get_settings()
    return settings.ai_enabled and settings.AI_USER_DAILY_LIMIT > 0


def _try_increment(db: Session, user_id: int, day: str, limit: int) -> bool:
    # 条件更新在数据库内原子完成，并发请求不会越过上限
    result = db.execute(
        update(AIUsageDaily)
        .where(
            AIUsageDaily.user_id == user_id,
            AIUsageDaily.day == day,
            AIUsageDaily.request_count < limit,
        )
        .values(request_count=AIUsageDaily.request_count + 1)
    )
    return result.rowcount > 0


def consume_ai_quota(db: Session, current_user: User) -> None:
    """为当前学生记一次 AI 请求，超出当日额度时返回 429。

    在路由内完成归属校验之后调用，参数校验或越权失败的请求不占用额度。
    """
    if not _quota_applies():
        return
    limit = get_settings().AI_USER_DAILY_LIMIT
    day = date.today().isoformat()

    if not _try_increment(db, current_user.id, day, limit):
        exists = db.query(AIUsageDaily.id).filter_by(user_id=current_user.id, day=day).first()
        if exists:
            db.rollback()
            raise AppException(
                f"今日 AI 使用次数已达上限（{limit} 次），请明天再试",
                code=ErrorCode.AI_QUOTA_EXCEEDED.value,
                status_code=429,
            )
        try:
            db.add(AIUsageDaily(user_id=current_user.id, day=day, request_count=1))
            db.flush()
        except IntegrityError:
            # 并发请求已抢先插入当天记录，回退到条件更新
            db.rollback()
            if not _try_increment(db, current_user.id, day, limit):
                raise AppException(
                    f"今日 AI 使用次数已达上限（{limit} 次），请明天再试",
                    code=ErrorCode.AI_QUOTA_EXCEEDED.value,
                    status_code=429,
                )
    db.commit()

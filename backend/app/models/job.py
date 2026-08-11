"""
文件名称：job.py
文件作用：岗位匹配相关 ORM 数据模型。
定义岗位匹配记录模型，用于持久化用户的匹配历史，供后续查询与统计。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class JobMatchRecord(Base):
    """岗位匹配记录：保存某次技能匹配的完整结果快照。

    每次调用 POST /api/match 时生成一条记录，
    匹配结果以 JSON 形式持久化，支持历史查询与后续分析。
    """

    __tablename__ = "job_match_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # 匹配输入：用户技能列表
    skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    # 匹配主结果：得分最高的岗位
    job_id: Mapped[str] = mapped_column(String(200), nullable=False)
    job_title: Mapped[str] = mapped_column(String(200), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # 命中的技能与缺失的技能
    matched_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    missing_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    # 完整匹配结果快照（MatchedJob 列表）
    result: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

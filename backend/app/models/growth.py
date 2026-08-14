"""
文件名称：growth.py
文件作用：成长规划相关 ORM 数据模型定义。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class GrowthPlan(Base):
    """成长规划记录

    保存每次AI生成的成长规划结果。
    """

    __tablename__ = "growth_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # 输入信息
    input_name: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    input_major: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    input_grade: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    target_job: Mapped[str] = mapped_column(String(100), nullable=False, default="")

    # 规划结果
    current_situation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ability_gaps: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    learning_roadmap: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    recommended_projects: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    recommended_resources: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    interview_prep_tips: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    expected_timeline: Mapped[str] = mapped_column(String(200), nullable=False, default="")

    # 完整原始结果
    raw_result: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

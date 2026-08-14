"""
文件名称：analysis.py
文件作用：AI 就业画像分析相关 ORM 数据模型定义。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class ProfileAnalysis(Base):
    """就业画像分析记录

    保存每次AI分析的完整结果，支持历史查询。
    """

    __tablename__ = "profile_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # 分析输入快照
    input_name: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    input_school: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    input_major: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    input_grade: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    target_job: Mapped[str] = mapped_column(String(100), nullable=False, default="")

    # 分析结果（JSON格式存储）
    profile_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    technical_direction: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    core_advantages: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    current_level: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    recommended_directions: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    areas_to_improve: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    comprehensive_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skill_assessment: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # 完整原始结果
    raw_result: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

"""
文件名称：resume.py
文件作用：简历优化相关 ORM 数据模型定义。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class ResumeOptimization(Base):
    """简历优化记录

    保存每次简历优化的完整结果。
    """

    __tablename__ = "resume_optimizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # 输入信息
    input_name: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    target_job: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    original_resume: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # 优化结果
    optimized_projects: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    optimized_skills: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    overall_suggestions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    personal_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    resume_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # 完整原始结果
    raw_result: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

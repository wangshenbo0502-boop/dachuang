"""AI career assistant conversations, private to the student who created them."""
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class AssistantSession(Base):
    __tablename__ = "assistant_sessions"
    __table_args__ = (UniqueConstraint("user_id", "session_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # 前端生成的会话编号，只在同一学生名下唯一
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(60), nullable=False, default="新对话")
    mode: Mapped[str] = mapped_column(String(10), nullable=False, default="consult")
    target: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    consult_messages: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    profile_messages: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    draft: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    suggested_action: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

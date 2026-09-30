"""Account-scoped learning tasks and resource interactions."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class GrowthTask(Base):
    __tablename__ = "growth_tasks"
    __table_args__ = (UniqueConstraint("user_id", "source_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source_key: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(500))
    target_job: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="todo")
    feedback: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    resource_query: Mapped[str] = mapped_column(String(500), default="")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ResourceEvent(Base):
    __tablename__ = "resource_user_events"
    __table_args__ = (UniqueConstraint("user_id", "resource_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    resource_key: Mapped[str] = mapped_column(String(100))
    resource: Mapped[dict] = mapped_column(JSON, default=dict)
    favorite: Mapped[bool] = mapped_column(default=False)
    read: Mapped[bool] = mapped_column(default=False)
    hidden: Mapped[bool] = mapped_column(default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

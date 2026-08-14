"""
文件名称：user.py
文件作用：定义学生基本资料、技能、项目经历、竞赛经历和实习经历的 ORM 数据模型。
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class User(Base):
    """学生基本资料，是技能、项目、竞赛和实习经历的聚合根。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    school: Mapped[str] = mapped_column(String(100), nullable=False)
    major: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str] = mapped_column(String(30), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="")
    email: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    target_city: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    target_salary: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    skills: Mapped[list[UserSkill]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list[UserProject]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    competitions: Mapped[list[UserCompetition]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    internships: Mapped[list[UserInternship]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserSkill(Base):
    """学生自评技能信息。"""

    __tablename__ = "user_skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    user: Mapped[User] = relationship(back_populates="skills")


class UserProject(Base):
    """学生项目实践经历。"""

    __tablename__ = "user_projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tech_stack: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped[User] = relationship(back_populates="projects")


class UserCompetition(Base):
    """学生竞赛获奖经历。"""

    __tablename__ = "user_competitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[str] = mapped_column(String(30), nullable=False, default="校级")
    award: Mapped[str] = mapped_column(String(100), nullable=False, default="参与奖")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    competition_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped[User] = relationship(back_populates="competitions")


class UserInternship(Base):
    """学生实习经历。"""

    __tablename__ = "user_internships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tech_stack: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped[User] = relationship(back_populates="internships")
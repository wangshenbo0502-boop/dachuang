"""Recruiter-owned vacancies and immutable, voluntarily shared resume snapshots."""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connection import Base


class RecruiterProfile(Base):
    __tablename__ = "recruiter_profiles"
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(150), default="", nullable=False)
    industry: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    city: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    contact_name: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    contact_email: Mapped[str] = mapped_column(String(100), default="", nullable=False)


class RecruitmentJob(Base):
    __tablename__ = "recruitment_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    recruiter_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), index=True)
    title: Mapped[str] = mapped_column(String(150), default="", nullable=False)
    company_name: Mapped[str] = mapped_column(String(150), default="", nullable=False)
    category: Mapped[str] = mapped_column(String(30), default="", nullable=False)
    city: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    salary: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    employment_type: Mapped[str] = mapped_column(String(20), default="实习", nullable=False)
    education: Mapped[str] = mapped_column(String(30), default="不限", nullable=False)
    experience: Mapped[str] = mapped_column(String(80), default="不限", nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    requirements: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True, nullable=False)
    moderation_status: Mapped[str] = mapped_column(String(20), default="allowed", server_default="allowed", index=True, nullable=False)
    management_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RecruitmentApplication(Base):
    __tablename__ = "recruitment_applications"
    __table_args__ = (UniqueConstraint("job_id", "student_id", name="uq_recruitment_job_student"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("recruitment_jobs.id", ondelete="RESTRICT"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), index=True)
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    resume_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    note: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="submitted", nullable=False, index=True)
    feedback: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

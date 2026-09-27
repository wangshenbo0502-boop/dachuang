"""BOSS 直聘投递助手接口数据结构。"""

from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field


ApplicationStatus = Literal["prepared", "opened", "applied", "replied", "interview", "closed"]


class JobApplicationCreate(BaseModel):
    job_id: str = Field(min_length=1, max_length=200)
    job_title: str = Field(min_length=1, max_length=200)
    boss_url: AnyHttpUrl
    greeting: str = Field(default="", max_length=2000)
    resume_version_id: int | None = Field(default=None, ge=1)
    note: str = Field(default="", max_length=2000)


class JobApplicationUpdate(BaseModel):
    status: ApplicationStatus
    note: str | None = Field(default=None, max_length=2000)


class ApplicationAutomationResponse(BaseModel):
    status: str
    message: str
    url: str = ""
    greeting_filled: bool = False


class JobApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: str
    job_title: str
    platform: str
    boss_url: str
    status: str
    greeting: str
    resume_version_id: int | None
    note: str
    applied_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
    automation_status: str
    automation_error: str

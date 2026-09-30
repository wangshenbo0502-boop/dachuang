"""Strict inputs: clients never choose owners or write lifecycle state directly."""
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

JobCategory = Literal["", "前端", "后端", "AI", "数据", "测试", "运维", "产品", "运营", "安全", "移动端", "其他"]


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RecruiterProfileInput(StrictInput):
    company_name: str = Field(default="", max_length=150)
    industry: str = Field(default="", max_length=80)
    city: str = Field(default="", max_length=80)
    description: str = Field(default="", max_length=10000)
    contact_name: str = Field(default="", max_length=50)
    contact_email: str = Field(default="", max_length=100)

    @field_validator("contact_email")
    @classmethod
    def valid_email(cls, value):
        if value and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("请输入有效的联系邮箱")
        return value


class RecruitmentJobInput(StrictInput):
    title: str = Field(default="", max_length=150)
    category: JobCategory = ""
    city: str = Field(default="", max_length=80)
    salary: str = Field(default="", max_length=80)
    employment_type: Literal["实习", "全职", "兼职"] = "实习"
    education: Literal["不限", "大专", "本科", "硕士", "博士"] = "不限"
    experience: str = Field(default="不限", max_length=80)
    description: str = Field(default="", max_length=20000)
    requirements: str = Field(default="", max_length=20000)
    tags: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, values):
        values = list(dict.fromkeys(value.strip() for value in values if value.strip()))
        if any(len(value) > 50 for value in values):
            raise ValueError("技能标签不能超过 50 字")
        return values


class JobStatusInput(StrictInput):
    status: Literal["published", "closed"]


class ApplyInput(StrictInput):
    resume_id: int = Field(ge=1)
    note: str = Field(default="", max_length=2000)


class ApplicationUpdateInput(StrictInput):
    status: Literal["reviewing", "interview", "offered", "rejected"]
    feedback: str = Field(default="", max_length=2000)

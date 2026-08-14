"""
文件名称：user.py
文件作用：定义学生资料、技能、项目经历、竞赛经历和实习经历接口使用的 Pydantic 数据结构。
"""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ProficiencyLevel = Literal["了解", "熟悉", "掌握", "精通"]


class UserBase(BaseModel):
    """学生基本资料的公共字段。"""
    name: str = Field(min_length=1, max_length=50)
    school: str = Field(min_length=1, max_length=100)
    major: str = Field(min_length=1, max_length=100)
    grade: str = Field(min_length=1, max_length=30)
    bio: str = Field(default="", max_length=5000)
    email: str = Field(default="", max_length=100)
    phone: str = Field(default="", max_length=20)
    target_city: str = Field(default="", max_length=50)
    target_salary: str = Field(default="", max_length=50)


class UserCreate(UserBase):
    """创建学生资料请求体。"""


class UserUpdate(BaseModel):
    """更新学生资料请求体，未提供的字段保持原值。"""
    name: str | None = Field(default=None, min_length=1, max_length=50)
    school: str | None = Field(default=None, min_length=1, max_length=100)
    major: str | None = Field(default=None, min_length=1, max_length=100)
    grade: str | None = Field(default=None, min_length=1, max_length=30)
    bio: str | None = Field(default=None, max_length=5000)
    email: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    target_city: str | None = Field(default=None, max_length=50)
    target_salary: str | None = Field(default=None, max_length=50)


class UserSkillCreate(BaseModel):
    """单项学生技能输入。"""
    name: str = Field(min_length=1, max_length=100)
    proficiency: ProficiencyLevel
    description: str = Field(default="", max_length=2000)


class UserSkillsReplace(BaseModel):
    """整组替换用户技能的请求体。"""
    skills: list[UserSkillCreate] = Field(default_factory=list, max_length=100)


class UserProjectCreate(BaseModel):
    """单项学生项目经历输入。"""
    name: str = Field(min_length=1, max_length=150)
    role: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=10000)
    tech_stack: list[str] = Field(default_factory=list, max_length=50)
    start_date: date | None = None
    end_date: date | None = None


class UserProjectsReplace(BaseModel):
    """整组替换用户项目经历的请求体。"""
    projects: list[UserProjectCreate] = Field(default_factory=list, max_length=50)


# ── 竞赛经历 ──

class UserCompetitionCreate(BaseModel):
    """单项竞赛经历输入。"""
    name: str = Field(min_length=1, max_length=200)
    level: str = Field(default="校级", max_length=30)
    award: str = Field(default="参与奖", max_length=100)
    description: str = Field(default="", max_length=5000)
    competition_date: Optional[date] = Field(default=None)


class UserCompetitionsReplace(BaseModel):
    """整组替换竞赛经历的请求体。"""
    competitions: list[UserCompetitionCreate] = Field(default_factory=list, max_length=20)


# ── 实习经历 ──

class UserInternshipCreate(BaseModel):
    """单项实习经历输入。"""
    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=10000)
    tech_stack: list[str] = Field(default_factory=list, max_length=50)
    start_date: date | None = None
    end_date: date | None = None


class UserInternshipsReplace(BaseModel):
    """整组替换实习经历的请求体。"""
    internships: list[UserInternshipCreate] = Field(default_factory=list, max_length=20)


# ── 响应体 ──

class UserSkillResponse(UserSkillCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class UserProjectResponse(UserProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class UserCompetitionResponse(UserCompetitionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class UserInternshipResponse(UserInternshipCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class UserProfileResponse(UserResponse):
    """包含全部关联数据的学生资料响应结构。"""
    skills: list[UserSkillResponse] = Field(default_factory=list)
    projects: list[UserProjectResponse] = Field(default_factory=list)
    competitions: list[UserCompetitionResponse] = Field(default_factory=list)
    internships: list[UserInternshipResponse] = Field(default_factory=list)


class StudentContextResponse(BaseModel):
    """提供给 AI 业务模块的稳定学生上下文结构。"""
    user_id: int
    name: str
    school: str
    major: str
    grade: str
    bio: str
    email: str = ""
    phone: str = ""
    target_city: str = ""
    target_salary: str = ""
    skills: list[UserSkillResponse] = Field(default_factory=list)
    projects: list[UserProjectResponse] = Field(default_factory=list)
    competitions: list[UserCompetitionResponse] = Field(default_factory=list)
    internships: list[UserInternshipResponse] = Field(default_factory=list)
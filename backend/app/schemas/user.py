"""
文件名称：user.py
文件作用：定义学生资料、技能和项目经历接口使用的 Pydantic 数据结构。
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ProficiencyLevel = Literal["了解", "熟悉", "掌握", "精通"]


class UserBase(BaseModel):
    """学生基本资料的公共字段。"""

    name: str = Field(min_length=1, max_length=50)
    school: str = Field(min_length=1, max_length=100)
    major: str = Field(min_length=1, max_length=100)
    grade: str = Field(min_length=1, max_length=30)
    bio: str = Field(default="", max_length=5000)


class UserCreate(UserBase):
    """创建学生资料请求体。"""


class UserUpdate(BaseModel):
    """更新学生资料请求体，未提供的字段保持原值。"""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    school: str | None = Field(default=None, min_length=1, max_length=100)
    major: str | None = Field(default=None, min_length=1, max_length=100)
    grade: str | None = Field(default=None, min_length=1, max_length=30)
    bio: str | None = Field(default=None, max_length=5000)


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


class UserSkillResponse(UserSkillCreate):
    """技能持久化后的响应结构。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class UserProjectResponse(UserProjectCreate):
    """项目经历持久化后的响应结构。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class UserResponse(UserBase):
    """学生基本资料响应结构。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class UserProfileResponse(UserResponse):
    """包含全部技能和项目经历的学生资料响应结构。"""

    skills: list[UserSkillResponse] = Field(default_factory=list)
    projects: list[UserProjectResponse] = Field(default_factory=list)


class StudentContextResponse(BaseModel):
    """提供给 AI 业务模块的稳定学生上下文结构。"""

    user_id: int
    name: str
    school: str
    major: str
    grade: str
    bio: str
    skills: list[UserSkillResponse] = Field(default_factory=list)
    projects: list[UserProjectResponse] = Field(default_factory=list)

"""
文件名称：growth.py
文件作用：成长规划相关 Pydantic 数据结构定义。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ── 请求体 ──

class GrowthPlanRequest(BaseModel):
    """成长规划请求"""
    user_id: Optional[int] = Field(default=None, description="用户ID（如果已保存用户信息）")

    # 直接传入信息
    name: Optional[str] = Field(default=None, max_length=50, description="姓名")
    major: Optional[str] = Field(default=None, max_length=100, description="专业")
    grade: Optional[str] = Field(default=None, max_length=30, description="年级")
    target_job: str = Field(..., min_length=1, max_length=100, description="目标岗位（必填）")
    skills: list[dict] = Field(default_factory=list, description="当前技能列表")
    projects: list[dict] = Field(default_factory=list, description="项目列表")

    # 可选：传入之前的画像分析结果
    profile_analysis: Optional[dict] = Field(default=None, description="之前的画像分析结果（可选）")

    @model_validator(mode="after")
    def require_user_or_inline_profile(self) -> "GrowthPlanRequest":
        if self.user_id is not None:
            return self
        missing = [field for field in ("name", "major", "grade") if not getattr(self, field)]
        if missing:
            raise ValueError("未提供 user_id 时，name、major、grade 为必填字段")
        return self


# ── 响应体 ──

class AbilityGap(BaseModel):
    """能力差距项"""
    skill: str = Field(description="技能名称")
    importance: str = Field(description="重要性：必须/加分")
    difficulty: str = Field(description="学习难度：低/中/高")
    description: str = Field(description="技能说明")


class LearningStage(BaseModel):
    """学习阶段"""
    stage: str = Field(description="阶段名称")
    focus: str = Field(description="阶段核心目标")
    tasks: list[str] = Field(description="具体学习任务")
    milestone: str = Field(description="阶段里程碑")


class RecommendedProject(BaseModel):
    """推荐实战项目"""
    name: str = Field(description="项目名称")
    description: str = Field(description="项目描述")
    tech_stack: list[str] = Field(description="技术栈")
    difficulty: str = Field(description="难度：入门/中级/进阶")


class GrowthPlanResult(BaseModel):
    """成长规划结果"""
    current_situation: str = Field(description="当前现状分析")
    ability_gaps: list[AbilityGap] = Field(default_factory=list, description="能力差距")
    learning_roadmap: list[LearningStage] = Field(default_factory=list, description="学习路线图")
    recommended_projects: list[RecommendedProject] = Field(default_factory=list, description="推荐实战项目")
    recommended_resources: list[str] = Field(default_factory=list, description="推荐学习资源")
    interview_prep_tips: list[str] = Field(default_factory=list, description="面试准备建议")
    expected_timeline: str = Field(description="预计达标时间")


class GrowthPlanResponse(BaseModel):
    """成长规划响应"""
    id: Optional[int] = Field(default=None, description="规划记录ID")
    user_id: Optional[int] = Field(default=None, description="用户ID")
    target_job: str = Field(description="目标岗位")
    result: GrowthPlanResult = Field(description="规划结果")
    is_mock: bool = Field(default=False, description="是否为模拟数据")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")


class GrowthPlanHistoryItem(BaseModel):
    """历史规划记录列表项"""
    id: int
    user_id: Optional[int] = None
    target_job: str
    expected_timeline: str
    created_at: Optional[datetime] = None

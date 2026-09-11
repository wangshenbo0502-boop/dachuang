"""
文件名称：resume.py
文件作用：简历优化相关 Pydantic 数据结构定义。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ── 请求体 ──

class ResumeOptimizationRequest(BaseModel):
    """简历优化请求"""
    user_id: Optional[int] = Field(default=None, description="用户ID（如果已保存用户信息）")

    # 直接传入信息
    name: Optional[str] = Field(default=None, max_length=50, description="姓名")
    target_job: str = Field(..., min_length=1, max_length=100, description="目标岗位（必填）")
    skills: list[dict] = Field(default_factory=list, description="技能列表")
    projects: list[dict] = Field(default_factory=list, description="项目列表")
    original_resume: Optional[str] = Field(default="", max_length=10000, description="原始简历文本（可选）")

    @model_validator(mode="after")
    def require_user_or_name(self) -> "ResumeOptimizationRequest":
        if self.user_id is None and not self.name:
            raise ValueError("未提供 user_id 时，name 为必填字段")
        return self


# ── 响应体 ──

class OptimizedProject(BaseModel):
    """优化后的项目经历"""
    project_name: str = Field(description="项目名称")
    original: str = Field(description="原始描述")
    optimized: str = Field(description="优化后的描述")
    highlight_tags: list[str] = Field(default_factory=list, description="亮点标签")


class OptimizedSkill(BaseModel):
    """优化后的技能描述"""
    original: str = Field(description="原始描述")
    optimized: str = Field(description="优化后的描述")


class ResumeOptimizationResult(BaseModel):
    """简历优化结果"""
    optimized_projects: list[OptimizedProject] = Field(default_factory=list, description="优化后的项目经历")
    optimized_skills: list[OptimizedSkill] = Field(default_factory=list, description="优化后的技能描述")
    overall_suggestions: list[str] = Field(default_factory=list, description="整体建议")
    personal_summary: str = Field(default="", description="优化后的个人简介")
    resume_score: int = Field(description="简历评分0-100")


class ResumeOptimizationResponse(BaseModel):
    """简历优化响应"""
    id: Optional[int] = Field(default=None, description="优化记录ID")
    user_id: Optional[int] = Field(default=None, description="用户ID")
    target_job: str = Field(description="目标岗位")
    result: ResumeOptimizationResult = Field(description="优化结果")
    is_mock: bool = Field(default=False, description="是否为模拟数据")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")


class ResumeOptimizationHistoryItem(BaseModel):
    """历史优化记录列表项"""
    id: int
    user_id: Optional[int] = None
    target_job: str
    resume_score: int
    created_at: Optional[datetime] = None

"""
文件名称：analysis.py
文件作用：就业画像分析相关 Pydantic 数据结构定义。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 请求体 ──

class ProfileAnalysisRequest(BaseModel):
    """就业画像分析请求

    可以传入user_id使用已保存的用户信息，也可以直接传入用户信息进行分析。
    """
    user_id: Optional[int] = Field(default=None, description="用户ID（如果已保存用户信息）")

    # 直接传入信息（不使用user_id时）
    name: Optional[str] = Field(default=None, max_length=50, description="姓名")
    school: Optional[str] = Field(default=None, max_length=100, description="学校")
    major: Optional[str] = Field(default=None, max_length=100, description="专业")
    grade: Optional[str] = Field(default=None, max_length=30, description="年级")
    bio: Optional[str] = Field(default="", max_length=2000, description="自我评价")
    skills: list[dict] = Field(default_factory=list, description="技能列表")
    projects: list[dict] = Field(default_factory=list, description="项目列表")
    target_job: Optional[str] = Field(default=None, max_length=100, description="目标岗位（可选）")


# ── 响应体 ──

class SkillAssessment(BaseModel):
    """技能评估分项"""
    programming_foundation: int = Field(description="编程基础评分")
    framework_usage: int = Field(description="框架使用能力评分")
    database_skill: int = Field(description="数据库能力评分")
    engineering_practice: int = Field(description="工程实践能力评分")
    project_experience: int = Field(description="项目经验评分")


class RecommendedDirection(BaseModel):
    """推荐方向"""
    job_title: str = Field(description="岗位名称")
    match_rate: int = Field(description="匹配度0-100")


class ProfileAnalysisResult(BaseModel):
    """就业画像分析结果"""
    profile_summary: str = Field(description="整体画像总结")
    technical_direction: str = Field(description="最适合的技术方向")
    core_advantages: list[str] = Field(description="核心优势列表")
    current_level: str = Field(description="当前水平定位")
    recommended_directions: list[RecommendedDirection] = Field(description="推荐方向列表")
    areas_to_improve: list[str] = Field(description="待提升方面")
    comprehensive_score: int = Field(description="综合评分0-100")
    skill_assessment: SkillAssessment = Field(description="技能分项评估")


class ProfileAnalysisResponse(BaseModel):
    """就业画像分析响应"""
    id: Optional[int] = Field(default=None, description="分析记录ID")
    user_id: Optional[int] = Field(default=None, description="用户ID")
    target_job: str = Field(default="", description="目标岗位")
    result: ProfileAnalysisResult = Field(description="分析结果")
    is_mock: bool = Field(default=False, description="是否为模拟数据（未配置API Key时）")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")


class ProfileAnalysisHistoryItem(BaseModel):
    """历史分析记录列表项"""
    id: int
    user_id: Optional[int] = None
    target_job: str
    technical_direction: str
    comprehensive_score: int
    created_at: Optional[datetime] = None

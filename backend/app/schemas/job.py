"""
文件名称：job.py
文件作用：岗位相关 Pydantic 数据结构定义。
定义岗位列表/详情/匹配的请求体与响应体。
"""

from typing import Optional

from pydantic import BaseModel, Field


# ── 岗位响应 ──

class JobBase(BaseModel):
    """岗位基础信息"""
    job_id: str = Field(description="岗位唯一标识（文件名）")
    title: str = Field(description="岗位名称")
    category: Optional[str] = Field(default=None, description="岗位分类（前端/后端/AI等）")
    tags: list[str] = Field(default_factory=list, description="技能标签")


class JobBrief(JobBase):
    """岗位列表项（简要信息）"""
    snippet: str = Field(default="", description="内容摘要（前200字）")


class JobDetail(JobBase):
    """岗位详情"""
    content: str = Field(description="完整 Markdown 内容")
    metadata: dict = Field(default_factory=dict, description="完整元数据")


# ── 岗位列表响应 ──

class JobListResponse(BaseModel):
    """岗位列表响应"""
    total: int = Field(description="总数量")
    items: list[JobBrief] = Field(default_factory=list)
    keyword: Optional[str] = Field(default=None, description="搜索关键词")


# ── 岗位匹配 ──

class JobMatchRequest(BaseModel):
    """岗位匹配请求"""
    skills: list[str] = Field(description="用户技能列表", min_length=1, max_length=50)
    job_category: Optional[str] = Field(default=None, description="目标岗位分类（可选过滤）")
    top_k: int = Field(default=10, ge=1, le=20, description="返回匹配数量")
    user_id: Optional[int] = Field(default=None, description="用户ID（可选，用于保存匹配历史）")


class MatchedJob(BaseModel):
    """单个匹配岗位"""
    job_id: str
    title: str
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    match_score: float = Field(description="匹配得分（0-100）")
    matched_skills: list[str] = Field(default_factory=list, description="命中的技能")
    missing_skills: list[str] = Field(default_factory=list, description="缺失的技能")
    snippet: str = Field(default="")


class JobMatchResponse(BaseModel):
    """岗位匹配响应"""
    user_skills: list[str]
    total_matches: int
    matches: list[MatchedJob]


# ── 匹配记录 ──

class JobMatchRecordResponse(BaseModel):
    """历史匹配记录响应"""
    id: int
    user_id: Optional[int] = None
    skills: list[str]
    job_id: str
    job_title: str
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    matches: list[MatchedJob]
    created_at: Optional[str] = Field(default=None, description="创建时间")

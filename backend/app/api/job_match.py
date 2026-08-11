"""
文件名称：job_match.py
文件作用：岗位匹配相关 API 接口。
提供岗位搜索、详情查看与技能匹配功能，并持久化匹配历史。

接口列表：
    GET  /api/jobs          - 岗位列表搜索
    GET  /api/jobs/{job_id} - 岗位详情
    POST /api/match         - 岗位技能匹配（保存历史记录）
    GET  /api/match/{match_id} - 查询历史匹配结果
"""

from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.job import JobMatchRecord
from app.schemas.job import (
    JobDetail,
    JobListResponse,
    JobMatchRecordResponse,
    JobMatchRequest,
    JobMatchResponse,
)
from app.services.job_match_service import JobMatchService
from app.utils.exceptions import ResourceNotFoundError
from app.utils.response import success

router = APIRouter()


def serialize_model(model: BaseModel) -> dict[str, Any]:
    """将 Pydantic 模型转换为可直接放入统一响应的数据。"""
    return model.model_dump(mode="json")


# ── 岗位列表搜索 ──

@router.get("/jobs")
def list_jobs(
    keyword: str = Query(default="", description="搜索关键词（如 Java、前端、AI）"),
    category: str = Query(default=None, description="岗位业务分类过滤（前端/后端/AI/数据/运维/测试/产品/运营/安全）"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=50, description="每页数量"),
) -> dict[str, Any]:
    """GET /api/jobs — 岗位列表搜索"""
    service = JobMatchService.instance()
    result = service.search_jobs(keyword=keyword, category=category, page=page, page_size=page_size)
    return success(serialize_model(result), message="岗位列表获取成功")


# ── 岗位详情 ──

@router.get("/jobs/{job_id}")
def get_job_detail(job_id: str = Path(description="岗位ID（文件名，如 Java后端开发工程师）")) -> dict[str, Any]:
    """GET /api/jobs/{job_id} — 岗位详情"""
    service = JobMatchService.instance()
    detail: JobDetail | None = service.get_job_detail(job_id)
    if not detail:
        raise ResourceNotFoundError(message=f"岗位「{job_id}」不存在")
    return success(serialize_model(detail), message="岗位详情获取成功")


# ── 岗位智能匹配 ──

@router.post("/match")
def match_jobs(
    request: JobMatchRequest,
    database_session: Session = Depends(get_db),
) -> dict[str, Any]:
    """POST /api/match — 岗位技能匹配
    示例请求：
    {
        "skills": ["Java", "Spring Boot", "MySQL", "Redis", "Git"],
        "job_category": "后端",
        "top_k": 10,
        "user_id": 1
    }
    """
    service = JobMatchService.instance()
    result: JobMatchResponse = service.match_jobs(request)
    # 持久化匹配历史（仅当有匹配结果时）
    record_id = None
    if result.matches:
        record = service.save_match_record(database_session, request, result)
        record_id = record.id
    return success(
        {
            "user_skills": result.user_skills,
            "total_matches": result.total_matches,
            "matches": [m.model_dump(mode="json") for m in result.matches],
            "record_id": record_id,
        },
        message="岗位匹配完成",
    )


# ── 历史匹配结果查询 ──

@router.get("/match/{match_id}")
def get_match_history(
    match_id: int = Path(ge=1, description="匹配记录ID"),
    database_session: Session = Depends(get_db),
) -> dict[str, Any]:
    """GET /api/match/{match_id} — 查询历史匹配结果"""
    record = database_session.get(JobMatchRecord, match_id)
    if not record:
        raise ResourceNotFoundError(message=f"匹配记录 {match_id} 不存在")
    response = JobMatchRecordResponse(
        id=record.id,
        user_id=record.user_id,
        skills=record.skills,
        job_id=record.job_id,
        job_title=record.job_title,
        match_score=record.match_score,
        matched_skills=record.matched_skills,
        missing_skills=record.missing_skills,
        matches=record.result,
        created_at=record.created_at.isoformat() if record.created_at else None,
    )
    return success(serialize_model(response), message="匹配记录获取成功")

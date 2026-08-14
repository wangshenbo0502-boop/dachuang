"""
文件名称：streaming.py
文件作用：SSE 流式响应 API 端点。
为 AI 分析、简历优化、成长规划、岗位匹配提供流式输出能力，
前端可实时展示 AI 打字机效果，提升用户体验。
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai.deepseek_client import DeepSeekClient
from app.ai.prompts import (
    SystemPrompts,
    ProfileAnalysisPrompts,
    ResumeOptimizationPrompts,
    GrowthPlanningPrompts,
    JobMatchPrompts,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.analysis import ProfileAnalysisRequest
from app.schemas.resume import ResumeOptimizationRequest
from app.schemas.growth import GrowthPlanRequest
from app.utils.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/api/stream", tags=["AI流式响应"])


def _sse_event(data: str, event: str = "message") -> str:
    """构造SSE事件格式"""
    return f"event: {event}\ndata: {data}\n\n"


async def _stream_generator(messages: list[dict], ai_client: DeepSeekClient) -> Any:
    """通用SSE流式生成器"""
    try:
        # 发送开始事件
        yield _sse_event(json.dumps({"type": "start", "message": "AI分析开始..."}), "start")

        full_text = ""
        for chunk in ai_client.chat_stream(messages):
            full_text += chunk
            yield _sse_event(json.dumps({"type": "chunk", "content": chunk}), "chunk")

        # 尝试解析JSON结果
        try:
            import re
            text = full_text
            text = re.sub(r"^```json\s*", "", text.strip())
            text = re.sub(r"\s*```$", "", text.strip())
            result = json.loads(text)
            yield _sse_event(
                json.dumps({"type": "complete", "result": result, "message": "分析完成"}),
                "complete",
            )
        except json.JSONDecodeError:
            yield _sse_event(
                json.dumps({"type": "complete", "raw_text": full_text, "message": "分析完成（非JSON格式）"}),
                "complete",
            )

    except Exception as e:
        yield _sse_event(
            json.dumps({"type": "error", "message": f"AI服务异常: {str(e)}"}),
            "error",
        )


def _resolve_user(user_id: int, db: Session) -> dict:
    """解析用户信息为字典"""
    user = db.get(User, user_id)
    if not user:
        raise ResourceNotFoundError(f"用户 {user_id} 不存在")
    return {
        "name": user.name,
        "school": user.school,
        "major": user.major,
        "grade": user.grade,
        "bio": user.bio,
        "skills": [
            {"name": s.name, "proficiency": s.proficiency, "description": s.description}
            for s in user.skills
        ],
        "projects": [
            {
                "name": p.name,
                "role": p.role,
                "description": p.description,
                "tech_stack": p.tech_stack or [],
            }
            for p in user.projects
        ],
        "competitions": [
            {
                "name": c.name,
                "level": c.level,
                "award": c.award,
                "description": c.description,
            }
            for c in user.competitions
        ],
        "internships": [
            {
                "company": i.company,
                "position": i.position,
                "description": i.description,
                "tech_stack": i.tech_stack or [],
            }
            for i in user.internships
        ],
    }


# ── 就业画像分析（流式） ──

@router.post("/analysis")
async def stream_analysis(
    request: Request,
    body: ProfileAnalysisRequest,
    db: Session = Depends(get_db),
):
    """POST /api/stream/analysis — 就业画像分析（流式SSE）"""
    ai_client = DeepSeekClient.instance()

    if body.user_id:
        user_info = _resolve_user(body.user_id, db)
    else:
        user_info = {
            "name": body.name or "同学",
            "school": body.school or "未填写",
            "major": body.major or "未填写",
            "grade": body.grade or "未填写",
            "bio": body.bio or "",
            "skills": [s.model_dump() for s in (body.skills or [])],
            "projects": [p.model_dump() for p in (body.projects or [])],
            "competitions": [],
            "internships": [],
        }

    system_prompt = SystemPrompts.profile_analyst()
    user_prompt = ProfileAnalysisPrompts.build_user_prompt(
        name=user_info["name"],
        school=user_info["school"],
        major=user_info["major"],
        grade=user_info["grade"],
        bio=user_info["bio"],
        skills=user_info["skills"],
        projects=user_info["projects"],
        target_job=body.target_job or "",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return StreamingResponse(
        _stream_generator(messages, ai_client),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── 简历优化（流式） ──

@router.post("/resume")
async def stream_resume(
    request: Request,
    body: ResumeOptimizationRequest,
    db: Session = Depends(get_db),
):
    """POST /api/stream/resume — 简历优化（流式SSE）"""
    ai_client = DeepSeekClient.instance()

    if body.user_id:
        user_info = _resolve_user(body.user_id, db)
    else:
        user_info = {
            "name": body.name or "同学",
            "skills": body.skills or [],
            "projects": body.projects or [],
            "internships": [],
        }

    system_prompt = SystemPrompts.resume_optimizer()
    user_prompt = ResumeOptimizationPrompts.build_user_prompt(
        name=user_info["name"],
        target_job=body.target_job,
        skills=user_info["skills"],
        projects=user_info["projects"],
        original_resume=body.original_resume or "",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return StreamingResponse(
        _stream_generator(messages, ai_client),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── 成长规划（流式） ──

@router.post("/growth")
async def stream_growth(
    request: Request,
    body: GrowthPlanRequest,
    db: Session = Depends(get_db),
):
    """POST /api/stream/growth — 成长规划（流式SSE）"""
    ai_client = DeepSeekClient.instance()

    if body.user_id:
        user_info = _resolve_user(body.user_id, db)
    else:
        user_info = {
            "name": body.name or "同学",
            "major": body.major or "计算机相关专业",
            "grade": body.grade or "未填写",
            "skills": body.skills or [],
            "projects": body.projects or [],
        }

    system_prompt = SystemPrompts.growth_planner()
    user_prompt = GrowthPlanningPrompts.build_user_prompt(
        name=user_info["name"],
        major=user_info["major"],
        grade=user_info["grade"],
        target_job=body.target_job,
        skills=user_info["skills"],
        projects=user_info["projects"],
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return StreamingResponse(
        _stream_generator(messages, ai_client),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
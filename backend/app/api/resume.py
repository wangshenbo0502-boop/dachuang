"""
文件名称：resume.py
文件作用：简历优化API接口。
提供AI简历优化、历史记录查询功能。
"""

from typing import Any

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.resume import (
    ResumeOptimizationRequest,
    ResumeOptimizationResponse,
    ResumeOptimizationHistoryItem,
)
from app.services.resume_service import ResumeService
from app.utils.response import success

router = APIRouter(prefix="/api/resume", tags=["AI简历优化"])


def serialize_model(model: BaseModel) -> dict[str, Any]:
    """将Pydantic模型转换为可序列化字典"""
    return model.model_dump(mode="json")


@router.post("", response_model_exclude_none=True)
def optimize_resume(
    request: ResumeOptimizationRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """POST /api/resume - 执行简历优化

    可以传入user_id使用已保存的用户信息，也可以直接传入用户信息进行优化。
    target_job为必填字段，指定目标岗位。

    示例请求：
    {
        "user_id": 1,
        "target_job": "Java后端开发工程师"
    }
    """
    service = ResumeService(db)
    result = service.optimize_resume(request)
    return success(serialize_model(result), message="简历优化完成")


@router.get("/{optimization_id}")
def get_optimization(
    optimization_id: int = Path(ge=1, description="优化记录ID"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """GET /api/resume/{optimization_id} - 获取优化记录详情"""
    service = ResumeService(db)
    result = service.get_optimization(optimization_id)
    return success(serialize_model(result), message="获取优化记录成功")


@router.get("/user/{user_id}")
def get_user_optimizations(
    user_id: int = Path(ge=1, description="用户ID"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """GET /api/resume/user/{user_id} - 获取用户的历史优化记录列表"""
    service = ResumeService(db)
    results = service.get_user_optimizations(user_id)
    return success(
        [serialize_model(r) for r in results],
        message="获取历史优化记录成功",
    )

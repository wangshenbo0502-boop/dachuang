"""
文件名称：resume.py
文件作用：简历优化API接口。
提供AI简历优化、历史记录查询功能。
"""

from typing import Any

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_owner
from app.models.user import User
from app.database.session import get_db
from app.schemas.resume import (
    ResumeOptimizationRequest,
    ResumeOptimizationResponse,
    ResumeOptimizationHistoryItem,
    ResumeVersionCreate, ResumeVersionUpdate,
)
from app.services.resume_service import ResumeService
from app.utils.response import success

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/resume", tags=["AI简历优化"])


def serialize_model(model: BaseModel) -> dict[str, Any]:
    """将Pydantic模型转换为可序列化字典"""
    return model.model_dump(mode="json")


@router.post("/versions")
def create_resume_version(request: ResumeVersionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_owner(request.user_id, current_user)
    return success(serialize_model(ResumeService(db).create_version(request)), message="简历版本创建成功")


@router.get("/versions/user/{user_id}")
def list_resume_versions(user_id: int = Path(ge=1), db: Session = Depends(get_db)) -> dict[str, Any]:
    return success([serialize_model(item) for item in ResumeService(db).list_versions(user_id)], message="获取简历版本成功")


@router.get("/versions/{version_id}")
def get_resume_version(version_id: int = Path(ge=1), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    version = ResumeService(db).get_version(version_id)
    require_owner(version.user_id, current_user)
    return success(serialize_model(version), message="获取简历版本成功")


@router.put("/versions/{version_id}")
def update_resume_version(version_id: int, request: ResumeVersionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_owner(ResumeService(db).get_version(version_id).user_id, current_user)
    return success(serialize_model(ResumeService(db).update_version(version_id, request)), message="简历版本已保存")


@router.post("", response_model_exclude_none=True)
def optimize_resume(
    request: ResumeOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    if request.user_id is not None:
        require_owner(request.user_id, current_user)
    request = request.model_copy(update={'user_id': current_user.id})
    result = service.optimize_resume(request)
    return success(serialize_model(result), message="简历优化完成")


@router.get("/{optimization_id}")
def get_optimization(
    optimization_id: int = Path(ge=1, description="优化记录ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """GET /api/resume/{optimization_id} - 获取优化记录详情"""
    service = ResumeService(db)
    result = service.get_optimization(optimization_id)
    require_owner(result.user_id, current_user)
    return success(serialize_model(result), message="获取优化记录成功")


@router.get("/user/{user_id}")
def get_user_optimizations(
    user_id: int = Path(ge=1, description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """GET /api/resume/user/{user_id} - 获取用户的历史优化记录列表"""
    service = ResumeService(db)
    results = service.get_user_optimizations(user_id)
    return success(
        [serialize_model(r) for r in results],
        message="获取历史优化记录成功",
    )

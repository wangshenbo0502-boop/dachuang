"""
文件名称：growth.py
文件作用：成长规划API接口。
提供AI成长规划生成、历史记录查询功能。
"""

from typing import Any

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.growth import (
    GrowthPlanRequest,
    GrowthPlanResponse,
    GrowthPlanHistoryItem,
)
from app.services.growth_service import GrowthService
from app.utils.response import success

router = APIRouter(prefix="/api/growth", tags=["AI成长规划"])


def serialize_model(model: BaseModel) -> dict[str, Any]:
    """将Pydantic模型转换为可序列化字典"""
    return model.model_dump(mode="json")


@router.post("", response_model_exclude_none=True)
def generate_growth_plan(
    request: GrowthPlanRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """POST /api/growth - 生成成长规划

    可以传入user_id使用已保存的用户信息，也可以直接传入用户信息生成规划。
    target_job为必填字段，指定目标岗位。

    示例请求：
    {
        "user_id": 1,
        "target_job": "Java后端开发工程师"
    }
    """
    service = GrowthService(db)
    result = service.generate_plan(request)
    return success(serialize_model(result), message="成长规划生成完成")


@router.get("/{plan_id}")
def get_growth_plan(
    plan_id: int = Path(ge=1, description="规划记录ID"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """GET /api/growth/{plan_id} - 获取规划记录详情"""
    service = GrowthService(db)
    result = service.get_plan(plan_id)
    return success(serialize_model(result), message="获取规划记录成功")


@router.get("/user/{user_id}")
def get_user_growth_plans(
    user_id: int = Path(ge=1, description="用户ID"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """GET /api/growth/user/{user_id} - 获取用户的历史规划记录列表"""
    service = GrowthService(db)
    results = service.get_user_plans(user_id)
    return success(
        [serialize_model(r) for r in results],
        message="获取历史规划记录成功",
    )

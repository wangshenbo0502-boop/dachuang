"""
文件名称：analysis.py
文件作用：就业画像分析API接口。
提供AI就业画像分析、历史记录查询功能。
"""

from typing import Any

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analysis import (
    ProfileAnalysisRequest,
    ProfileAnalysisResponse,
    ProfileAnalysisHistoryItem,
)
from app.services.analysis_service import AnalysisService
from app.utils.response import success

router = APIRouter(prefix="/api/analysis", tags=["AI就业画像分析"])


def serialize_model(model: BaseModel) -> dict[str, Any]:
    """将Pydantic模型转换为可序列化字典"""
    return model.model_dump(mode="json")


@router.post("", response_model_exclude_none=True)
def analyze_profile(
    request: ProfileAnalysisRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """POST /api/analysis - 执行就业画像分析

    可以传入user_id使用已保存的用户信息，也可以直接传入用户信息进行分析。

    示例请求（使用已保存用户）：
    {
        "user_id": 1,
        "target_job": "Java后端开发工程师"
    }

    示例请求（直接传入信息）：
    {
        "name": "张三",
        "school": "某某大学",
        "major": "计算机科学与技术",
        "grade": "大三",
        "bio": "热爱编程",
        "skills": [
            {"name": "Java", "proficiency": "掌握", "description": "熟悉Java基础"},
            {"name": "SpringBoot", "proficiency": "熟悉", "description": ""}
        ],
        "projects": [
            {"name": "校园管理系统", "role": "后端开发", "description": "负责后端接口开发", "tech_stack": ["SpringBoot", "MySQL"]}
        ]
    }
    """
    service = AnalysisService(db)
    result = service.analyze_profile(request)
    return success(serialize_model(result), message="就业画像分析完成")


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: int = Path(ge=1, description="分析记录ID"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """GET /api/analysis/{analysis_id} - 获取分析记录详情"""
    service = AnalysisService(db)
    result = service.get_analysis(analysis_id)
    return success(serialize_model(result), message="获取分析记录成功")


@router.get("/user/{user_id}")
def get_user_analyses(
    user_id: int = Path(ge=1, description="用户ID"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """GET /api/analysis/user/{user_id} - 获取用户的历史分析记录列表"""
    service = AnalysisService(db)
    results = service.get_user_analyses(user_id)
    return success(
        [serialize_model(r) for r in results],
        message="获取历史分析记录成功",
    )

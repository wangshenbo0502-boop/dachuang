"""
文件名称：user.py
文件作用：提供学生资料、技能、项目经历和 AI 用户上下文的 REST API。
"""

from typing import Any

from fastapi import APIRouter, Depends, Path, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import (
    StudentContextResponse,
    UserCreate,
    UserProfileResponse,
    UserProjectsReplace,
    UserSkillsReplace,
    UserUpdate,
)
from app.services.user_service import UserService
from app.utils.response import success

router = APIRouter(prefix="/api/users", tags=["学生资料"])


def serialize_model(model: BaseModel) -> dict[str, Any]:
    """将 Pydantic 模型转换为可直接放入统一响应的数据。"""
    return model.model_dump(mode="json")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, database_session: Session = Depends(get_db)) -> dict[str, Any]:
    """创建学生基本资料。"""
    user = UserService(database_session).create_user(user_data)
    response = UserProfileResponse.model_validate(user)
    return success(serialize_model(response), message="学生资料创建成功")


@router.get("/{user_id}")
def get_user(
    user_id: int = Path(ge=1),
    database_session: Session = Depends(get_db),
) -> dict[str, Any]:
    """获取包含技能和项目经历的学生资料。"""
    user = UserService(database_session).get_user(user_id)
    response = UserProfileResponse.model_validate(user)
    return success(serialize_model(response))


@router.put("/{user_id}")
def update_user(
    user_data: UserUpdate,
    user_id: int = Path(ge=1),
    database_session: Session = Depends(get_db),
) -> dict[str, Any]:
    """更新学生基本资料。"""
    user = UserService(database_session).update_user(user_id, user_data)
    response = UserProfileResponse.model_validate(user)
    return success(serialize_model(response), message="学生资料更新成功")


@router.put("/{user_id}/skills")
def replace_skills(
    skill_data: UserSkillsReplace,
    user_id: int = Path(ge=1),
    database_session: Session = Depends(get_db),
) -> dict[str, Any]:
    """整组替换学生技能。"""
    user = UserService(database_session).replace_skills(user_id, skill_data)
    response = UserProfileResponse.model_validate(user)
    return success(
        [serialize_model(skill) for skill in response.skills],
        message="学生技能更新成功",
    )


@router.put("/{user_id}/projects")
def replace_projects(
    project_data: UserProjectsReplace,
    user_id: int = Path(ge=1),
    database_session: Session = Depends(get_db),
) -> dict[str, Any]:
    """整组替换学生项目经历。"""
    user = UserService(database_session).replace_projects(user_id, project_data)
    response = UserProfileResponse.model_validate(user)
    return success(
        [serialize_model(project) for project in response.projects],
        message="学生项目经历更新成功",
    )


@router.get("/{user_id}/context")
def get_user_context(
    user_id: int = Path(ge=1),
    database_session: Session = Depends(get_db),
) -> dict[str, Any]:
    """获取供 AI 模块使用的结构化学生上下文。"""
    context = UserService(database_session).get_user_context(user_id)
    response = StudentContextResponse.model_validate(context)
    return success(serialize_model(response))

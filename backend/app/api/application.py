"""BOSS 直聘投递助手 API。"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.application import JobApplication
from app.models.user import User
from app.schemas.application import (
    ApplicationAutomationResponse,
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
)
from app.services.boss_automation_service import BossAutomationError, boss_automation_service
from app.utils.exceptions import AppException, ResourceNotFoundError
from app.utils.response import success

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    prefix="/api/applications",
    tags=["BOSS直聘投递助手"],
)


def serialize(model: JobApplication) -> dict[str, Any]:
    return JobApplicationResponse(
        id=model.id,
        user_id=model.user_id,
        job_id=model.job_id,
        job_title=model.job_title,
        platform=model.platform,
        boss_url=model.boss_url,
        status=model.status,
        greeting=model.greeting,
        resume_version_id=model.resume_version_id,
        note=model.note,
        applied_at=model.applied_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
        automation_status=model.automation_status,
        automation_error=model.automation_error,
    ).model_dump(mode="json")


@router.get("")
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    records = db.scalars(
        select(JobApplication)
        .where(JobApplication.user_id == current_user.id)
        .order_by(JobApplication.updated_at.desc(), JobApplication.id.desc())
    ).all()
    return success([serialize(item) for item in records], message="获取投递记录成功")


@router.post("")
def create_application(
    request: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    record = JobApplication(
        user_id=current_user.id,
        job_id=request.job_id,
        job_title=request.job_title,
        boss_url=str(request.boss_url),
        greeting=request.greeting,
        resume_version_id=request.resume_version_id,
        note=request.note,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return success(serialize(record), message="投递准备已保存")


@router.patch("/{application_id}")
def update_application(
    request: JobApplicationUpdate,
    application_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    record = db.get(JobApplication, application_id)
    if not record or record.user_id != current_user.id:
        raise ResourceNotFoundError(message="投递记录不存在")
    record.status = request.status
    if request.note is not None:
        record.note = request.note
    if request.status == "applied" and record.applied_at is None:
        record.applied_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return success(serialize(record), message="投递状态已更新")


@router.post("/{application_id}/automation/start")
async def start_automation(
    application_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    record = db.get(JobApplication, application_id)
    if not record or record.user_id != current_user.id:
        raise ResourceNotFoundError(message="投递记录不存在")
    try:
        result = await boss_automation_service.start(record)
        record.automation_status = result["status"]
        record.automation_error = ""
        if result["status"] == "ready_for_user_confirm":
            record.status = "opened"
        db.commit()
        response = ApplicationAutomationResponse(**result).model_dump(mode="json")
        return success(response, message=response["message"])
    except BossAutomationError as exc:
        record.automation_status = "error"
        record.automation_error = str(exc)
        db.commit()
        raise AppException(str(exc), code=4221, status_code=422) from exc


@router.get("/{application_id}/automation/status")
async def automation_status(
    application_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    record = db.get(JobApplication, application_id)
    if not record or record.user_id != current_user.id:
        raise ResourceNotFoundError(message="投递记录不存在")
    result = await boss_automation_service.status(current_user.id)
    return success(
        {
            "status": result["status"],
            "message": record.automation_error or "浏览器会话状态正常",
            "url": result.get("url", ""),
            "greeting_filled": False,
        }
    )

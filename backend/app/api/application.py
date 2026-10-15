"""外部投递记录 API：学生在 BOSS 直聘等平台手动投递后在此跟进状态。"""

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.application import JobApplication
from app.models.user import User
from app.models.resume import Resume
from app.schemas.application import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
)
from app.utils.exceptions import AppException, ResourceNotFoundError
from app.utils.response import success

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    prefix="/api/applications",
    tags=["外部投递记录"],
)


def validate_boss_url(url: str) -> None:
    """Accept only concrete HTTPS zhipin.com job pages without credentials or custom ports."""
    try:
        parsed = urlparse(url)
        port = parsed.port
    except ValueError as exc:
        raise AppException("请填写有效的 BOSS 直聘岗位链接", code=4221, status_code=422) from exc
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        raise AppException("请填写 HTTPS 的 BOSS 直聘岗位链接，不要包含账号或自定义端口", code=4221, status_code=422)
    host = parsed.hostname or ""
    if not (host == "zhipin.com" or host.endswith(".zhipin.com")):
        raise AppException("岗位链接只支持 zhipin.com", code=4221, status_code=422)
    if not parsed.path.strip("/"):
        raise AppException("请填写具体岗位链接，不要使用 BOSS 首页", code=4221, status_code=422)


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
    if request.resume_version_id is not None:
        version = db.get(Resume, request.resume_version_id)
        if not version or version.user_id != current_user.id:
            raise ResourceNotFoundError("简历版本不存在")
    validate_boss_url(str(request.boss_url))
    existing = db.scalar(select(JobApplication).where(
        JobApplication.user_id == current_user.id,
        JobApplication.boss_url == str(request.boss_url),
        JobApplication.resume_version_id == request.resume_version_id,
    ).order_by(JobApplication.id.desc()))
    if existing:
        return success(serialize(existing), message="该简历已有此岗位的投递记录")
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

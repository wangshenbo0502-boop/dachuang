"""Persistent interactions joining resources, job gaps and growth plans."""
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.activity import GrowthTask, ResourceEvent
from app.models.user import User
from app.services.insight_service import InsightService
from app.services.job_match_service import JobMatchService
from app.knowledge.skill_synonyms import normalize_skill
from app.utils.exceptions import AppException, ResourceNotFoundError
from app.utils.response import success

router = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)], tags=["IT 求职行动"])


def serialize(record):
    return {column.name: (value.isoformat() if isinstance(value, datetime) else value)
            for column in record.__table__.columns
            for value in [getattr(record, column.name)]}


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    target_job: str = Field(default="", max_length=100)
    source_key: str = Field(default="", max_length=500)
    resource_query: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def valid_title(self):
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("任务名称不能为空")
        return self


class TaskUpdate(BaseModel):
    status: Literal["todo", "doing", "done"] | None = None
    feedback: str | None = Field(default=None, max_length=3000)
    evidence: str | None = Field(default=None, max_length=3000)


@router.get("/growth/tasks/list")
def tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(GrowthTask).where(GrowthTask.user_id == user.id).order_by(GrowthTask.updated_at.desc())).all()
    return success([serialize(row) for row in rows])


@router.post("/growth/tasks")
def add_task(body: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    key = sha256((body.source_key or f"{body.target_job}:{body.title}").encode()).hexdigest()
    query = select(GrowthTask).where(GrowthTask.user_id == user.id, GrowthTask.source_key == key)
    record = db.scalar(query)
    if not record:
        record = GrowthTask(user_id=user.id, **body.model_dump(exclude={"source_key"}), source_key=key)
        db.add(record)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            record = db.scalar(query)
            if not record:
                raise
    return success(serialize(record))


@router.patch("/growth/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.get(GrowthTask, task_id)
    if not record or record.user_id != user.id:
        raise ResourceNotFoundError("任务不存在")
    updates = body.model_dump(exclude_none=True)
    if updates.get("status", record.status) == "done" and not (updates.get("evidence", record.evidence) or "").strip():
        raise AppException("请记录完成产物或学习复盘后再完成任务", code=4222, status_code=422)
    if "status" in updates and updates["status"] != record.status:
        record.completed_at = datetime.now(timezone.utc) if updates["status"] == "done" else None
    for key, value in updates.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return success(serialize(record))


class ResourceSnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore")
    doc_id: str = Field(default="", max_length=300)
    document_id: int | None = None
    title: str = Field(default="", max_length=500)
    content: str = Field(default="", max_length=10000)
    source: str = Field(default="", max_length=2000)
    category: str = Field(default="", max_length=100)
    metadata: dict = Field(default_factory=dict)


class EventUpdate(BaseModel):
    resource_key: str = Field(min_length=1, max_length=100)
    resource: ResourceSnapshot
    favorite: bool | None = None
    read: bool | None = None
    hidden: bool | None = None


@router.get("/resources/events")
def events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(ResourceEvent).where(ResourceEvent.user_id == user.id)).all()
    return success([serialize(row) for row in rows])


@router.put("/resources/events")
def save_event(body: EventUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(ResourceEvent).where(ResourceEvent.user_id == user.id, ResourceEvent.resource_key == body.resource_key)
    record = db.scalar(query)
    if not record:
        record = ResourceEvent(user_id=user.id, resource_key=body.resource_key)
        db.add(record)
    record.resource = body.resource.model_dump()
    for key in ("favorite", "read", "hidden"):
        value = getattr(body, key)
        if value is not None:
            setattr(record, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        record = db.scalar(query)
        if not record:
            raise
        record.resource = body.resource.model_dump()
        for key in ("favorite", "read", "hidden"):
            if getattr(body, key) is not None:
                setattr(record, key, getattr(body, key))
        db.commit()
    return success(serialize(record))


@router.get("/resources/home")
def resource_home():
    return success(InsightService.feed())


@router.get("/career-profile/market-context")
def career_context(target_job: str = "", user: User = Depends(get_current_user)):
    service = JobMatchService.instance()
    jobs = service.search_jobs(keyword=target_job, page_size=30).items
    evidence = {}
    for skill in user.skills:
        if skill.proficiency != "未知":
            evidence.setdefault(normalize_skill(skill.name), []).append(f"用户自述技能：{skill.name}（{skill.proficiency}）")
    for project in user.projects:
        for skill in project.tech_stack or []:
            evidence.setdefault(normalize_skill(skill), []).append(f"项目：{project.name}")
    matrix = {}
    for job in jobs:
        seen = set()
        for skill in job.required_skills:
            normalized = normalize_skill(skill)
            if normalized in seen:
                continue
            seen.add(normalized)
            row = matrix.setdefault(normalized, {"skill": skill, "count": 0, "sources": [], "evidence": evidence.get(normalized, [])})
            row["count"] += 1
            row["sources"].append({"job_id": job.job_id, "title": job.title})
    skills = sorted(matrix.values(), key=lambda row: row["count"], reverse=True)[:16]
    for row in skills:
        row["coverage"] = round(row["count"] / len(jobs) * 100) if jobs else 0
        row["status"] = "已有记录，待核验" if row["evidence"] else "缺少证据"
        row["action"] = f"完成 {row['skill']} 实践并补充可验证成果"
    return success({
        "target_job": target_job, "sample_count": len(jobs),
        "scope": "当前知识库检索样本，非实时全行业招聘统计；技能标签不是已核验能力。",
        "skills": skills, "jobs": [job.model_dump() for job in jobs[:6]],
        "observed_at": datetime.now(timezone.utc).isoformat(),
    })

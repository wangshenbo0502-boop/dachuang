"""Routes never registered unless the internal administration switch is enabled."""
from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.recruitment import RecruiterProfile, RecruitmentJob, RecruitmentApplication
from app.models.admin_receipt import BusinessAdminReceipt
from app.internal_admin.security import require_service_scope
from app.internal_admin.schemas import AccountStatusCommand, JobModerationCommand
from app.internal_admin.commands import execute, receipt_dto
from app.internal_admin.queries import envelope, account_dto, recruiter_dto, job_dto, application_dto, page_data

router = APIRouter(prefix="/internal/admin/v1", tags=["internal-admin"])


def pagination(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return page, page_size


@router.get("/overview", dependencies=[Depends(require_service_scope("overview:read"))])
def overview(db: Session = Depends(get_db)):
    def count(model, *conditions):
        return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0
    public = select(func.count()).select_from(RecruitmentJob).join(Account, Account.id == RecruitmentJob.recruiter_id).where(
        RecruitmentJob.status == "published", RecruitmentJob.moderation_status == "allowed", Account.is_active.is_(True))
    states = db.execute(select(RecruitmentApplication.status, func.count()).group_by(RecruitmentApplication.status)).all()
    return envelope({"student_total": count(Account, Account.role == "student"),
        "recruiter_total": count(Account, Account.role == "recruiter"),
        "active_account_total": count(Account, Account.is_active.is_(True)),
        "published_job_total": db.scalar(public) or 0,
        "blocked_job_total": count(RecruitmentJob, RecruitmentJob.moderation_status == "blocked"),
        "applications_by_status": dict(states), "as_of": datetime.now(timezone.utc)}, request_id=str(uuid4()))


@router.get("/accounts", dependencies=[Depends(require_service_scope("accounts:read"))])
def accounts(role: str = "", is_active: bool | None = None, keyword: str = Query("", max_length=100),
             paging=Depends(pagination), db: Session = Depends(get_db)):
    stmt = select(Account)
    if role:
        stmt = stmt.where(Account.role == role)
    if is_active is not None:
        stmt = stmt.where(Account.is_active == is_active)
    if keyword:
        stmt = stmt.where(or_(Account.username.contains(keyword, autoescape=True), Account.email.contains(keyword, autoescape=True)))
    return envelope(page_data(db, stmt.order_by(Account.created_at.desc(), Account.id.desc()), *paging, account_dto), request_id=str(uuid4()))


@router.get("/accounts/{account_id}", dependencies=[Depends(require_service_scope("accounts:read"))])
def account(account_id: int, db: Session = Depends(get_db)):
    row = db.get(Account, account_id)
    if not row:
        raise HTTPException(404, "账号不存在")
    return envelope(account_dto(row), request_id=str(uuid4()))


@router.get("/recruiters", dependencies=[Depends(require_service_scope("recruiters:read"))])
def recruiters(keyword: str = Query("", max_length=100), city: str = "", is_active: bool | None = None,
               paging=Depends(pagination), db: Session = Depends(get_db)):
    stmt = select(Account).outerjoin(RecruiterProfile, RecruiterProfile.account_id == Account.id).where(Account.role == "recruiter")
    if keyword:
        stmt = stmt.where(or_(Account.username.contains(keyword, autoescape=True), RecruiterProfile.company_name.contains(keyword, autoescape=True)))
    if city:
        stmt = stmt.where(RecruiterProfile.city.contains(city, autoescape=True))
    if is_active is not None:
        stmt = stmt.where(Account.is_active == is_active)
    return envelope(page_data(db, stmt.order_by(Account.created_at.desc(), Account.id.desc()), *paging, lambda x: recruiter_dto(db, x)), request_id=str(uuid4()))


@router.get("/recruiters/{account_id}", dependencies=[Depends(require_service_scope("recruiters:read"))])
def recruiter(account_id: int, db: Session = Depends(get_db)):
    row = db.get(Account, account_id)
    if not row or row.role != "recruiter":
        raise HTTPException(404, "招聘者不存在")
    return envelope(recruiter_dto(db, row), request_id=str(uuid4()))


@router.get("/jobs", dependencies=[Depends(require_service_scope("jobs:read"))])
def jobs(recruiter_id: int | None = None, status: str = "", moderation_status: str = "", city: str = "",
         keyword: str = Query("", max_length=100), paging=Depends(pagination), db: Session = Depends(get_db)):
    stmt = select(RecruitmentJob)
    for field, value in (("recruiter_id", recruiter_id), ("status", status), ("moderation_status", moderation_status), ("city", city)):
        if value is not None and value != "":
            stmt = stmt.where(getattr(RecruitmentJob, field) == value)
    if keyword:
        stmt = stmt.where(or_(RecruitmentJob.title.contains(keyword, autoescape=True), RecruitmentJob.company_name.contains(keyword, autoescape=True)))
    return envelope(page_data(db, stmt.order_by(RecruitmentJob.created_at.desc(), RecruitmentJob.id.desc()), *paging, job_dto), request_id=str(uuid4()))


@router.get("/jobs/{job_id}", dependencies=[Depends(require_service_scope("jobs:read"))])
def job(job_id: int, db: Session = Depends(get_db)):
    row = db.get(RecruitmentJob, job_id)
    if not row:
        raise HTTPException(404, "岗位不存在")
    return envelope(job_dto(row), request_id=str(uuid4()))


@router.get("/applications", dependencies=[Depends(require_service_scope("applications:read"))])
def applications(job_id: int | None = None, student_id: int | None = None, recruiter_id: int | None = None,
                 status: str = "", paging=Depends(pagination), db: Session = Depends(get_db)):
    stmt = select(RecruitmentApplication).join(RecruitmentJob)
    for field, value in (("job_id", job_id), ("student_id", student_id), ("status", status)):
        if value is not None and value != "":
            stmt = stmt.where(getattr(RecruitmentApplication, field) == value)
    if recruiter_id is not None:
        stmt = stmt.where(RecruitmentJob.recruiter_id == recruiter_id)
    return envelope(page_data(db, stmt.order_by(RecruitmentApplication.created_at.desc(), RecruitmentApplication.id.desc()),
                              *paging, lambda x: application_dto(db, x)), request_id=str(uuid4()))


@router.post("/accounts/{account_id}/status")
def account_status(account_id: int, body: AccountStatusCommand, command_id: UUID = Header(alias="Idempotency-Key"),
                   actor=Depends(require_service_scope("accounts:status_write"))):
    status, payload = execute(kind="accounts", resource_id=account_id, key=str(command_id), body=body, actor=actor)
    return JSONResponse(status_code=status, content=payload)


@router.post("/jobs/{job_id}/moderation")
def job_moderation(job_id: int, body: JobModerationCommand, command_id: UUID = Header(alias="Idempotency-Key"),
                   actor=Depends(require_service_scope("jobs:moderate"))):
    status, payload = execute(kind="jobs", resource_id=job_id, key=str(command_id), body=body, actor=actor)
    return JSONResponse(status_code=status, content=payload)


@router.get("/commands/{command_id}")
def receipt(command_id: UUID, actor=Depends(require_service_scope("commands:read")), db: Session = Depends(get_db)):
    row = db.get(BusinessAdminReceipt, str(command_id))
    if not row or row.actor_id != actor.id:
        raise HTTPException(404, "凭据不存在")
    return envelope(receipt_dto(row), request_id=str(uuid4()))

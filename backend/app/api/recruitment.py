"""Separate recruiter management and student recruitment APIs."""
from typing import Literal
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_account, get_current_recruiter, get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.recruitment import RecruitmentJob, RecruitmentApplication
from app.models.user import User
from app.schemas.recruitment import RecruiterProfileInput, RecruitmentJobInput, JobStatusInput, ApplyInput, ApplicationUpdateInput
from app.services.recruitment_service import RecruitmentService, serialize, paginate, job_query
from app.utils.response import success

recruiter_router = APIRouter(prefix="/api/recruiter", tags=["招聘者"], dependencies=[Depends(get_current_recruiter)])
student_router = APIRouter(prefix="/api/recruitment", tags=["站内招聘"], dependencies=[Depends(get_current_user)])


@recruiter_router.get("/profile")
def recruiter_profile(account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    return success(RecruitmentService(db).profile(account.id))


@recruiter_router.put("/profile")
def save_profile(body: RecruiterProfileInput, account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    return success(RecruitmentService(db).save_profile(account.id, body), message="企业资料已保存")


@recruiter_router.get("/jobs")
def recruiter_jobs(keyword: str = Query("", max_length=100), status: Literal["", "draft", "published", "closed"] = "",
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50),
    account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    return success(paginate(db, job_query(recruiter_id=account.id, keyword=keyword, status=status), page, page_size))


@recruiter_router.post("/jobs", status_code=201)
def create_job(body: RecruitmentJobInput, account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    return success(RecruitmentService(db).create_job(account.id, body), message="岗位草稿已创建")


@recruiter_router.get("/jobs/{job_id}")
def recruiter_job(job_id: int = Path(ge=1), account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    return success(serialize(RecruitmentService(db).owned_job(job_id, account.id)))


@recruiter_router.put("/jobs/{job_id}")
def edit_job(body: RecruitmentJobInput, job_id: int = Path(ge=1), account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    return success(RecruitmentService(db).edit_job(job_id, account.id, body), message="岗位已保存")


@recruiter_router.post("/jobs/{job_id}/status")
def set_status(body: JobStatusInput, job_id: int = Path(ge=1), account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    return success(RecruitmentService(db).set_job_status(job_id, account.id, body.status), message="岗位已发布" if body.status == "published" else "岗位已下架")


@recruiter_router.delete("/jobs/{job_id}")
def delete_job(job_id: int = Path(ge=1), account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    RecruitmentService(db).delete_job(job_id, account.id)
    return success(None, message="岗位已删除")


@recruiter_router.get("/applications")
def received_applications(job_id: int | None = Query(None, ge=1), status: Literal["", "submitted", "reviewing", "interview", "offered", "rejected", "withdrawn"] = "",
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50), account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    stmt = select(RecruitmentApplication).join(RecruitmentJob).where(RecruitmentJob.recruiter_id == account.id)
    if job_id:
        stmt = stmt.where(RecruitmentApplication.job_id == job_id)
    if status:
        stmt = stmt.where(RecruitmentApplication.status == status)
    return success(paginate(db, stmt.order_by(RecruitmentApplication.created_at.desc(), RecruitmentApplication.id.desc()), page, page_size))


@recruiter_router.patch("/applications/{application_id}")
def process_application(body: ApplicationUpdateInput, application_id: int = Path(ge=1), account: Account = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    service = RecruitmentService(db)
    row = service.owned_application(application_id, recruiter_id=account.id)
    return success(service.update_application(row, body.status, body.feedback), message="处理结果已保存，学生可在站内查看")


@student_router.get("/jobs")
def public_jobs(keyword: str = Query("", max_length=100), category: str = Query("", max_length=30), city: str = Query("", max_length=80),
    page: int = Query(1, ge=1), page_size: int = Query(12, ge=1, le=50), db: Session = Depends(get_db)):
    return success(paginate(db, job_query(keyword=keyword, category=category, city=city), page, page_size))


@student_router.get("/jobs/{job_id}")
def public_job(job_id: int = Path(ge=1), db: Session = Depends(get_db)):
    return success(RecruitmentService(db).public_detail(job_id))


@student_router.post("/jobs/{job_id}/apply", status_code=201)
def apply(body: ApplyInput, job_id: int = Path(ge=1), account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    return success(RecruitmentService(db).apply(job_id, account, body.resume_id, body.note), message="简历已投递")


@student_router.get("/applications")
def my_applications(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50),
    account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    stmt = select(RecruitmentApplication).where(RecruitmentApplication.student_id == account.id)
    return success(paginate(db, stmt.order_by(RecruitmentApplication.created_at.desc(), RecruitmentApplication.id.desc()), page, page_size))


@student_router.post("/applications/{application_id}/withdraw")
def withdraw(application_id: int = Path(ge=1), account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    service = RecruitmentService(db)
    row = service.owned_application(application_id, student_id=account.id)
    return success(service.update_application(row, "withdrawn"), message="投递已撤回")

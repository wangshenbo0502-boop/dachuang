"""Recruitment lifecycle, ownership and consent-bound resume sharing."""
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from sqlalchemy import String, cast, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.account import Account
from app.models.recruitment import RecruiterProfile, RecruitmentJob, RecruitmentApplication
from app.models.resume import Resume
from app.models.user import User
from app.schemas.recruitment import RecruiterProfileInput, RecruitmentJobInput
from app.utils.exceptions import AppException, ResourceNotFoundError

TRANSITIONS = {
    "submitted": {"reviewing", "interview", "rejected", "withdrawn"},
    "reviewing": {"interview", "rejected", "withdrawn"},
    "interview": {"offered", "rejected", "withdrawn"},
    "offered": set(), "rejected": set(), "withdrawn": set(),
}


def serialize(row):
    return jsonable_encoder({column.name: getattr(row, column.name) for column in row.__table__.columns})


def paginate(db, stmt, page, page_size):
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    items = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [serialize(row) for row in items], "total": total, "page": page, "page_size": page_size}


class RecruitmentService:
    def __init__(self, db: Session):
        self.db = db

    def profile(self, account_id: int):
        row = self.db.get(RecruiterProfile, account_id)
        return serialize(row) if row else {"account_id": account_id, **RecruiterProfileInput().model_dump()}

    def save_profile(self, account_id: int, body: RecruiterProfileInput):
        row = self.db.get(RecruiterProfile, account_id)
        if row is None:
            row = RecruiterProfile(account_id=account_id)
            self.db.add(row)
        for key, value in body.model_dump().items():
            setattr(row, key, value)
        self.db.commit()
        return serialize(row)

    def owned_job(self, job_id, recruiter_id):
        row = self.db.scalar(select(RecruitmentJob).where(
            RecruitmentJob.id == job_id, RecruitmentJob.recruiter_id == recruiter_id).with_for_update())
        if row is None:
            raise ResourceNotFoundError("岗位不存在或无权限访问")
        return row

    def public_job(self, job_id):
        # Lock the vacancy until an application is committed, so closing/deleting
        # a vacancy cannot race an accepted application on row-locking databases.
        row = self.db.scalar(select(RecruitmentJob).join(Account, RecruitmentJob.recruiter_id == Account.id).where(
            RecruitmentJob.id == job_id, RecruitmentJob.status == "published", Account.is_active.is_(True)).with_for_update(of=RecruitmentJob))
        if row is None:
            raise ResourceNotFoundError("岗位不存在或已下架")
        return row

    def create_job(self, recruiter_id, body: RecruitmentJobInput):
        row = RecruitmentJob(recruiter_id=recruiter_id, **body.model_dump())
        self.db.add(row)
        self.db.commit()
        return serialize(row)

    def edit_job(self, job_id, recruiter_id, body):
        row = self.owned_job(job_id, recruiter_id)
        if row.status == "published":
            raise AppException("请先下架岗位再编辑", code=5301, status_code=409)
        for key, value in body.model_dump().items():
            setattr(row, key, value)
        self.db.commit()
        return serialize(row)

    def set_job_status(self, job_id, recruiter_id, status):
        row = self.owned_job(job_id, recruiter_id)
        if status == row.status or (status == "closed" and row.status != "published"):
            raise AppException("岗位状态已变化，请刷新后重试", code=5302, status_code=409)
        if status == "published":
            missing = [label for key, label in {"title": "岗位名称", "category": "分类", "city": "城市", "salary": "薪资", "description": "岗位职责", "requirements": "任职要求"}.items() if not getattr(row, key).strip()]
            profile = self.profile(recruiter_id)
            missing.extend(label for key, label in {"company_name": "企业名称", "contact_name": "联系人", "contact_email": "联系邮箱"}.items() if not profile[key].strip())
            if missing:
                raise AppException("发布前请补充：" + "、".join(missing), code=5303)
            row.company_name = profile["company_name"]
            row.published_at = datetime.now(timezone.utc)
        row.status = status
        self.db.commit()
        return serialize(row)

    def delete_job(self, job_id, recruiter_id):
        row = self.owned_job(job_id, recruiter_id)
        exists = self.db.scalar(select(RecruitmentApplication.id).where(RecruitmentApplication.job_id == row.id).limit(1))
        if row.status == "published" or exists:
            raise AppException("招聘中的岗位或已有投递的岗位不能删除，请使用下架", code=5304, status_code=409)
        self.db.delete(row)
        self.db.commit()

    def public_detail(self, job_id):
        row = self.public_job(job_id)
        result = serialize(row)
        company = self.profile(row.recruiter_id)
        result["company"] = {key: value for key, value in company.items() if key != "account_id"}
        return result

    def apply(self, job_id, account: Account, resume_id, note):
        job = self.public_job(job_id)
        resume = self.db.get(Resume, resume_id)
        if resume is None:
            raise ResourceNotFoundError("简历版本不存在，请重新选择")
        if resume.user_id != account.profile_id or resume.profile_id != account.profile_id:
            raise AppException("只能投递本人的简历", code=5305, status_code=403)
        profile = self.db.get(User, account.profile_id)
        snapshot = self.resume_snapshot(resume, profile)
        row = RecruitmentApplication(job_id=job.id, student_id=account.id, job_title=job.title,
            company_name=job.company_name, resume_snapshot=snapshot, note=note)
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException("你已投递过这个岗位，请在站内投递中查看进度", code=5306, status_code=409) from exc
        return serialize(row)

    @staticmethod
    def resume_snapshot(resume, profile):
        def selected(items, ids):
            result = []
            for item in items:
                if item.id in (ids or []):
                    result.append({key: value for key, value in serialize(item).items() if key not in {"id", "user_id"}})
            return result
        experiences = resume.selected_experiences or {}
        projects = selected(profile.projects, resume.selected_projects)
        # Use only accepted expressions for selected projects; do not share
        # the full optimization response or unselected project descriptions.
        expressions = (resume.optimized_content or {}).get("optimized_projects", [])
        if isinstance(expressions, list):
            for project in projects:
                expression = next((item.get("optimized") for item in expressions if isinstance(item, dict)
                    and item.get("project_name") == project["name"] and isinstance(item.get("optimized"), str)), None)
                if expression:
                    project["description"] = expression
        return {"name": resume.name, "target_job": resume.target_job, "personal_summary": resume.personal_summary or profile.bio,
            "profile": {**{key: getattr(profile, key) for key in ("name", "school", "major", "grade", "email", "phone")},
                "skills": selected(profile.skills, resume.selected_skills),
                "projects": projects,
                "competitions": selected(profile.competitions, experiences.get("competitions", [])),
                "internships": selected(profile.internships, experiences.get("internships", []))}}

    def owned_application(self, application_id, *, student_id=None, recruiter_id=None):
        stmt = select(RecruitmentApplication).where(RecruitmentApplication.id == application_id)
        if student_id is not None:
            stmt = stmt.where(RecruitmentApplication.student_id == student_id)
        else:
            stmt = stmt.join(RecruitmentJob).where(RecruitmentJob.recruiter_id == recruiter_id)
        row = self.db.scalar(stmt)
        if row is None:
            raise ResourceNotFoundError("投递记录不存在或无权限访问")
        return row

    def update_application(self, row, status, feedback=None):
        if status not in TRANSITIONS[row.status] and not (status == row.status and TRANSITIONS[row.status]):
            raise AppException("此投递不能变更为该状态，请刷新后重试", code=5307, status_code=409)
        values = {"status": status, "updated_at": datetime.now(timezone.utc)}
        if feedback is not None:
            values["feedback"] = feedback
        result = self.db.execute(update(RecruitmentApplication).where(
            RecruitmentApplication.id == row.id, RecruitmentApplication.status == row.status).values(**values),
            execution_options={"synchronize_session": False})
        if result.rowcount != 1:
            self.db.rollback()
            raise AppException("投递状态已变化，请刷新后重试", code=5307, status_code=409)
        self.db.commit()
        self.db.refresh(row)
        return serialize(row)


def job_query(*, recruiter_id=None, keyword="", category="", city="", status=""):
    stmt = select(RecruitmentJob)
    if recruiter_id is not None:
        stmt = stmt.where(RecruitmentJob.recruiter_id == recruiter_id)
    else:
        stmt = stmt.join(Account, RecruitmentJob.recruiter_id == Account.id).where(Account.is_active.is_(True))
        status = "published"
    if status:
        stmt = stmt.where(RecruitmentJob.status == status)
    if keyword:
        stmt = stmt.where(or_(*[column.contains(keyword, autoescape=True) for column in
            (RecruitmentJob.title, RecruitmentJob.company_name, RecruitmentJob.description, RecruitmentJob.requirements, cast(RecruitmentJob.tags, String))]))
    if category:
        stmt = stmt.where(RecruitmentJob.category == category)
    if city:
        stmt = stmt.where(RecruitmentJob.city.contains(city, autoescape=True))
    return stmt.order_by(RecruitmentJob.updated_at.desc(), RecruitmentJob.id.desc())

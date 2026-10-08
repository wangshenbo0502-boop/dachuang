from datetime import datetime, timezone
from sqlalchemy import func, select
from app.models.account import Account
from app.models.recruitment import RecruiterProfile, RecruitmentJob, RecruitmentApplication


def envelope(data=None, code=0, message="success", request_id=""):
    from fastapi.encoders import jsonable_encoder
    def utc(value):
        return value.replace(tzinfo=timezone.utc).isoformat() if value.tzinfo is None else value.astimezone(timezone.utc).isoformat()
    return jsonable_encoder({"code": code, "message": message, "data": data, "request_id": request_id},
                            custom_encoder={datetime: utc})


def mask_email(value):
    local, sep, domain = (value or "").partition("@")
    return local[:2] + "***" + (sep + domain if sep else "")


def account_dto(row):
    return {"id": row.id, "role": row.role, "display_name": row.username,
            "email_masked": mask_email(row.email), "is_active": row.is_active,
            "management_version": row.management_version,
            "created_at": row.created_at, "last_login_at": row.last_login_at}


JOB_FIELDS = ("id", "recruiter_id", "title", "company_name", "category", "city", "salary",
              "employment_type", "education", "experience", "description", "requirements",
              "tags", "status", "moderation_status", "management_version", "published_at",
              "created_at", "updated_at")


def job_dto(row):
    return {key: getattr(row, key) for key in JOB_FIELDS}


def recruiter_dto(db, account):
    profile = db.get(RecruiterProfile, account.id)
    result = {"account_id": account.id, "display_name": account.username, "is_active": account.is_active,
              "job_count": db.scalar(select(func.count()).select_from(RecruitmentJob).where(RecruitmentJob.recruiter_id == account.id)),
              "company_name": "", "city": "", "industry": "", "description": "",
              "contact_name_masked": "", "contact_email_masked": ""}
    if profile:
        result.update({key: getattr(profile, key) for key in ("company_name", "city", "industry", "description")})
        result.update(contact_name_masked=profile.contact_name[:1]+"***", contact_email_masked=mask_email(profile.contact_email))
    return result


def application_dto(db, row):
    job = db.get(RecruitmentJob, row.job_id)
    account = db.get(Account, row.student_id)
    return {"id": row.id, "job_id": row.job_id, "job_title": row.job_title,
            "company_name": row.company_name, "student_id": row.student_id,
            "student_display_name_masked": (account.username[:1] if account else "")+"***",
            "recruiter_id": job.recruiter_id if job else None, "status": row.status,
            "created_at": row.created_at, "updated_at": row.updated_at}


def page_data(db, stmt, page, page_size, serialize):
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    rows = db.scalars(stmt.offset((page-1)*page_size).limit(page_size)).all()
    return {"items": [serialize(x) for x in rows], "total": total, "page": page, "page_size": page_size}

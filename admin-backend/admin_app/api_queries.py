from urllib.parse import urlencode
from fastapi import APIRouter, Depends, Query
from .dependencies import require_permission
from .services.business import query

router = APIRouter(tags=["queries"])


async def fetch(kind, admin, params=None, resource_id=None):
    suffix = f"/{resource_id}" if resource_id is not None else ""
    path = f"/internal/admin/v1/{kind}{suffix}"
    values = {k: str(v).lower() if isinstance(v, bool) else v for k, v in (params or {}).items() if v is not None and v != ""}
    if values:
        path += "?" + urlencode(values)
    return await query(path, actor=admin.id, scope=f"{kind}:read")


@router.get("/overview")
async def overview(admin=Depends(require_permission("overview:read"))):
    return await fetch("overview", admin)


@router.get("/accounts")
async def accounts(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                   keyword: str = Query("", max_length=100), role: str = "", is_active: bool | None = None,
                   admin=Depends(require_permission("accounts:read"))):
    return await fetch("accounts", admin, {"page": page, "page_size": page_size, "keyword": keyword, "role": role, "is_active": is_active})


@router.get("/accounts/{account_id}")
async def account(account_id: int, admin=Depends(require_permission("accounts:read"))):
    return await fetch("accounts", admin, resource_id=account_id)


@router.get("/recruiters")
async def recruiters(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                     keyword: str = Query("", max_length=100), city: str = "", is_active: bool | None = None,
                     admin=Depends(require_permission("recruiters:read"))):
    return await fetch("recruiters", admin, {"page": page, "page_size": page_size, "keyword": keyword, "city": city, "is_active": is_active})


@router.get("/recruiters/{account_id}")
async def recruiter(account_id: int, admin=Depends(require_permission("recruiters:read"))):
    return await fetch("recruiters", admin, resource_id=account_id)


@router.get("/jobs")
async def jobs(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
               keyword: str = Query("", max_length=100), city: str = "", recruiter_id: int | None = None,
               status: str = "", moderation_status: str = "", admin=Depends(require_permission("jobs:read"))):
    return await fetch("jobs", admin, {"page": page, "page_size": page_size, "keyword": keyword, "city": city,
                       "recruiter_id": recruiter_id, "status": status, "moderation_status": moderation_status})


@router.get("/jobs/{job_id}")
async def job(job_id: int, admin=Depends(require_permission("jobs:read"))):
    return await fetch("jobs", admin, resource_id=job_id)


@router.get("/applications")
async def applications(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                       job_id: int | None = None, student_id: int | None = None, recruiter_id: int | None = None,
                       status: str = "", admin=Depends(require_permission("applications:read"))):
    return await fetch("applications", admin, {"page": page, "page_size": page_size, "job_id": job_id,
                       "student_id": student_id, "recruiter_id": recruiter_id, "status": status})

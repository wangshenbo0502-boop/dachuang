"""Regression coverage for the connected IT job-seeking workflows."""
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from test_auth_api import auth_api, headers, register
from app.models.user import User, UserSkill
from app.schemas.auth import RegisterRequest
from app.schemas.job import JobBrief, JobListResponse, JobMatchRequest
from app.services.insight_service import parse_feed
from app.services.boss_automation_service import BossAutomationError, BossAutomationService
from app.services.resume_service import ResumeService


def test_registration_rejects_invalid_new_fields():
    base = dict(email="123456@qq.com", code="123456", password="password123", confirm_password="password123")
    with pytest.raises(ValidationError):
        RegisterRequest(**base, phone="123")
    with pytest.raises(ValidationError):
        RegisterRequest(**base, birth_date=date.today() + timedelta(days=1))


def test_prefill_rejects_unsafe_or_homepage_urls():
    for url in (
        "http://www.zhipin.com/job_detail/test.html",
        "https://www.zhipin.com:8443/job_detail/test.html",
        "https://user:secret@www.zhipin.com/job_detail/test.html",
        "https://www.zhipin.com.evil.example/job_detail/test.html",
        "https://zhipin.com/?from=search",
        "https://m.zhipin.com/",
        "https://www.zhipin.com:invalid/job_detail/test.html",
        "https://[invalid/",
    ):
        with pytest.raises(BossAutomationError):
            BossAutomationService._validate_url(url)
    BossAutomationService._validate_url("https://www.zhipin.com/job_detail/test.html")
    BossAutomationService._validate_url("https://www.zhipin.com:443/job_detail/test.html")


def test_task_lifecycle_dedup_and_ownership(auth_api):
    client, db, codes = auth_api
    a = register(client, codes, "111111111@qq.com")
    b = register(client, codes, "222222222@qq.com")
    ah, bh = headers(a), headers(b)
    body = {"title": "SQL index practice", "target_job": "Backend", "source_key": "gap:sql"}
    first = client.post("/api/growth/tasks", headers=ah, json=body).json()["data"]
    assert client.post("/api/growth/tasks", headers=ah, json=body).json()["data"]["id"] == first["id"]
    path = f"/api/growth/tasks/{first['id']}"
    assert client.patch(path, headers=ah, json={"status": "done"}).status_code == 422
    assert client.patch(path, headers=bh, json={"status": "doing"}).status_code == 404
    assert client.get("/api/growth/tasks/list", headers=bh).json()["data"] == []
    done = client.patch(path, headers=ah, json={"status": "done", "evidence": "EXPLAIN execution plan", "feedback": "Reviewed indexes"}).json()["data"]
    assert done["completed_at"] and done["feedback"] == "Reviewed indexes"
    assert client.patch(path, headers=ah, json={"evidence": " "}).status_code == 422
    assert client.get("/api/growth/tasks/list", headers=ah).json()["data"][0]["evidence"] == "EXPLAIN execution plan"
    reopened = client.patch(path, headers=ah, json={"status": "doing"}).json()["data"]
    assert reopened["completed_at"] is None


def test_resource_events_preserve_flags_and_isolate_accounts(auth_api):
    client, db, codes = auth_api
    a = register(client, codes, "333333333@qq.com")
    b = register(client, codes, "444444444@qq.com")
    body = {"resource_key": "rss:one", "resource": {"title": "SQL", "content": "Index practice", "category": "skills"}}
    assert client.put("/api/resources/events", headers=headers(a), json={**body, "favorite": True}).status_code == 200
    saved = client.put("/api/resources/events", headers=headers(a), json={**body, "read": True}).json()["data"]
    assert saved["favorite"] and saved["read"]
    assert len(client.get("/api/resources/events", headers=headers(a)).json()["data"]) == 1
    assert client.get("/api/resources/events", headers=headers(b)).json()["data"] == []
    assert client.get("/api/resources/events").status_code == 401


def feed_item(url, published):
    return f"<item><title>Release</title><link>{url}</link><pubDate>{published}</pubDate><description>&lt;b&gt;Update&lt;/b&gt;</description></item>"


def test_news_dates_and_source_boundaries():
    now = datetime.now(timezone.utc)
    fresh = format_datetime(now - timedelta(hours=2))
    items = [
        feed_item("https://github.blog/news", fresh),
        feed_item("https://github.blog.evil.example/news", fresh),
        feed_item("https://github.blog/old", format_datetime(now - timedelta(days=31))),
        feed_item("https://github.blog/future", format_datetime(now + timedelta(days=1))),
        feed_item("https://github.blog/undated", ""),
    ]
    parsed = parse_feed(("<rss><channel>" + "".join(items) + "</channel></rss>").encode(), "GitHub", "github.blog")
    assert len(parsed) == 1
    assert parsed[0]["content"] == "Update"
    assert parsed[0]["metadata"]["source_url"] == "https://github.blog/news"
    with pytest.raises(ValueError):
        parse_feed(b"<!DOCTYPE rss><rss/>", "GitHub", "github.blog")


def test_market_context_has_source_and_user_evidence(auth_api, monkeypatch):
    from app.services.job_match_service import JobMatchService
    client, db, codes = auth_api
    account = register(client, codes, "555555555@qq.com")
    user = db.get(User, account["user"]["profile_id"])
    user.skills.append(UserSkill(name="Python", proficiency="熟练", description=""))
    db.commit()
    jobs = JobListResponse(total=1, items=[JobBrief(job_id="backend", title="Backend", required_skills=["Python", "python", "SQL"])])
    monkeypatch.setattr(JobMatchService, "instance", classmethod(lambda cls: SimpleNamespace(search_jobs=lambda **kwargs: jobs)))
    result = client.get("/api/career-profile/market-context?target_job=Backend", headers=headers(account)).json()["data"]
    assert result["sample_count"] == 1
    rows = {row["skill"]: row for row in result["skills"]}
    assert rows["Python"]["evidence"]
    assert rows["Python"]["coverage"] == 100
    assert rows["SQL"]["evidence"] == []
    assert rows["SQL"]["sources"][0]["job_id"] == "backend"


def test_match_uses_requirements_without_substring_false_positives(monkeypatch):
    from app.services.job_match_service import JobMatchService
    service = JobMatchService.__new__(JobMatchService)
    document = dict(doc_id="java", content="Java role", metadata=dict(
        title="Backend", tags=["JavaScript"], required_skills=["Java", "SQL", "sql"],
        preferred_skills=["Linux"], hard_requirements={"学历": "本科"}))
    service._loaded = True
    service._all_jobs = {"java": document}
    service._knowledge = SimpleNamespace(search=lambda *args, **kwargs: [document], get_skill_requirements=lambda _: ["JavaScript"])
    service._ai_client = SimpleNamespace(is_mock_mode=True)
    result = service.match_jobs(JobMatchRequest(skills=["JavaScript", "SQL"])).matches[0]
    assert result.match_score == 50
    assert result.missing_skills == ["Java"]
    assert result.preferred_skills == ["Linux"]
    assert result.hard_requirements == {"学历": "本科"}


def test_resume_reordered_projects_cannot_replace_original_facts():
    service = ResumeService.__new__(ResumeService)
    facts = {"name": "Student", "skills": [], "projects": [
        {"id": 11, "name": "API", "description": "Built Python API", "tech_stack": ["Python"]},
        {"id": 12, "name": "SQL", "description": "Wrote SQL queries", "tech_stack": ["SQL"]},
    ]}
    response = service._parse_ai_result({"optimized_projects": [
        {"project_name": "SQL", "original": "Made up", "optimized": "Improved queries by 90%"},
        {"project_name": "API", "original": "Made up", "optimized": "Developed a Python API"},
    ], "personal_summary": "Led 50 engineers"}, facts)
    assert response.optimized_projects[0].source_experience_id == 11
    assert response.optimized_projects[0].original == "Built Python API"
    assert response.optimized_projects[0].optimized == "Developed a Python API"
    assert response.optimized_projects[1].optimized == "Wrote SQL queries"
    assert response.optimized_projects[1].fact_warnings
    assert response.optimized_projects[0].review_status == "pending_review"
    assert response.personal_summary == ""


def test_application_ownership_dedup_and_no_resubmit(auth_api):
    client, db, codes = auth_api
    a = register(client, codes, "666666666@qq.com")
    b = register(client, codes, "777777777@qq.com")
    version = client.post("/api/resume/versions", headers=headers(a), json={"user_id": a["user"]["profile_id"], "name": "Backend", "target_job": "Python"}).json()["data"]
    body = {"job_id": "python", "job_title": "Python", "boss_url": "https://www.zhipin.com/job_detail/test.html", "resume_version_id": version["id"], "greeting": "Hello"}
    assert client.post("/api/applications", headers=headers(b), json=body).status_code == 404
    assert client.post("/api/applications", headers=headers(a), json={**body, "boss_url": "https://evil.example/job"}).status_code == 422
    first = client.post("/api/applications", headers=headers(a), json=body).json()["data"]
    assert client.post("/api/applications", headers=headers(a), json=body).json()["data"]["id"] == first["id"]
    path = f"/api/applications/{first['id']}"
    assert client.patch(path, headers=headers(a), json={"status": "applied", "note": "Sent externally"}).status_code == 200
    assert client.post(path + "/automation/start", headers=headers(a)).status_code == 409
    assert client.patch(path, headers=headers(b), json={"status": "closed"}).status_code == 404

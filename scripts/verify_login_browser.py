"""Verify login roles in Edge against isolated SQLite and private processes.

Run from repository root: python scripts/verify_login_browser.py
Email challenges are fixtures; no live mail or existing business data is used.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
from urllib.parse import parse_qs, urlsplit

from verify_recruitment_browser import ROOT, capture, field, free_port, ready, token

OUTPUT = ROOT / "docs" / "verification" / "login"
EMAILS = {"student": "992000001@qq.com", "recruiter": "992000002@qq.com"}
PASSWORD = "login-verification-password"


def main():
    from playwright.sync_api import expect, sync_playwright

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "browser-results.json").unlink(missing_ok=True)
    backend_port, frontend_port = free_port(), free_port()
    backend_url = f"http://127.0.0.1:{backend_port}"
    frontend_url = f"http://127.0.0.1:{frontend_port}"
    checks, errors, processes = [], [], []
    with tempfile.TemporaryDirectory(prefix="dachuang-login-") as temporary:
        env = os.environ.copy()
        env.update({
            "DATABASE_URL": f"sqlite:///{Path(temporary).as_posix()}/verification.db",
            "APP_ENV": "testing", "JWT_SECRET": secrets.token_hex(32),
            "DEEPSEEK_API_KEY": "", "KNOWLEDGE_DATABASE_URL": "",
            "RATE_LIMIT_ENABLED": "false", "LOG_LEVEL": "WARNING",
        })
        os.environ.update(env)
        sys.path.insert(0, str(ROOT / "backend"))
        from app.auth.security import hash_code
        from app.database.bootstrap import initialize_database_schema
        from app.database.connection import get_engine
        from app.database.session import get_session_factory
        from app.models.account import EmailCode

        initialize_database_schema()
        with get_session_factory()() as db:
            now = datetime.now(timezone.utc)
            for email in EMAILS.values():
                for purpose in ("REGISTER", "RESET_PASSWORD"):
                    db.add(EmailCode(
                        email=email, purpose=purpose, code_hash=hash_code(email, purpose, "123456"),
                        expires_at=now + timedelta(hours=1), sent_at=now,
                        day=now.date().isoformat(), daily_count=1, failed_attempts=0,
                    ))
            db.commit()

        frontend_root = ROOT / "frontend"
        vite_config = Path(temporary) / "verification-vite.mjs"
        vite_module = (frontend_root / "node_modules/vite/dist/node/index.js").as_uri()
        vue_module = (frontend_root / "node_modules/@vitejs/plugin-vue/dist/index.mjs").as_uri()
        vite_config.write_text(
            f"import {{defineConfig}} from {json.dumps(vite_module)};\n"
            f"import vue from {json.dumps(vue_module)};\n"
            f"export default defineConfig({{root:{json.dumps(frontend_root.as_posix())},plugins:[vue()],"
            f"resolve:{{alias:{{'@':{json.dumps((frontend_root / 'src').as_posix())}}}}},"
            f"server:{{host:'127.0.0.1',port:{frontend_port},strictPort:true,"
            f"proxy:{{'/api':{json.dumps(backend_url)}}}}}}});",
            encoding="utf-8",
        )
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        with (OUTPUT / "backend.log").open("w", encoding="utf-8") as backend_log, \
                (OUTPUT / "frontend.log").open("w", encoding="utf-8") as frontend_log:
            try:
                backend = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(backend_port)],
                    cwd=ROOT / "backend", env=env, stdout=backend_log, stderr=subprocess.STDOUT, creationflags=flags,
                )
                processes.append(backend)
                frontend = subprocess.Popen(
                    ["node", str(frontend_root / "node_modules/vite/bin/vite.js"), "--config", str(vite_config)],
                    cwd=frontend_root, env=env, stdout=frontend_log, stderr=subprocess.STDOUT, creationflags=flags,
                )
                processes.append(frontend)
                ready(backend_url + "/api/health", backend)
                ready(frontend_url, frontend)
                with sync_playwright() as p:
                    browser = p.chromium.launch(channel="msedge", headless=True)
                    context = browser.new_context(viewport={"width": 1440, "height": 1000}, base_url=frontend_url)
                    page = context.new_page()
                    page.set_default_timeout(12000)
                    page.on("pageerror", lambda exc: errors.append(str(exc)))
                    for role, email in EMAILS.items():
                        response = page.request.post(frontend_url + "/api/auth/register", data={
                            "email": email, "code": "123456", "password": PASSWORD,
                            "confirm_password": PASSWORD, "name": f"登录验证-{role}", "role": role,
                        })
                        assert response.status == 201, response.text()

                    page.goto("/login")
                    expect(page.get_by_role("button", name="求职者登录", exact=True)).to_have_attribute("aria-pressed", "true")
                    expect(page.get_by_role("button", name="招聘者登录", exact=True)).to_be_visible()
                    expect(page.get_by_role("heading", name="求职者登录", exact=True)).to_be_visible()
                    capture(page, OUTPUT / "desktop-student.png")
                    field(page, "QQ 邮箱", EMAILS["recruiter"])
                    field(page, "密码", PASSWORD)
                    page.get_by_role("button", name="招聘者登录", exact=True).click()
                    expect(page.get_by_role("heading", name="招聘者登录", exact=True)).to_be_visible()
                    expect(page.get_by_label("QQ 邮箱", exact=True)).to_have_value(EMAILS["recruiter"])
                    expect(page.get_by_label("密码", exact=True)).to_have_value(PASSWORD)
                    assert parse_qs(urlsplit(page.url).query)["role"] == ["recruiter"]
                    page.reload()
                    expect(page.get_by_role("button", name="招聘者登录", exact=True)).to_have_attribute("aria-pressed", "true")
                    capture(page, OUTPUT / "desktop-recruiter.png")
                    checks.append("both visible role entries, context copy, retained inputs and refresh selection")

                    page.get_by_role("link", name="注册招聘者账号", exact=True).click()
                    expect(page.get_by_role("heading", name="创建招聘者账号", exact=True)).to_be_visible()
                    expect(page.get_by_role("radio", name="招聘者", exact=True)).to_be_checked()
                    page.get_by_text("求职者", exact=True).click()
                    page.get_by_role("link", name="返回登录", exact=True).click()
                    expect(page.get_by_role("heading", name="求职者登录", exact=True)).to_be_visible()
                    page.get_by_role("link", name="注册求职者账号", exact=True).click()
                    expect(page.get_by_role("radio", name="求职者", exact=True)).to_be_checked()
                    page.get_by_role("link", name="返回登录", exact=True).click()
                    checks.append("registration preselects both roles and returns with the current registration role")

                    page.goto("/login?role=recruiter&redirect=/recruiter/jobs/new")
                    page.get_by_role("link", name="忘记密码？", exact=True).click()
                    assert parse_qs(urlsplit(page.url).query)["role"] == ["recruiter"]
                    page.get_by_role("link", name="返回登录", exact=True).click()
                    expect(page.get_by_role("heading", name="招聘者登录", exact=True)).to_be_visible()
                    page.get_by_role("link", name="忘记密码？", exact=True).click()
                    field(page, "QQ 邮箱", EMAILS["recruiter"])
                    field(page, "验证码", "123456")
                    recruiter_password = "reset-login-verification-password"
                    field(page, "新密码", recruiter_password)
                    field(page, "确认新密码", recruiter_password)
                    page.get_by_role("button", name="重置密码", exact=True).click()
                    expect(page.get_by_role("heading", name="招聘者登录", exact=True)).to_be_visible()
                    query = parse_qs(urlsplit(page.url).query)
                    assert query["role"] == ["recruiter"] and query["redirect"] == ["/recruiter/jobs/new"]
                    checks.append("password reset and return preserve recruiter selection and original destination")

                    # A recruiter account in the seeker entry must not create a session.
                    page.get_by_role("button", name="求职者登录", exact=True).click()
                    field(page, "QQ 邮箱", EMAILS["recruiter"])
                    field(page, "密码", recruiter_password)
                    page.get_by_role("button", name="登录求职工作台", exact=True).click()
                    expect(page.locator(".el-alert")).to_contain_text("请选择“招聘者登录”")
                    assert token(page) is None
                    capture(page, OUTPUT / "role-mismatch.png")
                    page.get_by_role("button", name="招聘者登录", exact=True).click()
                    expect(page.locator(".el-alert")).to_have_count(0)
                    login_requests = []
                    page.on("request", lambda request: login_requests.append(request.post_data_json)
                            if request.method == "POST" and request.url.endswith("/api/auth/login") else None)
                    page.get_by_label("密码", exact=True).press("Enter")
                    expect(page).to_have_url(frontend_url + "/recruiter/jobs/new")
                    page.wait_for_load_state("networkidle")
                    assert len(login_requests) == 1 and login_requests[0]["role"] == "recruiter"
                    checks.append("wrong recruiter entry creates no session; role switch clears error; Enter submits once and preserves destination")

                    student_context = browser.new_context(viewport={"width": 1440, "height": 1000}, base_url=frontend_url)
                    student = student_context.new_page()
                    student.set_default_timeout(12000)
                    student.on("pageerror", lambda exc: errors.append(str(exc)))
                    student.goto("/login?role=recruiter&redirect=/recruiter")
                    field(student, "QQ 邮箱", EMAILS["student"])
                    field(student, "密码", PASSWORD)
                    student.get_by_role("button", name="登录招聘工作台", exact=True).click()
                    expect(student.locator(".el-alert")).to_contain_text("请选择“求职者登录”")
                    assert token(student) is None
                    student.get_by_role("button", name="求职者登录", exact=True).click()
                    student.get_by_role("button", name="登录求职工作台", exact=True).click()
                    expect(student).to_have_url(frontend_url + "/dashboard")
                    assert token(student)
                    student_context.close()
                    checks.append("wrong seeker entry creates no session; seeker login rejects cross-role redirect and enters dashboard")

                    mobile_context = browser.new_context(viewport={"width": 390, "height": 844}, base_url=frontend_url)
                    mobile = mobile_context.new_page()
                    mobile.set_default_timeout(12000)
                    mobile.on("pageerror", lambda exc: errors.append(str(exc)))
                    mobile.goto("/recruiter/jobs/new?source=login-verification")
                    expect(mobile.get_by_role("heading", name="招聘者登录", exact=True)).to_be_visible()
                    query = parse_qs(urlsplit(mobile.url).query)
                    assert query["role"] == ["recruiter"]
                    assert query["redirect"] == ["/recruiter/jobs/new?source=login-verification"]
                    checks.append("protected recruiter URL opens the matching login entry and preserves the full destination")
                    for role, label in (("recruiter", "招聘者"), ("student", "求职者")):
                        mobile.goto(f"/login?role={role}")
                        expect(mobile.get_by_role("heading", name=f"{label}登录", exact=True)).to_be_visible()
                        for entry in ("求职者登录", "招聘者登录"):
                            expect(mobile.get_by_role("button", name=entry, exact=True)).to_be_in_viewport()
                        assert mobile.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                        capture(mobile, OUTPUT / f"mobile-{role}.png")
                    mobile_context.close()
                    context.close()
                    browser.close()
                    checks.append("both mobile entries appear in the first viewport without horizontal overflow")
                    assert not errors, errors
                result = {"status": "passed", "checks": checks, "browser_errors": errors,
                          "screenshots": sorted(path.name for path in OUTPUT.glob("*.png"))}
                (OUTPUT / "browser-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            except Exception as exc:
                (OUTPUT / "browser-results.json").write_text(json.dumps({
                    "status": "failed", "checks": checks, "browser_errors": errors, "error": str(exc),
                }, ensure_ascii=False, indent=2), encoding="utf-8")
                raise
            finally:
                for process in reversed(processes):
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=10)
                get_engine().dispose()


if __name__ == "__main__":
    main()

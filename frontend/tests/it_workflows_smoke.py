"""Browser smoke tests with explicit API fixtures; never writes business data.

Run with Python + Playwright against the local Vite server. Screenshots are
written to the supplied output directory, not to the application assets.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5173"
NOW = datetime.now(timezone.utc).isoformat()
PROFILE = dict(
    id=1, name="测试开发者", school="测试大学", major="软件工程", grade="大四",
    email="123456789@qq.com", phone="13800138000", birth_date="2003-06-15",
    target_city="上海", target_salary="10k-15k", bio="专注后端开发与工程实践。",
    skills=[dict(id=1, name="Python", proficiency="熟练", description="接口开发"),
            dict(id=2, name="SQL", proficiency="掌握", description="查询与索引")],
    projects=[dict(id=1, name="就业信息检索系统", role="后端开发", description="使用 Python 开发岗位查询接口。",
                   tech_stack=["Python", "SQL"], start_date="2025-09-01", end_date=None)],
    internships=[], competitions=[], created_at=NOW, updated_at=NOW,
)
JOBS = [dict(
    job_id=f"backend-{i}", title=title, category="后端", tags=["Python", "SQL", "Docker"],
    required_skills=["Python", "SQL", "Docker"], preferred_skills=["Linux"],
    hard_requirements={"学历": "本科"}, published_at=None, source="测试岗位库",
    snippet="负责业务接口、数据查询与服务部署，关注代码质量和团队协作。",
    content="技术要求：Python、SQL、Docker。加分项：Linux。",
) for i, title in enumerate(["Python 后端开发工程师", "数据平台开发工程师", "后端开发实习生"], 1)]
NEWS = [dict(
    doc_id=f"test-news-{i}", title=title, content="浏览器验收夹具，仅用于验证页面呈现，不代表真实新闻。",
    category="market", source="测试官方来源",
    metadata=dict(published_at=NOW, source_url=f"https://github.blog/test-{i}", recommendation="开发工具与工程实践"),
) for i, title in enumerate(["开发工具更新与工程实践", "Python 生态技术动态", "数据库性能优化专题"], 1)]
ANALYSIS = dict(id=1, user_id=1, target_job=JOBS[0]["title"], is_mock=True, created_at=NOW, result=dict(
    comprehensive_score=72, current_level="具备基础实践", technical_direction="Python 后端",
    profile_summary="已有接口开发记录，仍需补充部署与测试证据。",
    skill_assessment=dict(programming_foundation=75, framework_usage=65, database_skill=70, engineering_practice=55, project_experience=68),
    recommended_directions=[dict(job_title=JOBS[0]["title"], match_rate=78)],
    core_advantages=["具备后端项目记录"], areas_to_improve=["补充部署实践"],
))
GROWTH = dict(id=1, user_id=1, target_job=JOBS[0]["title"], is_mock=True, created_at=NOW, result=dict(
    current_situation="已有基础项目", expected_timeline="4 周",
    learning_roadmap=[dict(stage="工程实践", focus="容器部署与测试", tasks=["完成 Docker 部署实践"], milestone="提交部署记录")],
    ability_gaps=[dict(skill="Docker", importance="高", description="缺少部署证据")],
    recommended_resources=["Docker 入门"], interview_prep_tips=["解释数据库索引原理"],
    recommended_projects=[dict(name="接口部署实践", description="为接口添加测试与部署配置", tech_stack=["Python", "Docker"])],
))


def main():
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=True)
    tasks, events = [], []
    version = dict(id=1, user_id=1, profile_id=1, name="后端校招简历", target_job=JOBS[0]["title"],
                   selected_projects=[1], selected_skills=[1, 2], selected_experiences=dict(internships=[], competitions=[]),
                   optimized_content={}, personal_summary="", template="default", status="draft",
                   profile=PROFILE, created_at=NOW, updated_at=NOW)
    applications = [dict(id=1, user_id=1, job_id="backend-1", job_title=JOBS[0]["title"],
                         platform="boss", boss_url="https://www.zhipin.com/job_detail/test.html",
                         status="applied", greeting="您好", resume_version_id=1, note="待反馈",
                         applied_at=NOW, created_at=NOW, updated_at=NOW, automation_status="idle", automation_error="")]
    errors = []
    missing = []

    def route_api(route):
        if not urlparse(route.request.url).path.startswith("/api/"):
            route.continue_()
            return
        path = urlparse(route.request.url).path.removeprefix("/api")
        method = route.request.method
        body = route.request.post_data_json if method in ("POST", "PUT", "PATCH") else {}
        data = None
        if path == "/auth/me":
            data = dict(id=1, profile_id=1, email=PROFILE["email"], email_verified=True)
        elif path == "/users/1":
            data = PROFILE
        elif path == "/resources/home":
            data = dict(items=NEWS, unavailable_sources=[], fetched_at=NOW, period_days=30)
        elif path == "/resources/events":
            if method == "PUT":
                old = next((x for x in events if x["resource_key"] == body["resource_key"]), None)
                if old is None:
                    old = dict(id=len(events)+1, user_id=1, favorite=False, read=False, hidden=False)
                    events.append(old)
                old.update(body)
                data = old
            else:
                data = events
        elif path == "/knowledge/search":
            data = dict(query=body["query"], results=NEWS)
        elif path == "/growth/tasks/list":
            data = tasks
        elif path == "/growth/tasks":
            data = dict(id=len(tasks)+1, user_id=1, status="todo", evidence="", feedback="", created_at=NOW, updated_at=NOW, completed_at=None, **body)
            tasks.append(data)
        elif path.startswith("/growth/tasks/"):
            data = next(t for t in tasks if t["id"] == int(path.split("/")[-1]))
            data.update(body)
            data["completed_at"] = NOW if data["status"] == "done" else None
        elif path == "/jobs":
            data = dict(items=JOBS, total=len(JOBS))
        elif path.startswith("/jobs/"):
            data = next(j for j in JOBS if j["job_id"] == path.split("/")[-1])
        elif path == "/match":
            data = dict(user_skills=["Python", "SQL"], total_matches=3, matches=[dict(**j, match_score=70, matched_skills=["Python", "SQL"], missing_skills=["Docker"], match_reason="按技能记录对照") for j in JOBS])
        elif path == "/analysis/user/1":
            data = [dict(id=1)]
        elif path == "/analysis/1" or path == "/analysis":
            data = ANALYSIS
        elif path == "/growth/user/1":
            data = [dict(id=1)]
        elif path == "/growth/1" or path == "/growth":
            data = GROWTH
        elif path == "/career-profile/market-context":
            data = dict(target_job=JOBS[0]["title"], sample_count=3, scope="浏览器测试样本，非实际招聘统计。",
                        observed_at=NOW, jobs=JOBS, skills=[dict(skill="Docker", count=3, coverage=100, sources=[dict(job_id="backend-1", title=JOBS[0]["title"])],
                                                              evidence=[], status="缺少证据", action="完成 Docker 实践")])
        elif path == "/resume/versions/user/1":
            data = [version]
        elif path.startswith("/resume/versions/"):
            if method == "PUT":
                version.update(body)
            data = version
        elif path == "/resume/versions":
            version.update(body)
            data = version
        elif path == "/resume":
            data = dict(id=1, result=dict(personal_summary="具有 Python 接口开发经历。", resume_score=72,
                                         overall_suggestions=["补充测试记录"], optimized_projects=[dict(
                                             project_name=PROFILE["projects"][0]["name"], source_experience_id=1,
                                             original=PROFILE["projects"][0]["description"], optimized="使用 Python 实现岗位查询接口。",
                                             fact_warnings=["结果数据待补充"], review_status="pending_review")]))
        elif path == "/applications":
            data = applications
        elif path.startswith("/applications/"):
            applications[0].update(body)
            data = applications[0]
        elif path == "/health":
            data = dict(status="healthy", ai_mode="mock", modules=[])
        else:
            missing.append(path)
            data = []
        route.fulfill(status=200, content_type="application/json", body=json.dumps(dict(code=0, message="test fixture", data=data), ensure_ascii=False))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=dict(width=1440, height=1000), device_scale_factor=1)
        context.route("**/api/**", route_api)
        context.add_init_script("localStorage.setItem('employment-platform-access-token','test-fixture-token')")
        page = context.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda message: print("Browser:", message.text) if message.type == "error" else None)
        report = []
        for width, height in [(1440, 1000), (390, 844)]:
            page.set_viewport_size(dict(width=width, height=height))
            for path in ["dashboard", "profile", "analysis", "jobs", "resume", "growth", "resources", "applications"]:
                page.goto(f"{BASE}/{path}")
                try:
                    page.wait_for_selector(".career-heading" if path == "dashboard" else ".page-header", timeout=30000)
                except Exception:
                    page.screenshot(path=str(output / "failure.png"), full_page=True)
                    print("Failed page:", page.url, "errors:", errors, "unhandled:", missing)
                    print(page.locator("body").inner_text()[:3000])
                    raise
                if path in ("profile", "analysis"):
                    page.wait_for_selector("canvas", timeout=15000)
                page.wait_for_timeout(700)
                assert page.url.endswith(path), page.url
                page.screenshot(path=str(output / f"{path}-{width}.png"), full_page=True)
                assert not errors, errors
                overflow = page.evaluate("document.documentElement.scrollWidth > innerWidth + 2")
                assert not overflow, f"Horizontal overflow: {path} {width}"
                canvases = page.locator("canvas").evaluate_all("""els => els.map(c => {
                    const pixels = c.getContext('2d').getImageData(0,0,c.width,c.height).data;
                    let n = 0; for(let i=3;i<pixels.length;i+=4) if(pixels[i]>0) n++;
                    return n;
                })""")
                if path in ("profile", "analysis"):
                    assert canvases and all(n > 100 for n in canvases), (path, canvases)
                report.append(dict(page=path, width=width, canvas_pixels=canvases))
        page.set_viewport_size(dict(width=1440, height=1000))
        page.goto(BASE + "/jobs")
        page.get_by_role("button", name="智能匹配", exact=True).click()
        page.wait_for_selector(".result-notice")
        assert page.locator(".job-card").count() == 3
        assert "Docker" in page.locator(".job-card").first.inner_text()
        page.get_by_text("仅看匹配度 75% 以上", exact=True).click()
        page.get_by_text("没有找到相关 IT 岗位", exact=True).wait_for()
        assert page.locator(".job-card").count() == 0
        page.get_by_text("仅看匹配度 75% 以上", exact=True).click()
        page.screenshot(path=str(output / "jobs-matched-1440.png"), full_page=True)
        page.goto(BASE + "/resources")
        page.get_by_role("button", name="收藏", exact=True).first.click()
        page.get_by_role("button", name="加入成长任务", exact=True).first.click()
        page.reload()
        page.get_by_text("我的收藏", exact=True).click()
        page.wait_for_selector(".resource-list article")
        assert page.locator(".resource-list article").count() == 1
        page.goto(BASE + "/growth")
        page.get_by_role("button", name="开始", exact=True).click()
        page.get_by_role("button", name="提交完成", exact=True).click()
        page.locator(".el-dialog textarea").first.fill("完成实践，记录测试过程与结果")
        page.get_by_role("button", name="保存记录", exact=True).click()
        page.wait_for_timeout(350)
        page.reload()
        page.wait_for_selector(".task-row")
        assert "完成实践" in page.locator(".task-row").inner_text()
        assert tasks[0]["status"] == "done"
        page.goto(BASE + "/resume")
        page.get_by_role("button", name="AI 优化", exact=True).click()
        page.wait_for_selector(".resume-review")
        assert page.get_by_role("button", name="写入已确认内容").is_disabled()
        page.locator(".review-row .el-checkbox").click()
        page.get_by_role("button", name="写入已确认内容").click()
        page.wait_for_timeout(350)
        assert version["optimized_content"]["optimized_projects"][0]["review_status"] == "confirmed"
        page.get_by_role("button", name="准备投递", exact=True).click()
        page.wait_for_selector(".application-workbench")
        page.wait_for_timeout(500)
        page.screenshot(path=str(output / "resume-workbench-1440.png"), full_page=True)
        page.set_viewport_size(dict(width=390, height=844))
        page.wait_for_timeout(600)
        page.screenshot(path=str(output / "resume-workbench-390.png"), full_page=True)
        assert page.locator(".sidebar").bounding_box()["x"] + page.locator(".sidebar").bounding_box()["width"] <= 1
        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2")
        context.close()
        context = browser.new_context(viewport=dict(width=390, height=844))
        page = context.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(BASE + "/register")
        page.wait_for_timeout(700)
        assert page.get_by_text("手机号", exact=True).count() > 0
        assert page.get_by_text("出生日期", exact=True).count() > 0
        page.screenshot(path=str(output / "register-390.png"), full_page=True)
        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2")
        page.set_viewport_size(dict(width=1440, height=1000))
        page.wait_for_timeout(300)
        page.screenshot(path=str(output / "register-1440.png"), full_page=True)
        page.evaluate("localStorage.setItem('employment-platform-access-token', 'expired-browser-test-token')")
        page.goto(BASE + "/resources")
        page.wait_for_url("**/login?redirect=**", timeout=15000)
        assert page.evaluate("localStorage.getItem('employment-platform-access-token')") is None
        page.wait_for_selector(".login-form")
        assert not errors, errors
        assert not missing, missing
        print(json.dumps(dict(views=report, interactions="passed", errors=errors), ensure_ascii=False))
        browser.close()


if __name__ == "__main__":
    main()

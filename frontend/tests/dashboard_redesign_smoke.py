"""Dashboard proportions, real interactions, and resilient states using isolated fixtures."""
import copy
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import expect, sync_playwright
from it_workflows_smoke import BASE, PROFILE, ANALYSIS, GROWTH, NEWS, NOW


CATEGORIES = {
    "后端": ["Python", "SQL", "Docker", "Redis", "Git"],
    "前端": ["TypeScript", "Vue", "CSS", "Git"],
    "AI": ["Python", "PyTorch", "SQL"],
    "数据": ["SQL", "Python", "Spark"],
    "测试": ["Python", "Selenium", "Git"],
    "运维": ["Linux", "Docker", "Kubernetes"],
    "安全": ["Linux", "Python", "网络安全"],
    "产品": [],
}
JOBS = [
    dict(job_id=f"fixture-{i}", title=f"{category}工程师 / 验收样本 {i}",
         category=category, tags=skills, required_skills=skills + skills[:1],
         preferred_skills=[], hard_requirements={}, snippet="仅供浏览器测试的岗位样本。",
         source="浏览器验收岗位库")
    for i in range(54)
    for category, skills in [list(CATEGORIES.items())[i % len(CATEGORIES)]]
]
SKEWED_COUNTS = {"AI": 20, "后端": 9, "其他": 7, "数据": 5, "运营": 4, "产品": 2,
                 "前端": 2, "测试": 2, "移动端": 1, "安全": 1, "运维": 1}
SKEWED_JOBS = [
    dict(job_id=f"skewed-{category}-{i}", title=f"{category}工程师 / 验收样本 {i}",
         category=category, required_skills=CATEGORIES.get(category, ["SQL", "Git"]),
         tags=[], snippet="隔离的非均匀分布测试样本。", source="")
    for category, count in SKEWED_COUNTS.items() for i in range(count)
]


def main():
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=True)
    state = {"mode": "populated"}
    calls, errors, missing = [], [], []

    def route_api(route):
        parsed = urlparse(route.request.url)
        if not parsed.path.startswith("/api/"):
            route.continue_()
            return
        path = parsed.path.removeprefix("/api")
        query = parse_qs(parsed.query)
        calls.append((path, query))
        mode = state["mode"]
        if mode == "error" and path in ("/jobs", "/resources/home", "/analysis/user/1"):
            route.fulfill(status=503, content_type="application/json",
                          body=json.dumps(dict(code=3101, message="验收：服务暂不可用", data=None)))
            return
        if path == "/auth/me":
            data = dict(id=1, profile_id=1, email=PROFILE["email"], email_verified=True)
        elif path == "/users/1":
            data = copy.deepcopy(PROFILE)
            if mode == "new":
                data.update(skills=[], projects=[], competitions=[], internships=[],
                            target_city="", bio="", school="", major="", grade="", target_salary="")
            if mode == "long":
                data["name"] = "一个名字较长的测试求职者" * 3
        elif path == "/jobs":
            items = [] if mode == "empty" else SKEWED_JOBS if mode == "skewed" else JOBS
            if "category" in query:
                items = [job for job in items if job["category"] == query["category"][0]]
            if "keyword" in query:
                keyword = query["keyword"][0].lower()
                items = [job for job in items if keyword in (job["title"] + " ".join(job["required_skills"])).lower()]
            start = (int(query.get("page", ["1"])[0]) - 1) * int(query.get("page_size", ["50"])[0])
            size = int(query.get("page_size", ["50"])[0])
            data = dict(total=len(items), items=items[start:start + size])
        elif path.startswith("/jobs/"):
            data = dict(**next(job for job in JOBS if job["job_id"] == path.split("/")[-1]),
                        content="岗位详情浏览器测试样本。", metadata={})
        elif path == "/resources/home":
            data = dict(items=NEWS if mode != "empty" else [], unavailable_sources=[], fetched_at=NOW, period_days=30)
        elif path in ("/analysis/user/1", "/growth/user/1"):
            data = [] if mode in ("new", "empty") else [dict(id=1)]
        elif path == "/analysis/1":
            data = copy.deepcopy(ANALYSIS)
            if mode == "long":
                data["result"]["technical_direction"] = "ArtificialIntelligenceInfrastructureEngineering" * 3
                data["result"]["profile_summary"] = "这是一段较长的就业分析建议，用于测试内容能否自然换行。" * 8
        elif path == "/growth/1":
            data = GROWTH
        else:
            missing.append(path)
            data = []
        route.fulfill(status=200, content_type="application/json",
                      body=json.dumps(dict(code=0, message="isolated test fixture", data=data), ensure_ascii=False))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport=dict(width=1440, height=1000))
        context.add_init_script("localStorage.setItem('employment-platform-access-token','dashboard-test-fixture')")
        context.route("**/api/**", route_api)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))

        def dashboard(mode="populated"):
            state["mode"] = mode
            page.goto(BASE + "/dashboard")
            page.wait_for_selector(".it-home[aria-busy='false']")
            page.wait_for_timeout(400)

        report = []
        for width, height in [(1920, 1080), (1440, 1000), (1024, 900), (768, 1024), (390, 844), (320, 740)]:
            page.set_viewport_size(dict(width=width, height=height))
            dashboard()
            assert not page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"), width
            assert page.locator(".circuit-image").evaluate("(img) => img.complete && img.naturalWidth > 1000")
            expect(page.locator(".industry-summary > div").first).to_contain_text("54")
            expect(page.locator(".industry-summary > div").nth(1)).to_contain_text("8")
            assert page.locator(".news-item").count() == 3
            assert page.locator(".ai-actions article").count() == 3
            pixels = page.locator("canvas").evaluate("""c => {
                const a = c.getContext('2d').getImageData(0,0,c.width,c.height).data;
                let n=0; for(let i=3;i<a.length;i+=4) if(a[i]) n++; return n;
            }""")
            assert pixels > 100
            sections = page.locator(".it-home > section").evaluate_all(
                "els => els.map(el => el.getBoundingClientRect().height)")
            proportions = [round(value / sum(sections) * 100, 1) for value in sections]
            if width >= 1440:
                assert 15 < proportions[0] < 26, proportions
                assert 53 < proportions[1] < 67, proportions
                assert 15 < proportions[2] < 26, proportions
            page.screenshot(path=str(output / f"dashboard-full-{width}.png"), full_page=True)
            page.screenshot(path=str(output / f"dashboard-viewport-{width}.png"))
            report.append(dict(width=width, proportions=proportions, chart_pixels=pixels))

        page.set_viewport_size(dict(width=1440, height=1000))
        dashboard()
        page.get_by_role("button", name="前端", exact=True).click()
        expect(page.locator(".data-note")).to_contain_text("前端共 7 个岗位样本")
        expect(page.get_by_role("button", name="分析 TypeScript 技能要求")).to_contain_text("100")
        page.get_by_role("button", name="分析 TypeScript 技能要求").click()
        expect(page.locator(".skill-insight")).to_contain_text("TypeScript")
        expect(page.locator(".skill-pairing")).to_contain_text("Vue")
        assert page.locator(".evidence-job").count() == 2
        assert all("TypeScript" in text for text in page.locator(".evidence-job").all_inner_texts())
        page.locator(".evidence-intro button").click()
        page.wait_for_url("**/jobs?**")
        page.wait_for_selector(".job-card")
        assert parse_qs(urlparse(page.url).query) == {"keyword": ["TypeScript"], "category": ["前端"]}
        assert any(path == "/jobs" and query.get("category") == ["前端"] and query.get("keyword") == ["TypeScript"] for path, query in calls)
        assert page.locator(".job-card").count() == 7

        dashboard()
        page.locator(".direction-map-canvas").click(position=dict(x=35, y=35))
        expect(page.locator(".map-legend button[aria-pressed='true']")).to_have_count(1)
        chosen = page.locator(".map-legend button[aria-pressed='true']").get_attribute("aria-label")
        expect(page.locator(".skill-demand h3")).to_contain_text(chosen)
        page.get_by_role("button", name="前端", exact=True).focus()
        page.keyboard.press("Enter")
        expect(page.locator(".skill-demand h3")).to_contain_text("前端")
        page.get_by_role("button", name="产品", exact=True).click()
        expect(page.locator(".skill-demand")).to_contain_text("暂无明确标注")
        assert page.locator(".skill-tile").count() == 0
        assert page.locator(".evidence-job").count() == 2
        page.get_by_role("button", name="全部方向", exact=True).click()
        page.get_by_role("searchbox", name="搜索岗位或技能").fill("  Python  ")
        page.get_by_role("searchbox", name="搜索岗位或技能").press("Enter")
        page.wait_for_url("**/jobs?keyword=Python")
        dashboard()
        first_job_url = page.locator(".evidence-job").first.get_attribute("href")
        page.locator(".evidence-job").first.click()
        page.wait_for_selector(".job-detail-head")
        assert urlparse(page.url).path == first_job_url
        for width in [1440, 390]:
            page.set_viewport_size(dict(width=width, height=1000))
            dashboard("skewed")
            expect(page.locator(".map-insight")).to_contain_text("AI")
            expect(page.locator(".map-insight")).to_contain_text("37%")
            assert page.locator(".map-legend button").count() == 11
            for category, count in SKEWED_COUNTS.items():
                page.get_by_role("button", name=category, exact=True).click()
                expect(page.locator(".data-note")).to_contain_text(f"{category}共 {count} 个岗位样本")
            page.get_by_role("button", name="全部方向", exact=True).click()
            page.wait_for_timeout(600)
            assert not page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"), width
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(200)
            page.screenshot(path=str(output / f"dashboard-map-skewed-{width}.png"), full_page=True)
            page.locator(".market-analysis").screenshot(path=str(output / f"dashboard-charts-{width}.png"))
            page.get_by_role("button", name="后端", exact=True).click()
            page.get_by_role("button", name="分析 Python 技能要求").click()
            page.wait_for_timeout(600)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(200)
            page.screenshot(path=str(output / f"dashboard-map-selected-{width}.png"), full_page=True)
        page.set_viewport_size(dict(width=1440, height=1000))
        dashboard("new")
        expect(page.locator(".ai-source")).to_contain_text("完成就业分析后")
        assert "画像匹配度" not in page.locator(".ai-actions").inner_text()
        expect(page.locator(".personal-status")).to_contain_text("待完善")
        page.screenshot(path=str(output / "dashboard-new-user.png"), full_page=True)

        dashboard("empty")
        expect(page.locator(".distribution")).to_contain_text("暂无岗位样本")
        expect(page.locator(".news-empty")).to_contain_text("暂时没有可展示的资讯")
        assert page.locator("canvas").count() == 0
        page.screenshot(path=str(output / "dashboard-empty.png"), full_page=True)

        dashboard("error")
        expect(page.locator(".industry-section")).to_contain_text("岗位统计暂时无法加载")
        expect(page.locator(".news-notice")).to_contain_text("验收")
        expect(page.locator(".personal-overview")).to_contain_text("部分个人数据暂时无法加载")
        page.screenshot(path=str(output / "dashboard-error.png"), full_page=True)
        state["mode"] = "populated"
        page.get_by_role("button", name="重新加载", exact=True).click()
        page.wait_for_selector(".it-home[aria-busy='false']")
        expect(page.locator(".industry-summary > div").first).to_contain_text("54")
        assert page.locator(".news-item").count() == 3
        assert page.locator(".news-notice").count() == 0
        for width in [1440, 390, 320]:
            page.set_viewport_size(dict(width=width, height=900))
            dashboard("long")
            assert not page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"), width
            boxes = page.locator(".it-home > section").evaluate_all(
                "els => els.map(el => ({top:el.getBoundingClientRect().top,bottom:el.getBoundingClientRect().bottom}))")
            assert all(boxes[i]["bottom"] <= boxes[i + 1]["top"] + 1 for i in range(2))
        assert not errors, errors
        assert not missing, missing
        assert any(path == "/jobs" and query.get("page") == ["2"] for path, query in calls)
        print(json.dumps(dict(viewports=report, interactions="passed", states="passed", errors=errors), ensure_ascii=False))
        browser.close()


if __name__ == "__main__":
    main()

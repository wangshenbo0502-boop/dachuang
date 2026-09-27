"""Browser-assisted BOSS投递流程。

浏览器使用持久化本地 profile 保存登录态，但不接触账号密码，也不自动绕过
验证码或点击最终发送按钮。自动化只负责打开岗位页并尽量填充开场白。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.models.application import JobApplication

try:
    from playwright.async_api import BrowserContext, Page, Playwright, async_playwright
except ImportError:  # pragma: no cover - dependency is installed in runtime
    BrowserContext = Any
    Page = Any
    Playwright = Any
    async_playwright = None


class BossAutomationError(RuntimeError):
    """用户可理解的浏览器自动化错误。"""


class BossAutomationService:
    """管理每个用户一个持久化 BOSS 浏览器上下文。"""

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._contexts: dict[int, BrowserContext] = {}
        self._pages: dict[int, Page] = {}
        self._lock = asyncio.Lock()

    async def _ensure_runtime(self) -> None:
        if async_playwright is None:
            raise BossAutomationError("后端缺少 Playwright，请先安装项目依赖")
        if self._playwright is None:
            self._playwright = await async_playwright().start()

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise BossAutomationError("请填写有效的 BOSS 直聘岗位链接")
        host = parsed.hostname or ""
        if not (host == "zhipin.com" or host.endswith(".zhipin.com")):
            raise BossAutomationError("为保护账号安全，自动投递只支持 zhipin.com 岗位链接")
        if url.rstrip("/") in {"https://www.zhipin.com", "https://www.zhipin.com/"}:
            raise BossAutomationError("请填写具体岗位链接，不要使用 BOSS 首页")

    async def _context_for(self, user_id: int) -> BrowserContext:
        await self._ensure_runtime()
        context = self._contexts.get(user_id)
        if context and not context.pages:
            self._contexts.pop(user_id, None)
            context = None
        if context is None:
            profile_dir = Path(__file__).resolve().parents[2] / ".boss-browser-profiles" / f"user_{user_id}"
            profile_dir.mkdir(parents=True, exist_ok=True)
            try:
                context = await self._playwright.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    headless=False,
                    viewport={"width": 1440, "height": 900},
                    args=["--start-maximized"],
                )
            except Exception as exc:
                raise BossAutomationError(
                    "无法启动 BOSS 浏览器，请确认已执行 playwright install chromium"
                ) from exc
            self._contexts[user_id] = context
        return context

    @staticmethod
    async def _fill_greeting(page: Page, greeting: str) -> bool:
        if not greeting:
            return False
        selectors = [
            "textarea[placeholder*='沟通']",
            "textarea[placeholder*='留言']",
            "textarea[placeholder*='自我介绍']",
            "textarea",
            "[contenteditable='true']",
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if await locator.count() and await locator.is_visible():
                    await locator.fill(greeting)
                    return True
            except Exception:
                continue
        return False

    @staticmethod
    async def _looks_like_login_page(page: Page) -> bool:
        url = page.url.lower()
        if any(part in url for part in ("login", "register", "passport")):
            return True
        text = (await page.locator("body").inner_text(timeout=3000)).lower()
        return any(keyword in text for keyword in ("登录", "扫码登录", "手机号登录", "验证码登录"))

    async def start(self, application: JobApplication) -> dict[str, Any]:
        self._validate_url(application.boss_url)
        async with self._lock:
            context = await self._context_for(application.user_id)
            page = self._pages.get(application.user_id)
            if page is None or page.is_closed():
                page = await context.new_page()
                self._pages[application.user_id] = page
            try:
                await page.goto(application.boss_url, wait_until="domcontentloaded", timeout=30000)
            except Exception as exc:
                raise BossAutomationError("BOSS 岗位页面打开失败，请检查链接或网络后重试") from exc
            await page.wait_for_timeout(1200)
            if await self._looks_like_login_page(page):
                return {
                    "status": "needs_login",
                    "message": "请在打开的 BOSS 页面完成登录或验证码，完成后再次点击一键投递",
                    "url": page.url,
                    "greeting_filled": False,
                }
            greeting_filled = await self._fill_greeting(page, application.greeting)
            return {
                "status": "ready_for_user_confirm",
                "message": "岗位页面已打开，请检查简历和开场白，并在 BOSS 页面点击最终发送",
                "url": page.url,
                "greeting_filled": greeting_filled,
            }

    async def status(self, user_id: int) -> dict[str, Any]:
        async with self._lock:
            page = self._pages.get(user_id)
            if page is None or page.is_closed():
                return {"status": "idle", "url": ""}
            return {"status": "browser_open", "url": page.url}

    async def close(self) -> None:
        async with self._lock:
            for context in self._contexts.values():
                await context.close()
            self._contexts.clear()
            self._pages.clear()
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None


boss_automation_service = BossAutomationService()

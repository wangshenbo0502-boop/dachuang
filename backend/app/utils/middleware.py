"""
文件名称：middleware.py
文件作用：请求日志中间件 + 请求ID追踪 + 简易限流。
记录每个请求的耗时、状态码、请求ID，并按客户端IP做全局与认证接口两级限流。
"""

import re
import time
import uuid
import logging
import threading
from contextvars import ContextVar
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import get_settings

# 请求ID上下文变量（协程安全）
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# 简易限流计数器（单进程内存实现；多 worker 或多实例部署时应改用 Redis）
_rate_limit_store: dict[str, deque[float]] = defaultdict(deque)
_rate_limit_lock = threading.Lock()
_last_sweep = 0.0

# 登录、注册、验证码、重置密码使用单独的严格额度，防止撞库和邮件轰炸
AUTH_RATE_LIMITED_PATHS = frozenset({
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/email/send-code",
    "/api/auth/reset-password",
})

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

logger = logging.getLogger("api.access")


def configure_logging() -> None:
    """配置全局日志格式"""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    # 降低第三方库日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )


def _sweep_expired(now: float, window: int) -> None:
    """定期清理已过期的计数键，避免字典随访问IP数量无限增长。调用方需持有锁。"""
    global _last_sweep
    if now - _last_sweep < window:
        return
    _last_sweep = now
    for key in [k for k, hits in _rate_limit_store.items() if not hits or now - hits[-1] >= window]:
        del _rate_limit_store[key]


def _check_rate_limit(key: str, max_requests: int) -> bool:
    """滑动窗口限流检查。

    Returns:
        True 表示未超限，False 表示已被限流
    """
    settings = get_settings()
    if not settings.RATE_LIMIT_ENABLED:
        return True

    now = time.time()
    window = settings.RATE_LIMIT_WINDOW
    with _rate_limit_lock:
        _sweep_expired(now, window)
        hits = _rate_limit_store[key]
        while hits and now - hits[0] >= window:
            hits.popleft()
        if len(hits) >= max_requests:
            return False
        hits.append(now)
        return True


def _client_ip(request: Request) -> str:
    """识别客户端IP；仅在明确信任反向代理时读取 X-Forwarded-For。"""
    if get_settings().RATE_LIMIT_TRUST_PROXY:
        forwarded = request.headers.get("X-Forwarded-For", "")
        # 取最右侧一项：由最近一层可信代理写入，客户端无法伪造
        candidate = forwarded.split(",")[-1].strip()
        if candidate:
            return candidate
    return request.client.host if request.client else "unknown"


def _request_id(request: Request) -> str:
    """沿用客户端传入的请求ID，但只接受安全字符，防止日志注入。"""
    supplied = request.headers.get("X-Request-ID", "")
    return supplied if _REQUEST_ID_PATTERN.fullmatch(supplied) else str(uuid.uuid4())[:8]


async def request_logging_middleware(request: Request, call_next):
    """请求日志中间件：注入请求ID、记录耗时、检查限流"""
    # 生成或提取请求ID
    request_id = _request_id(request)
    request_id_var.set(request_id)

    # 限流检查：认证接口单独计数，额度更严格
    settings = get_settings()
    client_ip = _client_ip(request)
    allowed = _check_rate_limit(client_ip, settings.RATE_LIMIT_REQUESTS)
    if allowed and request.url.path in AUTH_RATE_LIMITED_PATHS:
        allowed = _check_rate_limit(f"auth:{client_ip}", settings.RATE_LIMIT_AUTH_REQUESTS)
    if not allowed:
        logger.warning(
            f"[{request_id}] 限流触发 | {request.method} {request.url.path} | IP: {client_ip}"
        )
        return JSONResponse(
            status_code=429,
            content={
                "code": 429,
                "message": "请求过于频繁，请稍后再试",
                "data": None,
            },
        )

    start_time = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start_time) * 1000

    # 注入响应头
    response.headers["X-Request-ID"] = request_id

    logger.info(
        f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} "
        f"({elapsed:.1f}ms)"
    )
    return response
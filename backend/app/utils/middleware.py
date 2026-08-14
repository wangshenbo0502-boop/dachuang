"""
文件名称：middleware.py
文件作用：请求日志中间件 + 请求ID追踪 + 简易限流。
记录每个请求的耗时、状态码、请求ID，支持开发环境下的简易限流保护。
"""

import time
import uuid
import logging
from contextvars import ContextVar
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import get_settings

# 请求ID上下文变量（协程安全）
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# 简易限流计数器（开发环境使用字典，生产环境建议用Redis）
_rate_limit_store: dict[str, list[float]] = defaultdict(list)

logger = logging.getLogger("api.access")


def configure_logging() -> None:
    """配置全局日志格式，包含请求ID"""
    settings = get_settings()
    log_format = settings.LOG_FORMAT
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
    )
    # 降低第三方库日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )


def _check_rate_limit(client_ip: str) -> bool:
    """简易滑动窗口限流检查。

    Returns:
        True 表示未超限，False 表示已被限流
    """
    settings = get_settings()
    if not settings.RATE_LIMIT_ENABLED:
        return True

    now = time.time()
    window = settings.RATE_LIMIT_WINDOW
    max_requests = settings.RATE_LIMIT_REQUESTS

    # 清理过期记录
    _rate_limit_store[client_ip] = [
        t for t in _rate_limit_store[client_ip] if now - t < window
    ]

    if len(_rate_limit_store[client_ip]) >= max_requests:
        return False

    _rate_limit_store[client_ip].append(now)
    return True


async def request_logging_middleware(request: Request, call_next):
    """请求日志中间件：注入请求ID、记录耗时、检查限流"""
    # 生成或提取请求ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request_id_var.set(request_id)

    # 限流检查
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
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
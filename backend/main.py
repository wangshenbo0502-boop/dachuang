"""
文件名称：main.py
文件作用：FastAPI 项目启动入口，负责创建应用实例、注册路由以及配置中间件。
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import user, job_match, analysis, resume, growth, streaming
from app.config import get_settings
from app.database.bootstrap import initialize_database_schema
from app.utils.exceptions import AppException
from app.utils.middleware import request_logging_middleware, configure_logging
from app.utils.response import error, success, ErrorCode
from app.ai.deepseek_client import DeepSeekClient

load_dotenv()

# 初始化配置和日志
settings = get_settings()
configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="针对计算机专业大学生的AI就业竞争力分析平台 - 后端API",
    version=settings.APP_VERSION,
    debug=settings.APP_DEBUG,
)


@app.on_event("startup")
def initialize_database() -> None:
    """Create missing tables and upgrade legacy local SQLite user profiles."""
    initialize_database_schema()

# ── 中间件注册 ──

app.middleware("http")(request_logging_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 异常处理器 ──

@app.exception_handler(AppException)
async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error(code=exc.code, message=exc.message),
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for item in exc.errors():
        detail = dict(item)
        # Pydantic may include a non-JSON-serializable ValueError in `ctx`.
        if "ctx" in detail:
            detail["ctx"] = {key: str(value) for key, value in detail["ctx"].items()}
        details.append(detail)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error(code=ErrorCode.PARAM_VALIDATION_ERROR.value, message="参数校验失败", data=details),
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error(code=ErrorCode.INTERNAL_ERROR.value, message="服务器内部错误"),
    )


# ── 健康检查 ──

@app.get("/")
def root():
    return success({
        "service": f"{settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.APP_ENV,
    })


@app.get("/api/health")
def health_check():
    ai_client = DeepSeekClient.instance()
    return success({
        "status": "healthy",
        "environment": settings.APP_ENV,
        "ai_mode": "mock" if ai_client.is_mock_mode else "live",
        "modules": [
            "用户管理（含竞赛/实习经历）",
            "岗位匹配（关键词+AI增强+同义词映射）",
            "AI就业画像分析",
            "AI简历优化",
            "AI成长规划",
            "AI流式响应（SSE）",
            "Token用量统计",
        ]
    })


@app.get("/api/usage")
def get_ai_usage():
    """GET /api/usage — 获取AI Token用量和成本统计"""
    stats = DeepSeekClient.get_usage_stats()
    return success(stats, message="Token用量统计")


# 注册路由
app.include_router(user.router)
app.include_router(job_match.router, prefix="/api", tags=["岗位匹配"])
app.include_router(analysis.router)
app.include_router(resume.router)
app.include_router(growth.router)
app.include_router(streaming.router)  # 流式响应路由

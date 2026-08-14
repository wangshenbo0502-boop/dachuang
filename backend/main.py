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

from app.api import user, job_match, analysis, resume, growth
from app.utils.exceptions import AppException
from app.utils.middleware import request_logging_middleware
from app.utils.response import error, success, ErrorCode

load_dotenv()


def get_cors_origins() -> list[str]:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


app = FastAPI(
    title="AI就业竞争力分析助手",
    description="针对计算机专业大学生的AI就业竞争力分析平台 - 后端API",
    version="1.0.0",
)

# ── 中间件注册 ──

app.middleware("http")(request_logging_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
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
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error(code=ErrorCode.PARAM_VALIDATION_ERROR.value, message="参数校验失败", data=exc.errors()),
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
        "service": "AI就业竞争力分析助手 API",
        "version": "1.0.0",
        "status": "running",
    })


@app.get("/api/health")
def health_check():
    return success({
        "status": "healthy",
        "modules": [
            "用户管理（含竞赛/实习经历）",
            "岗位匹配（关键词+AI增强）",
            "AI就业画像分析",
            "AI简历优化",
            "AI成长规划",
        ]
    })


# 注册路由
app.include_router(user.router)
app.include_router(job_match.router, prefix="/api", tags=["岗位匹配"])
app.include_router(analysis.router)
app.include_router(resume.router)
app.include_router(growth.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
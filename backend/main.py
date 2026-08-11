"""
文件名称：main.py
文件作用：FastAPI 项目启动入口，负责创建应用实例、注册路由以及配置中间件。
负责注册通用中间件、统一异常处理器和后续业务路由。
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import user, job_match
from app.utils.exceptions import AppException
from app.utils.response import error, success

# TODO: 后续导入 analysis、resume、growth 等模块路由

load_dotenv()


def get_cors_origins() -> list[str]:
    """读取允许访问 API 的前端来源，默认仅本地 Vite 服务。"""
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]

app = FastAPI(
    title="AI就业竞争力分析助手",
    description="针对计算机专业大学生的AI就业竞争力分析平台",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
    """将可预期的业务异常转换为统一 API 响应。"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error(code=exc.code, message=exc.message),
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    """将 FastAPI 参数校验错误转换为统一 API 响应。"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error(code=1001, message="参数校验失败", data=exc.errors()),
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
    """隐藏内部实现细节，避免向客户端泄露敏感信息。"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error(code=1, message="服务器内部错误"),
    )


@app.get("/")
def root():
    """根路径健康检查"""
    return success({"service": "AI就业竞争力分析助手 API", "status": "running"})


# 注册学生资料路由
app.include_router(user.router)

# 注册岗位匹配路由
app.include_router(job_match.router, prefix="/api", tags=["岗位匹配"])

# TODO: 注册其余模块路由
# app.include_router(analysis.router, prefix="/api/analysis", tags=["AI分析"])
# app.include_router(resume.router, prefix="/api/resume", tags=["简历优化"])
# app.include_router(growth.router, prefix="/api/growth", tags=["成长规划"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

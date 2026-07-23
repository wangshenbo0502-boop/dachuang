"""
文件名称：main.py
文件作用：FastAPI 项目启动入口，负责创建应用实例、注册路由以及配置中间件。
当前阶段仅搭建项目结构，具体业务功能后续实现。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# TODO: 后续导入各模块路由
# from app.api import user, analysis, job_match, resume, growth

app = FastAPI(
    title="AI就业竞争力分析助手",
    description="针对计算机专业大学生的AI就业竞争力分析平台",
    version="0.1.0",
)

# TODO: 配置 CORS 中间件（生产环境需限制来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """根路径健康检查"""
    return {"message": "AI就业竞争力分析助手 API 运行中"}


# TODO: 注册各模块路由
# app.include_router(user.router, prefix="/api/user", tags=["用户管理"])
# app.include_router(analysis.router, prefix="/api/analysis", tags=["AI分析"])
# app.include_router(job_match.router, prefix="/api/job", tags=["岗位匹配"])
# app.include_router(resume.router, prefix="/api/resume", tags=["简历优化"])
# app.include_router(growth.router, prefix="/api/growth", tags=["成长规划"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

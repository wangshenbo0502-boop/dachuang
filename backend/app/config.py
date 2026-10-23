"""
文件名称：config.py
文件作用：应用配置管理，支持按环境(dev/prod)加载不同配置。
统一管理所有环境变量读取，提供类型安全的配置访问。
"""

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

Environment = Literal["development", "production", "testing"]


class Settings:
    """应用全局配置，所有配置项从环境变量读取，提供合理的默认值。"""

    def __init__(self) -> None:
        # ── 应用基础 ──
        # 未设置 APP_ENV 时按生产环境处理，避免漏配后静默打开调试、关闭限流。
        app_env = os.getenv("APP_ENV", "production").strip().lower()
        if app_env not in ("development", "production", "testing"):
            raise ValueError(f"APP_ENV 只能是 development / production / testing，当前为 {app_env!r}")
        self.APP_ENV: Environment = app_env  # type: ignore[assignment]
        self.APP_DEBUG: bool = not self.is_prod and os.getenv(
            "APP_DEBUG", "true" if self.is_dev else "false"
        ).lower() == "true"
        self.APP_NAME: str = os.getenv("APP_NAME", "IT求职与技术成长系统")
        self.APP_VERSION: str = os.getenv("APP_VERSION", "1.2.0")

        # ── 数据库 ──
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            "sqlite:///./ai_job_analysis.db",
        )
        # Knowledge/RAG uses a dedicated PostgreSQL + pgvector database so that
        # existing user and AI-result tables do not need a forced migration.
        self.KNOWLEDGE_DATABASE_URL: str = os.getenv("KNOWLEDGE_DATABASE_URL", "")
        self.DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5" if self.is_dev else "20"))
        self.DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        self.DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

        # ── Account authentication and QQ email delivery ──
        self.JWT_SECRET: str = os.getenv("JWT_SECRET", "")
        self.INTERNAL_ADMIN_ENABLED: bool = os.getenv("INTERNAL_ADMIN_ENABLED", "false").lower() == "true"
        self.INTERNAL_ADMIN_SERVICE_SECRET: str = os.getenv("INTERNAL_ADMIN_SERVICE_SECRET", "")
        self.JWT_ACCESS_MINUTES: int = max(1, int(os.getenv("JWT_ACCESS_MINUTES", "1440")))
        self.DEV_EMAIL_CODE_MODE: bool = self.is_dev and os.getenv("DEV_EMAIL_CODE_MODE", "false").lower() == "true"
        self.SMTP_HOST: str = os.getenv("SMTP_HOST", "")
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
        self.SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
        self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
        self.SMTP_FROM: str = os.getenv("SMTP_FROM", "")

        # ── CORS ──
        self.CORS_ORIGINS: list[str] = [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if origin.strip()
        ]

        # ── AI 服务 ──
        self.DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.AI_TIMEOUT: float = float(os.getenv("AI_TIMEOUT", "60"))
        self.AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", "3"))
        self.AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "4000"))
        # Token 成本控制
        self.AI_COST_BUDGET_PER_DAY: float = float(
            os.getenv("AI_COST_BUDGET_PER_DAY", "10.0")
        )  # 每日预算(美元)
        self.AI_COST_WARNING_THRESHOLD: float = float(
            os.getenv("AI_COST_WARNING_THRESHOLD", "0.8")
        )  # 预算告警阈值(80%)
        # 每个学生每天可发起的 AI 请求次数，0 表示不限制；仅在接入真实模型时生效
        self.AI_USER_DAILY_LIMIT: int = max(0, int(os.getenv("AI_USER_DAILY_LIMIT", "50")))

        # ── 限流 ──
        self.RATE_LIMIT_ENABLED: bool = (
            os.getenv("RATE_LIMIT_ENABLED", "true" if not self.is_dev else "false").lower() == "true"
        )
        self.RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # 秒
        # 登录、注册、发送验证码、重置密码共用的更严格额度（每个IP每个窗口）
        self.RATE_LIMIT_AUTH_REQUESTS: int = int(os.getenv("RATE_LIMIT_AUTH_REQUESTS", "10"))
        # 部署在 nginx 等反向代理之后时开启，按 X-Forwarded-For 识别真实客户端IP
        self.RATE_LIMIT_TRUST_PROXY: bool = os.getenv("RATE_LIMIT_TRUST_PROXY", "false").lower() == "true"

        # ── 日志 ──
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG" if self.is_dev else "INFO")
        self.LOG_FORMAT: str = os.getenv(
            "LOG_FORMAT",
            "%(asctime)s | %(levelname)s | %(request_id)s | %(message)s",
        )

    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_prod(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == "testing"

    def validate_runtime(self) -> None:
        """生产环境启动前检查关键配置，缺失时拒绝启动而不是带病运行。"""
        if not self.is_prod:
            return
        problems = []
        if len(self.JWT_SECRET) < 32:
            problems.append("JWT_SECRET 未配置或少于 32 个字符")
        if "*" in self.CORS_ORIGINS:
            problems.append("CORS_ORIGINS 不能包含 *")
        if problems:
            raise RuntimeError("生产环境配置不完整：" + "；".join(problems))

    @property
    def ai_enabled(self) -> bool:
        """是否已配置真实AI API Key"""
        return bool(self.DEEPSEEK_API_KEY) and self.DEEPSEEK_API_KEY != "your_deepseek_api_key_here"

    @property
    def db_dialect(self) -> str:
        """数据库类型：sqlite / mysql / postgresql"""
        if self.DATABASE_URL.startswith("sqlite"):
            return "sqlite"
        if "mysql" in self.DATABASE_URL or "pymysql" in self.DATABASE_URL:
            return "mysql"
        if self.DATABASE_URL.startswith("postgresql"):
            return "postgresql"
        return "unknown"


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例（缓存）。"""
    return Settings()

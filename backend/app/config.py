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
        self.APP_ENV: Environment = os.getenv("APP_ENV", "development")  # type: ignore[assignment]
        self.APP_DEBUG: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
        self.APP_NAME: str = os.getenv("APP_NAME", "AI就业竞争力分析助手")
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

        # ── 限流 ──
        self.RATE_LIMIT_ENABLED: bool = (
            os.getenv("RATE_LIMIT_ENABLED", "true" if not self.is_dev else "false").lower() == "true"
        )
        self.RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # 秒

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

import os
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class Settings:
    def __init__(self):
        self.environment = os.getenv("ADMIN_ENV", "development")
        self.database_url = os.getenv("ADMIN_DATABASE_URL", "sqlite:///./admin_control_v1.db")
        self.cookie_secure = self.environment == "production"
        self.cookie_name = "__Secure-dachuang_admin_session" if self.cookie_secure else "dachuang_admin_dev"
        self.origin = os.getenv("ADMIN_ORIGIN", "http://127.0.0.1:5174")
        self.business_base_url = os.getenv("BUSINESS_INTERNAL_BASE_URL",
                                           os.getenv("BUSINESS_BASE_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.service_secret = os.getenv("INTERNAL_ADMIN_SERVICE_SECRET", "")
        if self.environment not in {"development", "testing", "production"}:
            raise ValueError("Invalid ADMIN_ENV")
        if self.cookie_secure and (not self.database_url.startswith("postgresql") or not self.origin.startswith("https://")):
            raise ValueError("Production requires PostgreSQL and HTTPS origin")


@lru_cache
def get_settings():
    return Settings()

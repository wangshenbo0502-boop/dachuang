"""
文件名称：connection.py
文件作用：MySQL 数据库连接配置。
通过环境变量创建 SQLAlchemy 引擎，并提供全项目复用的 ORM Base。
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.utils.exceptions import DatabaseConfigurationError

load_dotenv()


class Base(DeclarativeBase):
    """所有 ORM 数据模型的声明基类。"""


@lru_cache
def get_database_url() -> str:
    """读取数据库连接地址，缺失时返回可识别的配置错误。"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise DatabaseConfigurationError("未配置 DATABASE_URL，请检查 backend/.env 文件")
    return database_url


@lru_cache
def get_engine() -> Engine:
    """创建并缓存 SQLAlchemy 数据库引擎。"""
    database_url = get_database_url()
    engine_options: dict[str, object] = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

    if database_url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}
        if database_url in {"sqlite://", "sqlite:///:memory:"}:
            engine_options["poolclass"] = StaticPool

    try:
        return create_engine(database_url, **engine_options)
    except SQLAlchemyError as exc:
        raise DatabaseConfigurationError("数据库连接配置无效") from exc


def reset_database_connection() -> None:
    """清除连接缓存，供测试或环境变量更新后重新初始化。"""
    get_engine.cache_clear()
    get_database_url.cache_clear()

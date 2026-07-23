"""
文件名称：session.py
文件作用：数据库会话管理，提供依赖注入式的数据库会话获取。
由 FastAPI 在每次请求中创建并关闭同步 SQLAlchemy 会话。
"""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import get_engine


def get_session_factory() -> sessionmaker[Session]:
    """基于当前数据库引擎创建会话工厂。"""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入：获取数据库会话并在请求结束后关闭。"""
    database_session = get_session_factory()()
    try:
        yield database_session
    finally:
        database_session.close()

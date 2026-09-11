"""
文件名称：init_db.py
文件作用：数据库初始化脚本。
运行此脚本将自动创建所有数据库表。
支持MySQL和SQLite（开发阶段默认使用SQLite，无需额外配置）。

使用方法：
    python init_db.py
"""

import os
import sys

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保使用SQLite作为默认数据库（开发阶段）
if not os.getenv("DATABASE_URL") or "your_password" in os.getenv("DATABASE_URL", ""):
    os.environ["DATABASE_URL"] = "sqlite:///./ai_job_analysis.db"
    print("未配置MySQL，使用SQLite数据库: ai_job_analysis.db")


from app.database.bootstrap import initialize_database_schema
from app.database.connection import get_engine, reset_database_connection


def init_database():
    """初始化数据库，创建所有表"""
    # 重置连接缓存（确保使用最新配置）
    reset_database_connection()

    engine = get_engine()

    print("正在创建数据库表并执行兼容迁移...")
    added_columns = initialize_database_schema(engine)
    if added_columns:
        print(f"已补齐 users 表字段: {', '.join(added_columns)}")
    print("数据库初始化完成！")

    # 打印创建的表
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n已创建的数据表 ({len(tables)}):")
    for table in tables:
        print(f"  - {table}")


if __name__ == "__main__":
    print("=" * 50)
    print("AI就业竞争力分析助手 - 数据库初始化")
    print("=" * 50)
    init_database()
    print("=" * 50)
    print("数据库初始化完成！")
    print("\n下一步：")
    print("  1. 运行 python main.py 启动后端服务")
    print("  2. 访问 http://localhost:8000/docs 查看API文档")
    print("  3. 配置DEEPSEEK_API_KEY到.env文件以使用真实AI功能")
    print("=" * 50)

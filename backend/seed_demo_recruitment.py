"""
文件名称：seed_demo_recruitment.py
文件作用：写入站内招聘演示数据（5 家虚构的“示例”企业、18 个已发布岗位）。

使用方法（在 backend 目录下执行，与 init_db.py 相同）：
    python seed_demo_recruitment.py                      # 随机生成演示密码并打印
    python seed_demo_recruitment.py --password 你的密码   # 指定演示密码

可重复执行：已存在的账号和岗位不会重复创建；每次执行都会把演示账号密码
重置为本次使用的密码。APP_ENV=production 时拒绝执行。
"""

import argparse
import os
import secrets
import sys

from dotenv import load_dotenv

load_dotenv()

from app.config import get_settings
from app.database.bootstrap import initialize_database_schema
from app.database.connection import reset_database_connection
from app.database.session import get_session_factory
from app.services.demo_recruitment import DEMO_COMPANIES, seed_demo_recruitment


def main() -> int:
    parser = argparse.ArgumentParser(description="写入站内招聘演示数据")
    parser.add_argument("--password", help="演示招聘者账号密码（至少 8 位）；不填则随机生成")
    args = parser.parse_args()

    settings = get_settings()
    if settings.is_prod:
        print("APP_ENV=production：演示账号密码公开可知，且能查看投递学生的联系方式，已拒绝写入。")
        return 1

    password = args.password or os.getenv("DEMO_RECRUITER_PASSWORD") or secrets.token_urlsafe(9)
    reset_database_connection()
    initialize_database_schema()
    db = get_session_factory()()
    try:
        result = seed_demo_recruitment(db, password)
    except ValueError as exc:
        print(f"写入失败：{exc}")
        return 1
    finally:
        db.close()

    print(f"数据库：{settings.DATABASE_URL}")
    print(f"示例企业 {result['companies']} 家、岗位 {result['jobs']} 个；"
          f"本次新建账号 {result['created_accounts']} 个、岗位 {result['created_jobs']} 个。")
    print("\n招聘者登录（选择“招聘者登录”）：")
    for company in DEMO_COMPANIES:
        print(f"  {company['email']}  {company['profile']['company_name']}")
    print(f"密码：{password}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

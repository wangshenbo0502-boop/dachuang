"""Verify the non-destructive SQLite user-schema compatibility migration."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.database.bootstrap import ensure_sqlite_compatibility_columns
from app.models.user import User


class SqliteUserMigrationTestCase(unittest.TestCase):
    def test_legacy_user_table_is_upgraded_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "legacy.db"
            engine = create_engine(f"sqlite:///{database_path}")
            with engine.begin() as connection:
                connection.execute(text("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(50) NOT NULL,
                        school VARCHAR(100) NOT NULL,
                        major VARCHAR(100) NOT NULL,
                        grade VARCHAR(30) NOT NULL,
                        bio TEXT NOT NULL DEFAULT '',
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                connection.execute(text("""
                    CREATE TABLE user_competitions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        level VARCHAR(30) NOT NULL DEFAULT '校级',
                        award VARCHAR(100) NOT NULL DEFAULT '参与奖',
                        description TEXT NOT NULL DEFAULT ''
                    )
                """))

            self.assertEqual(
                ensure_sqlite_compatibility_columns(engine),
                [
                    "users.email",
                    "users.phone",
                    "users.target_city",
                    "users.target_salary",
                    "user_competitions.competition_date",
                ],
            )
            self.assertEqual(ensure_sqlite_compatibility_columns(engine), [])
            self.assertTrue(
                {"email", "phone", "target_city", "target_salary"}.issubset(
                    {column["name"] for column in inspect(engine).get_columns("users")}
                )
            )
            self.assertIn(
                "competition_date",
                {column["name"] for column in inspect(engine).get_columns("user_competitions")},
            )

            with Session(engine) as session:
                session.add(User(name="迁移验证", school="测试大学", major="计算机", grade="大三"))
                session.commit()
                self.assertEqual(session.query(User).count(), 1)
            engine.dispose()


if __name__ == "__main__":
    unittest.main()

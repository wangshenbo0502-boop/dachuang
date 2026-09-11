"""
File name: test_user_api.py
Purpose: Verify student profile API behavior against an isolated SQLite database.
"""

import os
import sys
import unittest
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite://"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import app.models
from app.config import get_settings
from app.database.connection import Base, get_engine, reset_database_connection
from app.database.session import get_db, get_session_factory
from main import app


class UserApiTestCase(unittest.TestCase):
    """Integration tests for the student profile API contract."""

    @classmethod
    def setUpClass(cls) -> None:
        get_settings.cache_clear()
        reset_database_connection()
        Base.metadata.create_all(get_engine())

    def setUp(self) -> None:
        Base.metadata.drop_all(get_engine())
        Base.metadata.create_all(get_engine())
        self.database_session = get_session_factory()()
        app.dependency_overrides[get_db] = lambda: self.database_session
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.database_session.close()

    @classmethod
    def tearDownClass(cls) -> None:
        Base.metadata.drop_all(get_engine())
        get_engine().dispose()

    def create_user(self) -> int:
        response = self.client.post(
            "/api/users",
            json={
                "name": "Test User",
                "school": "Test University",
                "major": "Computer Science",
                "grade": "2024",
                "bio": "Initial profile",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["code"], 0)
        return response.json()["data"]["id"]

    def test_create_get_update_and_context(self) -> None:
        user_id = self.create_user()

        profile_response = self.client.get(f"/api/users/{user_id}")
        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(profile_response.json()["data"]["name"], "Test User")
        self.assertEqual(profile_response.json()["data"]["skills"], [])

        update_response = self.client.put(
            f"/api/users/{user_id}",
            json={"bio": "Updated profile"},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["data"]["bio"], "Updated profile")

        context_response = self.client.get(f"/api/users/{user_id}/context")
        self.assertEqual(context_response.status_code, 200)
        self.assertEqual(context_response.json()["data"]["user_id"], user_id)
        self.assertEqual(context_response.json()["data"]["bio"], "Updated profile")

    def test_replace_skills_and_projects(self) -> None:
        user_id = self.create_user()

        first_skills_response = self.client.put(
            f"/api/users/{user_id}/skills",
            json={
                "skills": [
                    {"name": "Python", "proficiency": "\u638c\u63e1"},
                    {"name": "SQL", "proficiency": "\u719f\u6089"},
                ]
            },
        )
        self.assertEqual(first_skills_response.status_code, 200)
        self.assertEqual(len(first_skills_response.json()["data"]), 2)

        second_skills_response = self.client.put(
            f"/api/users/{user_id}/skills",
            json={"skills": [{"name": "Java", "proficiency": "\u4e86\u89e3"}]},
        )
        self.assertEqual(second_skills_response.status_code, 200)
        self.assertEqual(second_skills_response.json()["data"][0]["name"], "Java")

        projects_response = self.client.put(
            f"/api/users/{user_id}/projects",
            json={
                "projects": [
                    {
                        "name": "Career Assistant",
                        "role": "Backend Developer",
                        "description": "Built a student profile API.",
                        "tech_stack": ["FastAPI", "MySQL"],
                        "start_date": "2026-07-01",
                        "end_date": "2026-07-23",
                    }
                ]
            },
        )
        self.assertEqual(projects_response.status_code, 200)
        self.assertEqual(projects_response.json()["data"][0]["tech_stack"], ["FastAPI", "MySQL"])

        profile_response = self.client.get(f"/api/users/{user_id}")
        profile_data = profile_response.json()["data"]
        self.assertEqual([skill["name"] for skill in profile_data["skills"]], ["Java"])
        self.assertEqual(len(profile_data["projects"]), 1)

    def test_validation_error_and_missing_user(self) -> None:
        user_id = self.create_user()

        valid_response = self.client.put(
            f"/api/users/{user_id}/skills",
            json={"skills": [{"name": "Python", "proficiency": "\u638c\u63e1"}]},
        )
        self.assertEqual(valid_response.status_code, 200)

        invalid_response = self.client.put(
            f"/api/users/{user_id}/skills",
            json={"skills": [{"name": "Python", "proficiency": "invalid"}]},
        )
        self.assertEqual(invalid_response.status_code, 422)
        self.assertEqual(invalid_response.json()["code"], 1001)

        profile_response = self.client.get(f"/api/users/{user_id}")
        self.assertEqual([skill["name"] for skill in profile_response.json()["data"]["skills"]], ["Python"])

        missing_response = self.client.get("/api/users/999")
        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(missing_response.json()["code"], 3001)


if __name__ == "__main__":
    unittest.main()

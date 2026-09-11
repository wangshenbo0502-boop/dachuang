"""Verify documented AI API contracts with an isolated SQLite database."""

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


class AiApiContractTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        get_settings.cache_clear()
        reset_database_connection()
        Base.metadata.create_all(get_engine())

    def setUp(self) -> None:
        Base.metadata.drop_all(get_engine())
        Base.metadata.create_all(get_engine())
        self.session = get_session_factory()()
        app.dependency_overrides[get_db] = lambda: self.session
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.session.close()

    @classmethod
    def tearDownClass(cls) -> None:
        Base.metadata.drop_all(get_engine())
        get_engine().dispose()

    def create_user(self) -> int:
        response = self.client.post(
            "/api/users",
            json={"name": "Test User", "school": "Test University", "major": "CS", "grade": "大三"},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()["data"]["id"]

    def test_ai_requests_require_documented_profile_source(self) -> None:
        requests = [
            ("/api/analysis", {"target_job": "Java后端开发工程师"}),
            ("/api/resume", {"target_job": "Java后端开发工程师"}),
            ("/api/growth", {"target_job": "Java后端开发工程师"}),
        ]
        for path, payload in requests:
            with self.subTest(path=path):
                response = self.client.post(path, json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["code"], 1001)

    def test_mock_ai_records_and_histories_follow_contract(self) -> None:
        user_id = self.create_user()
        requests = [
            ("/api/analysis", f"/api/analysis/user/{user_id}", {"user_id": user_id, "target_job": "Java后端开发工程师"}),
            ("/api/resume", f"/api/resume/user/{user_id}", {"user_id": user_id, "target_job": "Java后端开发工程师"}),
            ("/api/growth", f"/api/growth/user/{user_id}", {"user_id": user_id, "target_job": "Java后端开发工程师"}),
        ]
        for create_path, history_path, payload in requests:
            with self.subTest(path=create_path):
                created = self.client.post(create_path, json=payload)
                self.assertEqual(created.status_code, 200)
                body = created.json()
                self.assertEqual(body["code"], 0)
                self.assertTrue(body["data"]["is_mock"])
                record_id = body["data"]["id"]

                detail = self.client.get(f"{create_path}/{record_id}")
                self.assertEqual(detail.status_code, 200)
                self.assertEqual(detail.json()["data"]["id"], record_id)

                history = self.client.get(history_path)
                self.assertEqual(history.status_code, 200)
                self.assertEqual(history.json()["data"][0]["id"], record_id)

    def test_match_rejects_unknown_user_before_persisting_record(self) -> None:
        response = self.client.post(
            "/api/match",
            json={"skills": ["Java"], "user_id": 999, "top_k": 1},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["code"], 3001)

    def test_route_inventory_request_id_and_sse_contract(self) -> None:
        expected_paths = {
            "/", "/api/health", "/api/usage", "/api/users", "/api/users/{user_id}",
            "/api/users/{user_id}/skills", "/api/users/{user_id}/projects",
            "/api/users/{user_id}/competitions", "/api/users/{user_id}/internships",
            "/api/users/{user_id}/context", "/api/jobs", "/api/jobs/{job_id}",
            "/api/match", "/api/match/{match_id}", "/api/analysis", "/api/analysis/{analysis_id}",
            "/api/analysis/user/{user_id}", "/api/resume", "/api/resume/{optimization_id}",
            "/api/resume/user/{user_id}", "/api/growth", "/api/growth/{plan_id}",
            "/api/growth/user/{user_id}", "/api/stream/analysis", "/api/stream/resume",
            "/api/stream/growth",
        }
        route_paths = {route.path for route in app.routes if route.path in expected_paths}
        self.assertEqual(route_paths, expected_paths)

        root = self.client.get("/", headers={"X-Request-ID": "contract-1"})
        self.assertEqual(root.status_code, 200)
        self.assertEqual(root.headers.get("X-Request-ID"), "contract-1")

        user_id = self.create_user()
        payloads = {
            "/api/stream/analysis": {"user_id": user_id, "target_job": "Java后端开发工程师"},
            "/api/stream/resume": {"user_id": user_id, "target_job": "Java后端开发工程师"},
            "/api/stream/growth": {"user_id": user_id, "target_job": "Java后端开发工程师"},
        }
        for path, payload in payloads.items():
            with self.subTest(path=path):
                response = self.client.post(path, json=payload)
                self.assertEqual(response.status_code, 200)
                self.assertIn("text/event-stream", response.headers.get("content-type", ""))
                self.assertIn("event: start", response.text)
                self.assertIn("event: complete", response.text)


if __name__ == "__main__":
    unittest.main()

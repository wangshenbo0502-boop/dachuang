"""Regression tests for the unified AI career assistant contracts."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite://"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import app.models  # noqa: F401
from app.ai.deepseek_client import DeepSeekClient
from app.config import get_settings
from app.database.connection import Base, get_engine, reset_database_connection
from app.database.session import get_db, get_session_factory
from main import app
from tests.auth_helpers import create_authenticated_profile


class FakeAssistant:
    def chat_json(self, messages, **kwargs):
        return {
            "reply": "请继续补充一个你亲自负责的细节。",
            "finished": False,
            "extracted": {"skills": [], "projects": [], "competitions": [], "internships": []},
            "missing": [],
        }

    def chat_stream(self, messages, **kwargs):
        yield "这是开放咨询的 Mock 回复。"


class ChatApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_settings.cache_clear()
        reset_database_connection()
        Base.metadata.create_all(get_engine())

    def setUp(self):
        Base.metadata.drop_all(get_engine())
        Base.metadata.create_all(get_engine())
        self.session = get_session_factory()()
        app.dependency_overrides[get_db] = lambda: self.session
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(get_engine())
        get_engine().dispose()

    def create_user(self) -> int:
        return create_authenticated_profile(self.session, self.client, major="Computer Science")

    def test_usage_endpoint_returns_without_deadlock(self):
        self.create_user()
        response = self.client.get("/api/usage")
        self.assertEqual(response.status_code, 200)
        self.assertIn("daily_cost_usd", response.json()["data"])

    def test_profile_turn_accepts_more_than_ten_answers(self):
        user_id = self.create_user()
        messages = []
        for index in range(11):
            messages.extend([
                {"role": "user", "content": f"第{index + 1}次回答"},
                {"role": "assistant", "content": "继续说说。"},
            ])
        with patch.object(DeepSeekClient, "instance", return_value=FakeAssistant()):
            response = self.client.post("/api/chat/profile-turn", json={"user_id": user_id, "messages": messages})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["question_number"], 11)
        self.assertFalse(response.json()["data"]["finished"])

    def test_sync_updates_same_records_and_does_not_invent_missing_facts(self):
        user_id = self.create_user()
        self.client.put(
            f"/api/users/{user_id}/skills",
            json={"skills": [{"name": "Python", "proficiency": "熟悉", "description": "基础"}]},
        )
        payload = {
            "user_id": user_id,
            "profile": {
                "skills": [{"name": "Python", "proficiency": "掌握", "description": "用于数据处理"}],
                "projects": [{"name": "未完成项目"}],
                "competitions": [{"name": "未说明竞赛"}],
                "internships": [{"company": "未说明公司"}],
            },
        }
        response = self.client.post("/api/chat/sync-profile", json=payload)
        self.assertEqual(response.status_code, 200)
        body = response.json()["data"]
        self.assertEqual(body["profile"]["skills"][0]["proficiency"], "掌握")
        self.assertEqual(body["profile"]["skills"][0]["description"], "用于数据处理")
        self.assertEqual(body["profile"]["projects"][0]["role"], "主要负责人")
        self.assertEqual(body["profile"]["projects"][0]["description"], "")
        self.assertEqual(body["profile"]["competitions"][0]["level"], "")
        self.assertEqual(body["profile"]["competitions"][0]["award"], "已参加")
        self.assertEqual(body["profile"]["internships"], [])
        self.assertEqual(body["skipped"], ["实习“未说明公司”缺少公司或岗位"])

    def test_sync_saves_named_experiences_with_missing_optional_details(self):
        user_id = self.create_user()
        for details in ({}, {"role": "", "level": "", "award": ""},
                        {"role": None, "level": None, "award": None},
                        {"role": "  ", "level": "  ", "award": "  "}):
            with self.subTest(details=details):
                payload = {
                    "user_id": user_id,
                    "profile": {
                        "projects": [
                            {"name": "毕业求职agent开发", **details},
                            {"name": "工程实践1 QT游戏", **details},
                        ],
                        "competitions": [
                            {"name": "中国软件杯", **details},
                            {"name": "数据建模大赛", **details},
                        ],
                    },
                }
                response = self.client.post("/api/chat/sync-profile", json=payload)
                self.assertEqual(response.status_code, 200)
                body = response.json()["data"]
                self.assertEqual(body["skipped"], [])
                profile = self.client.get(f"/api/users/{user_id}").json()["data"]
                self.assertEqual(len(profile["projects"]), 2)
                self.assertEqual(len(profile["competitions"]), 2)
                for project in profile["projects"]:
                    self.assertEqual(project["role"], "主要负责人")
                    self.assertEqual(project["description"], "")
                for competition in profile["competitions"]:
                    self.assertEqual(competition["level"], "")
                    self.assertEqual(competition["award"], "已参加")
                # Exercise creation for every missing/blank variant, not just merging.
                self.client.put(f"/api/users/{user_id}/projects", json={"projects": []})
                self.client.put(f"/api/users/{user_id}/competitions", json={"competitions": []})

    def test_sync_preserves_explicit_details_and_allows_later_corrections(self):
        user_id = self.create_user()

        def sync(project, competition):
            response = self.client.post("/api/chat/sync-profile", json={
                "user_id": user_id,
                "profile": {
                    "projects": [{"name": "求职助手", **project}],
                    "competitions": [{"name": "软件杯", **competition}],
                },
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["data"]["skipped"], [])
            return response.json()["data"]["profile"]

        original = sync({}, {})
        updated = sync(
            {"role": "前端开发", "description": "实现档案页面"},
            {"level": "省级", "award": "二等奖"},
        )
        for empty in ({}, {"role": "", "level": "", "award": ""},
                      {"role": None, "level": None, "award": None}):
            updated = sync(empty, empty)
            self.assertEqual(len(updated["projects"]), 1)
            self.assertEqual(updated["projects"][0]["id"], original["projects"][0]["id"])
            self.assertEqual(updated["projects"][0]["role"], "前端开发")
            self.assertEqual(updated["projects"][0]["description"], "实现档案页面")
            self.assertEqual(len(updated["competitions"]), 1)
            self.assertEqual(updated["competitions"][0]["id"], original["competitions"][0]["id"])
            self.assertEqual(updated["competitions"][0]["level"], "省级")
            self.assertEqual(updated["competitions"][0]["award"], "二等奖")

    def test_profile_prompt_does_not_require_optional_experience_details(self):
        user_id = self.create_user()
        assistant = FakeAssistant()
        with patch.object(assistant, "chat_json", wraps=assistant.chat_json) as chat, patch.object(
            DeepSeekClient, "instance", return_value=assistant
        ):
            response = self.client.post("/api/chat/profile-turn", json={"user_id": user_id})
        self.assertEqual(response.status_code, 200)
        prompt = chat.call_args.args[0][0]["content"]
        self.assertIn("不要将这些选填字段列入 missing", prompt)
        self.assertIn("主要负责人", prompt)
        self.assertIn("已参加", prompt)

    def test_sync_saves_new_skill_as_unknown_when_proficiency_is_unclear(self):
        user_id = self.create_user()
        response = self.client.post(
            "/api/chat/sync-profile",
            json={
                "user_id": user_id,
                "profile": {"skills": [{"name": "Rust", "description": "接触过基础语法"}]},
            },
        )
        self.assertEqual(response.status_code, 200)
        skills = response.json()["data"]["profile"]["skills"]
        self.assertEqual(skills[0]["name"], "Rust")
        self.assertEqual(skills[0]["proficiency"], "未知")

    def test_sync_rolls_back_the_whole_draft_when_commit_fails(self):
        user_id = self.create_user()
        with patch.object(self.session, "commit", side_effect=RuntimeError("commit failed")), patch.object(
            self.session, "rollback", wraps=self.session.rollback
        ) as rollback:
            response = self.client.post(
                "/api/chat/sync-profile",
                json={
                    "user_id": user_id,
                    "profile": {
                        "bio": "不应被部分保存",
                        "skills": [{"name": "Python", "proficiency": "掌握"}],
                    },
                },
            )
        self.assertEqual(response.status_code, 500)
        rollback.assert_called_once()
        profile = self.client.get(f"/api/users/{user_id}").json()["data"]
        self.assertEqual(profile["bio"], "")
        self.assertEqual(profile["skills"], [])

    def test_conversation_stream_returns_sse(self):
        user_id = self.create_user()
        with patch.object(DeepSeekClient, "instance", return_value=FakeAssistant()):
            response = self.client.post(
                "/api/chat/conversation-stream",
                json={"user_id": user_id, "target_job": "前端开发", "messages": [{"role": "user", "content": "怎么准备面试"}]},
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers.get("content-type", ""))
        self.assertIn("event: chunk", response.text)
        self.assertIn("event: complete", response.text)


if __name__ == "__main__":
    unittest.main()

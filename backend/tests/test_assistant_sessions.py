"""AI assistant conversations are stored server-side and private to their owner."""
import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401
from app.auth.security import hash_password, issue_token
from app.database.connection import Base, get_engine
from app.database.session import get_db, get_session_factory
from app.knowledge.knowledge_service import KnowledgeService
from app.models.account import Account
from app.models.user import User
from main import app
from tests.auth_helpers import create_authenticated_profile


@pytest.fixture
def api():
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = get_session_factory()()
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app, raise_server_exceptions=False)
    yield client, db
    app.dependency_overrides.clear()
    db.close()


def _token_for_new_account(db, role="student"):
    email = f"{200000000 + db.query(User).count()}@qq.com"
    profile = User(name="另一位同学", school="X", major="Y", grade="大三", bio="", email=email)
    db.add(profile)
    db.flush()
    account = Account(username=email.split("@")[0], email=email, profile_id=profile.id,
                      password_hash=hash_password("correct-password"), email_verified=True, role=role)
    db.add(account)
    db.commit()
    return {"Authorization": f"Bearer {issue_token(account.id, account.token_version)}"}


def _payload(text="怎么准备面试"):
    return {
        "title": text,
        "mode": "consult",
        "target": "前端开发",
        "consultMessages": [
            {"id": "m1", "role": "user", "content": text, "createdAt": "2026-10-24T08:00:00Z"},
            {"id": "m2", "role": "assistant", "content": "先梳理项目经历。", "createdAt": "2026-10-24T08:00:05Z"},
        ],
        "profileMessages": [],
        "draft": {"skills": [{"name": "Vue"}]},
        "suggestedAction": "resume",
    }


def test_owner_can_save_list_read_update_and_delete(api):
    client, db = api
    create_authenticated_profile(db, client)
    assert client.put("/api/chat/sessions/s-1", json=_payload()).status_code == 200
    listed = client.get("/api/chat/sessions").json()["data"]
    assert [item["id"] for item in listed] == ["s-1"]
    # 列表只返回摘要，不带消息正文
    assert "consultMessages" not in listed[0]
    detail = client.get("/api/chat/sessions/s-1").json()["data"]
    assert detail["consultMessages"][1]["content"] == "先梳理项目经历。"
    assert detail["draft"] == {"skills": [{"name": "Vue"}]}

    assert client.put("/api/chat/sessions/s-1", json=_payload("改成问简历")).status_code == 200
    assert client.get("/api/chat/sessions/s-1").json()["data"]["title"] == "改成问简历"
    assert len(client.get("/api/chat/sessions").json()["data"]) == 1

    assert client.delete("/api/chat/sessions/s-1").status_code == 200
    assert client.get("/api/chat/sessions/s-1").status_code == 404


def test_other_students_cannot_see_or_change_a_conversation(api):
    client, db = api
    create_authenticated_profile(db, client)
    client.put("/api/chat/sessions/private-1", json=_payload("我的私人困惑"))
    other = _token_for_new_account(db)

    assert client.get("/api/chat/sessions", headers=other).json()["data"] == []
    assert client.get("/api/chat/sessions/private-1", headers=other).status_code == 404
    # 同一编号在对方名下是独立的新对话，不会覆盖原主人的数据
    assert client.put("/api/chat/sessions/private-1", json=_payload("别人的"), headers=other).status_code == 200
    assert client.delete("/api/chat/sessions/private-1", headers=other).status_code == 200
    mine = client.get("/api/chat/sessions/private-1").json()["data"]
    assert mine["title"] == "我的私人困惑"


def test_recruiters_and_anonymous_users_are_rejected(api):
    client, db = api
    recruiter = _token_for_new_account(db, role="recruiter")
    assert client.get("/api/chat/sessions", headers=recruiter).status_code == 403
    assert client.get("/api/chat/sessions").status_code == 401


def test_invalid_payloads_are_rejected(api):
    client, db = api
    create_authenticated_profile(db, client)
    assert client.put("/api/chat/sessions/bad id!", json=_payload()).status_code == 422
    bad_role = _payload()
    bad_role["consultMessages"][0]["role"] = "system"
    assert client.put("/api/chat/sessions/s-2", json=bad_role).status_code == 422
    huge = _payload()
    huge["draft"] = {"bio": "x" * 200_000}
    assert client.put("/api/chat/sessions/s-3", json=huge).status_code == 422


def test_knowledge_errors_do_not_leak_internal_details(api, monkeypatch):
    client, db = api
    create_authenticated_profile(db, client)

    class Broken:
        def search(self, *args, **kwargs):
            raise RuntimeError("could not connect to postgresql://ai_job:secret@10.0.0.5")

        def health(self):
            return {"status": "failed", "postgresql": False, "error": "password authentication failed for ai_job"}

    monkeypatch.setattr(KnowledgeService, "instance", classmethod(lambda cls: Broken()))
    response = client.post("/api/knowledge/search", json={"query": "面试"})
    assert response.status_code == 503
    assert "secret" not in response.text and "10.0.0.5" not in response.text
    health = client.get("/api/knowledge/health")
    assert health.status_code == 503
    assert "password" not in health.text

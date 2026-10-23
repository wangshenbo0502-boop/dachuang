"""AI quota, AI budget, rate limiting and production-config safeguards."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401
from app.ai.deepseek_client import AIServiceError, DeepSeekClient
from app.config import Settings, get_settings
from app.database.connection import Base, get_engine
from app.database.session import get_db, get_session_factory
from app.models.ai_usage import AIUsageDaily
from app.utils import middleware
from main import app
from tests.auth_helpers import create_authenticated_profile


class FakeAssistant:
    is_mock_mode = False

    def chat_json(self, messages, **kwargs):
        return {"reply": "继续说说。", "finished": False, "extracted": {}, "missing": []}

    def chat_stream(self, messages, **kwargs):
        yield "好的"


@pytest.fixture
def api(monkeypatch):
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = get_session_factory()()
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app, raise_server_exceptions=False)
    yield client, db
    app.dependency_overrides.clear()
    db.close()
    get_settings.cache_clear()


def _live_ai(monkeypatch, limit: int) -> None:
    """模拟已配置真实模型：额度只在 live 模式下生效。"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-not-real")
    monkeypatch.setenv("AI_USER_DAILY_LIMIT", str(limit))
    get_settings.cache_clear()


def _profile_turn(client, user_id):
    return client.post("/api/chat/profile-turn", json={"user_id": user_id, "messages": [{"role": "user", "content": "你好"}]})


def test_daily_ai_quota_blocks_after_limit(api, monkeypatch):
    client, db = api
    user_id = create_authenticated_profile(db, client)
    _live_ai(monkeypatch, limit=2)
    with patch.object(DeepSeekClient, "instance", return_value=FakeAssistant()):
        assert _profile_turn(client, user_id).status_code == 200
        assert _profile_turn(client, user_id).status_code == 200
        blocked = _profile_turn(client, user_id)
    assert blocked.status_code == 429
    assert blocked.json()["code"] == 3005
    assert db.query(AIUsageDaily).filter_by(user_id=user_id).one().request_count == 2


def test_quota_is_not_consumed_by_forbidden_requests(api, monkeypatch):
    client, db = api
    user_id = create_authenticated_profile(db, client)
    _live_ai(monkeypatch, limit=1)
    with patch.object(DeepSeekClient, "instance", return_value=FakeAssistant()):
        assert _profile_turn(client, user_id + 999).status_code == 403
        assert _profile_turn(client, user_id).status_code == 200


def test_mock_mode_does_not_count_against_quota(api, monkeypatch):
    client, db = api
    user_id = create_authenticated_profile(db, client)
    monkeypatch.setenv("AI_USER_DAILY_LIMIT", "1")
    get_settings.cache_clear()
    with patch.object(DeepSeekClient, "instance", return_value=FakeAssistant()):
        for _ in range(3):
            assert _profile_turn(client, user_id).status_code == 200
    assert db.query(AIUsageDaily).count() == 0


def test_over_budget_client_refuses_live_calls(monkeypatch):
    client = DeepSeekClient.__new__(DeepSeekClient)
    client._mock_mode = False
    monkeypatch.setattr(DeepSeekClient._usage_tracker, "is_over_budget", lambda: True)
    with pytest.raises(AIServiceError) as exc:
        client.chat([{"role": "user", "content": "hi"}])
    assert exc.value.error_type == AIServiceError.TYPE_BUDGET_EXCEEDED
    with pytest.raises(AIServiceError):
        next(client.chat_stream([{"role": "user", "content": "hi"}]))


def test_ai_errors_are_not_leaked_to_clients(api):
    client, db = api
    user_id = create_authenticated_profile(db, client)

    class Broken(FakeAssistant):
        def chat_json(self, messages, **kwargs):
            raise AIServiceError("AI API错误: 401 - upstream secret detail")

    with patch.object(DeepSeekClient, "instance", return_value=Broken()):
        response = _profile_turn(client, user_id)
    assert response.status_code == 502
    assert "upstream secret detail" not in response.text


def test_auth_endpoints_have_stricter_rate_limit(api, monkeypatch):
    client, _ = api
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_AUTH_REQUESTS", "3")
    get_settings.cache_clear()
    middleware._rate_limit_store.clear()
    body = {"email": "100000001@qq.com", "password": "wrong-password"}
    statuses = [client.post("/api/auth/login", json=body).status_code for _ in range(4)]
    assert statuses == [401, 401, 401, 429]
    # 普通接口使用全局额度，不受认证额度影响
    assert client.get("/").status_code == 200
    middleware._rate_limit_store.clear()


def test_rate_limit_store_drops_expired_keys(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    get_settings.cache_clear()
    middleware._rate_limit_store.clear()
    middleware._rate_limit_store["stale"].append(0.0)
    monkeypatch.setattr(middleware, "_last_sweep", 0.0)
    assert middleware._check_rate_limit("fresh", 10)
    assert "stale" not in middleware._rate_limit_store
    middleware._rate_limit_store.clear()
    get_settings.cache_clear()


def test_request_id_header_is_sanitized(api):
    client, _ = api
    assert client.get("/", headers={"X-Request-ID": "ok-123"}).headers["X-Request-ID"] == "ok-123"
    injected = client.get("/", headers={"X-Request-ID": "x\tFAKE LOG LINE"}).headers["X-Request-ID"]
    assert injected != "x\tFAKE LOG LINE" and "FAKE" not in injected


def test_missing_app_env_defaults_to_production(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("APP_DEBUG", raising=False)
    monkeypatch.delenv("RATE_LIMIT_ENABLED", raising=False)
    monkeypatch.setenv("DEV_EMAIL_CODE_MODE", "true")
    settings = Settings()
    assert settings.is_prod
    assert not settings.APP_DEBUG
    assert settings.RATE_LIMIT_ENABLED
    assert not settings.DEV_EMAIL_CODE_MODE


def test_production_debug_cannot_be_forced_on(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_DEBUG", "true")
    assert not Settings().APP_DEBUG


def test_invalid_app_env_is_rejected(monkeypatch):
    monkeypatch.setenv("APP_ENV", "prod")
    with pytest.raises(ValueError):
        Settings()


def test_production_requires_strong_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "short")
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        Settings().validate_runtime()
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    Settings().validate_runtime()

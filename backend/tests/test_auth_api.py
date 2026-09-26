"""End-to-end account registration, token, and ownership regressions."""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import jwt
import pytest
from fastapi.testclient import TestClient
import app.models  # noqa: F401
from app.database.connection import Base, get_engine
from app.database.session import get_db, get_session_factory
from app.models.account import Account, EmailCode
from app.auth.security import verify_password
from app.config import get_settings
from main import app

@pytest.fixture
def auth_api():
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = get_session_factory()()
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app, raise_server_exceptions=False)
    codes = {}
    with patch("app.api.auth._send_mail", side_effect=lambda email, code, purpose: codes.__setitem__((email, purpose), code)):
        yield client, db, codes
    app.dependency_overrides.clear()
    db.close()

def register(client, codes, email, name="测试同学"):
    assert client.post("/api/auth/email/send-code", json={"email": email}).status_code == 200
    response = client.post("/api/auth/register", json={
        "email": email, "code": codes[(email, "REGISTER")], "password": "correct-password",
        "confirm_password": "correct-password", "name": name,
    })
    assert response.status_code == 201, response.json()
    return response.json()["data"]

def headers(payload):
    return {"Authorization": "Bearer " + payload["access_token"]}

def test_registration_login_me_logout_and_hash(auth_api):
    client, db, codes = auth_api
    assert client.post("/api/auth/email/send-code", json={"email": "not-qq@example.com"}).status_code == 422
    account = register(client, codes, "123456789@qq.com")
    stored = db.get(Account, account["user"]["id"])
    assert stored.password_hash != "correct-password"
    assert stored.password_hash.startswith("$argon2id$")
    assert verify_password("correct-password", stored.password_hash)
    assert "password_hash" not in str(account)
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers=headers(account)).json()["data"]["profile_id"] == stored.profile_id
    assert client.post("/api/auth/email/send-code", json={"email": stored.email}).status_code == 409
    assert client.post("/api/auth/login", json={"email": stored.email, "password": "wrong"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "987654321@qq.com", "password": "wrong"}).status_code == 401
    logged_in = client.post("/api/auth/login", json={"email": stored.email, "password": "correct-password"})
    assert logged_in.status_code == 200
    assert client.post("/api/auth/logout", headers=headers(logged_in.json()["data"])).status_code == 200
    assert client.get("/api/auth/me", headers=headers(logged_in.json()["data"])).status_code == 401

def test_code_expiry_errors_and_rate_limits(auth_api):
    client, db, codes = auth_api
    email = "111222333@qq.com"
    assert client.post("/api/auth/email/send-code", json={"email": email}).status_code == 200
    assert client.post("/api/auth/email/send-code", json={"email": email}).status_code == 429
    for _ in range(5):
        assert client.post("/api/auth/register", json={"email": email, "code": "000000", "password": "correct-password", "confirm_password": "correct-password"}).status_code == 400
    assert client.post("/api/auth/register", json={"email": email, "code": codes[(email, "REGISTER")], "password": "correct-password", "confirm_password": "correct-password"}).status_code == 429
    row = db.query(EmailCode).filter_by(email=email).one()
    row.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1)
    db.commit()
    assert client.post("/api/auth/register", json={"email": email, "code": codes[(email, "REGISTER")], "password": "correct-password", "confirm_password": "correct-password"}).status_code == 400

def test_two_users_cannot_read_or_write_each_others_data(auth_api):
    client, db, codes = auth_api
    a = register(client, codes, "222333444@qq.com")
    b = register(client, codes, "333444555@qq.com")
    aid, bid = a["user"]["profile_id"], b["user"]["profile_id"]
    ah = headers(a)
    assert client.get(f"/api/users/{bid}", headers=ah).status_code == 403
    assert client.put(f"/api/users/{bid}", headers=ah, json={"name": "越权"}).status_code == 403
    assert client.get(f"/api/analysis/user/{bid}", headers=ah).status_code == 403
    assert client.post("/api/chat/turn", headers=ah, json={"user_id": bid, "messages": []}).status_code == 403
    assert client.post("/api/match", headers=ah, json={"skills": ["Python"], "user_id": bid}).status_code == 403
    assert client.post("/api/stream/analysis", headers=ah, json={"user_id": bid, "target_job": "Python"}).status_code == 403
    version = client.post("/api/resume/versions", headers=headers(b), json={"user_id": bid, "name": "校招简历", "target_job": "Python工程师"})
    assert version.status_code == 200, version.json()
    version_id = version.json()["data"]["id"]
    assert client.get(f"/api/resume/versions/{version_id}", headers=ah).status_code == 403
    assert client.put(f"/api/resume/versions/{version_id}", headers=ah, json={"name": "越权修改"}).status_code == 403
    assert client.get(f"/api/resume/versions/{version_id}", headers=headers(b)).json()["data"]["name"] == "校招简历"
    assert client.get(f"/api/users/{aid}").status_code == 401
    assert client.get("/api/users/me", headers=ah).json()["data"]["id"] == aid
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401

def test_sql_injection_strings_are_rejected_or_parameterized(auth_api):
    client, db, codes = auth_api
    assert client.post("/api/auth/login", json={"email": "1' OR 1=1--@qq.com", "password": "x"}).status_code == 422
    account = register(client, codes, "555666777@qq.com")
    assert client.post("/api/auth/login", json={"email": "555666777@qq.com", "password": "' OR 1=1 --"}).status_code == 401
    assert client.get("/api/auth/me", headers=headers(account)).status_code == 200

def test_expired_token_and_disabled_account(auth_api):
    client, db, codes = auth_api
    payload = register(client, codes, "777888999@qq.com")
    account = db.get(Account, payload["user"]["id"])
    expired = jwt.encode({
        "sub": str(account.id), "ver": account.token_version,
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }, get_settings().JWT_SECRET, algorithm="HS256")
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    account.is_active = False
    db.commit()
    assert client.get("/api/auth/me", headers=headers(payload)).status_code == 403

def test_password_reset_uses_qq_code_and_revokes_old_token(auth_api):
    client, db, codes = auth_api
    email = "888999000@qq.com"
    original = register(client, codes, email)
    assert client.post("/api/auth/email/send-code", json={"email": email, "purpose": "RESET_PASSWORD"}).status_code == 200
    code = codes[(email, "RESET_PASSWORD")]
    wrong = client.post("/api/auth/reset-password", json={"email": email, "code": "000000", "password": "new-password", "confirm_password": "new-password"})
    assert wrong.status_code == 400
    changed = client.post("/api/auth/reset-password", json={"email": email, "code": code, "password": "new-password", "confirm_password": "new-password"})
    assert changed.status_code == 200
    assert client.get("/api/auth/me", headers=headers(original)).status_code == 401
    assert client.post("/api/auth/login", json={"email": email, "password": "correct-password"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": email, "password": "new-password"}).status_code == 200

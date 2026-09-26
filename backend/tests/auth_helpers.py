"""Authenticated profile fixture for pre-existing API contract tests."""
from app.auth.security import hash_password, issue_token
from app.models.account import Account
from app.models.user import User

def create_authenticated_profile(session, client, name="Test User", major="CS"):
    email = f"{100000000 + session.query(User).count()}@qq.com"
    profile = User(name=name, school="Test University", major=major, grade="大三", bio="", email=email)
    session.add(profile)
    session.flush()
    account = Account(username=email.split("@")[0], email=email, profile_id=profile.id, password_hash=hash_password("correct-password"), email_verified=True)
    session.add(account)
    session.commit()
    client.headers.update({"Authorization": f"Bearer {issue_token(account.id, account.token_version)}"})
    return profile.id

import hashlib
import hmac
from dataclasses import dataclass
from uuid import UUID
import jwt
from fastapi import Header, HTTPException, Request
from app.config import get_settings


def request_digest(method, target, body, key):
    return hashlib.sha256(f"{method.upper()}\n{target}\n{key}\n".encode() + body).hexdigest()


@dataclass(frozen=True)
class ServiceActor:
    id: str
    request_hash: str
    scope: str


def require_service_scope(scope):
    async def dependency(request: Request, authorization: str | None = Header(None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(401, "需要服务凭证")
        try:
            claims = jwt.decode(authorization[7:], get_settings().INTERNAL_ADMIN_SERVICE_SECRET,
                                algorithms=["HS256"], issuer="dachuang-admin-service",
                                audience="dachuang-business-internal",
                                options={"require": ["iss", "aud", "sub", "actor", "scope", "req", "iat", "exp", "jti"]})
            actor = str(UUID(claims["actor"]))
            UUID(claims["jti"])
            if claims["sub"] != "admin-service" or type(claims["iat"]) is not int or type(claims["exp"]) is not int or not 0 < claims["exp"]-claims["iat"] <= 30:
                raise ValueError()
        except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError):
            raise HTTPException(401, "服务凭证无效") from None
        if claims["scope"] != scope:
            raise HTTPException(403, "服务权限不足")
        path = request.scope.get("raw_path", request.url.path.encode()).decode("ascii")
        query = request.scope.get("query_string", b"").decode("ascii")
        target = path + ("?" + query if query else "")
        digest = request_digest(request.method, target, await request.body(), request.headers.get("idempotency-key", ""))
        if not isinstance(claims["req"], str) or not hmac.compare_digest(digest, claims["req"]):
            raise HTTPException(403, "服务请求内容不匹配")
        return ServiceActor(actor, digest, scope)
    return dependency

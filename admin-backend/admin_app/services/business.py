import hashlib
import json
import time
from uuid import uuid4
import httpx
import jwt
from fastapi import HTTPException
from ..config import get_settings

client: httpx.AsyncClient | None = None


def encode_body(body):
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def request_digest(method, target, body, key):
    return hashlib.sha256(f"{method.upper()}\n{target}\n{key}\n".encode() + body).hexdigest()


def sign_call(actor, scope, method, target, body, key):
    secret = get_settings().service_secret
    if len(secret.encode()) < 32:
        raise HTTPException(503, "内部服务配置不可用")
    now = int(time.time())
    return jwt.encode({"iss": "dachuang-admin-service", "aud": "dachuang-business-internal",
                      "sub": "admin-service", "actor": actor, "scope": scope,
                      "req": request_digest(method, target, body, key), "iat": now,
                      "exp": now+30, "jti": str(uuid4())}, secret, algorithm="HS256")


async def send(method, path, *, actor, scope, key="", raw=b""):
    if client is None:
        raise HTTPException(503, "业务服务暂不可用")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Idempotency-Key"] = key
    request = client.build_request(method, path, content=raw, headers=headers)
    request.headers["Authorization"] = "Bearer " + sign_call(actor, scope, method,
            request.url.raw_path.decode("ascii"), raw, key)
    return await client.send(request)


async def query(path, *, actor, scope):
    try:
        response = await send("GET", path, actor=actor, scope=scope)
        payload = response.json()
    except httpx.HTTPError:
        raise HTTPException(503, "业务服务暂不可用") from None
    except ValueError:
        raise HTTPException(502, "业务服务响应格式错误") from None
    if not isinstance(payload, dict) or not all(k in payload for k in ("code", "message", "data", "request_id")):
        raise HTTPException(502, "业务服务响应格式错误")
    if response.status_code >= 500:
        raise HTTPException(503, "业务服务暂不可用")
    if response.status_code >= 400:
        raise HTTPException(response.status_code, payload["message"])
    if payload["code"] != 0:
        raise HTTPException(502, "业务服务响应格式错误")
    return payload

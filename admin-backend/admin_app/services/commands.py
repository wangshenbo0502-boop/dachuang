import asyncio
import json
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from ..db import SessionLocal
from ..models import AdminCommand, AdminAuditLog
from ..permissions import can
from .audit import record
from .business import encode_body, request_digest, send

locks = {}
TERMINAL = {"succeeded", "rejected"}


def command_path(row):
    suffix = "status" if row.target_type == "accounts" else "moderation"
    return f"/internal/admin/v1/{row.target_type}/{row.target_id}/{suffix}"


def dto(row):
    return {"command_id": row.command_id, "state": row.status, "operation": row.operation,
            "resource_id": str(row.target_id), "created_at": row.created_at,
            "updated_at": row.updated_at, "result": row.result if row.status in TERMINAL else None}


def accept_command(admin, kind, resource_id, body, key):
    raw = encode_body(body)
    operation = "accounts:status_write" if kind == "accounts" else "jobs:moderate"
    path = f"/internal/admin/v1/{kind}/{resource_id}/" + ("status" if kind == "accounts" else "moderation")
    digest = request_digest("POST", path, raw, key)
    try:
        with SessionLocal.begin() as db:
            row = db.get(AdminCommand, key)
            if row:
                if row.actor_id != admin.id or row.request_hash != digest:
                    raise HTTPException(409, "幂等键已绑定其他请求")
                return key
            db.add(AdminCommand(command_id=key, actor_id=admin.id, operation=operation,
                target_type=kind, target_id=resource_id, expected_version=body["expected_version"],
                request_body=body, request_hash=digest, frozen_body=raw.decode(), status="pending"))
            record(db, admin.id, operation, target_type=kind, target_id=resource_id, result="pending",
                   detail={"reason": body["reason"]}, command_id=key, event_kind="accepted")
    except IntegrityError:
        with SessionLocal() as db:
            row = db.get(AdminCommand, key)
            if not row:
                raise
            if row.actor_id != admin.id or row.request_hash != digest:
                raise HTTPException(409, "幂等键已绑定其他请求") from None
    return key


def mark_unknown(key, reason):
    with SessionLocal.begin() as db:
        db.execute(update(AdminCommand).where(AdminCommand.command_id == key,
                    AdminCommand.status.in_(["pending", "unknown"])).values(status="unknown", error_code=reason))


def record_business_result(key, receipt):
    with SessionLocal.begin() as db:
        row = db.get(AdminCommand, key)
        if not row:
            return
        required = {"command_id", "actor_id", "operation", "resource_id", "request_hash", "http_status", "response", "before", "after"}
        if not isinstance(receipt, dict) or not required.issubset(receipt):
            raise ValueError("invalid receipt")
        response, status = receipt["response"], receipt["http_status"]
        if receipt["command_id"] != key or receipt["actor_id"] != row.actor_id or receipt["request_hash"] != row.request_hash or receipt["operation"] != row.operation or receipt["resource_id"] != str(row.target_id):
            raise ValueError("receipt mismatch")
        if not isinstance(response, dict) or response.get("request_id") != key or not {"code", "message", "data"}.issubset(response):
            raise ValueError("invalid envelope")
        if not (status == 200 and response["code"] == 0 or status in {404, 409, 422} and response["code"] != 0):
            raise ValueError("invalid outcome")
        state = "succeeded" if status == 200 else "rejected"
        changed = db.execute(update(AdminCommand).where(AdminCommand.command_id == key,
                  AdminCommand.status.in_(["pending", "unknown"])).values(status=state,
                  result={"http_status": status, "response": response}), execution_options={"synchronize_session": False})
        if changed.rowcount:
            record(db, row.actor_id, row.operation, target_type=row.target_type, target_id=row.target_id,
                   result=state, detail={"reason": row.request_body["reason"], "before": receipt["before"], "after": receipt["after"]},
                   command_id=key, event_kind="terminal")


async def reconcile_unlocked(key):
    with SessionLocal() as db:
        row = db.get(AdminCommand, key)
        if not row or row.status in TERMINAL:
            return
        actor = row.actor_id
    try:
        response = await send("GET", f"/internal/admin/v1/commands/{key}", actor=actor, scope="commands:read")
        if response.status_code == 200:
            payload = response.json()
            if payload.get("code") == 0:
                record_business_result(key, payload["data"])
    except Exception:
        # Receipt reads cannot authorize or trigger another write.
        return


async def reconcile_command(key):
    async with locks.setdefault(key, asyncio.Lock()):
        await reconcile_unlocked(key)


async def dispatch_command(key):
    async with locks.setdefault(key, asyncio.Lock()):
        await reconcile_unlocked(key)
        with SessionLocal() as db:
            row = db.get(AdminCommand, key)
            if not row or row.status in TERMINAL:
                return
            path, raw, actor, scope = command_path(row), row.frozen_body.encode(), row.actor_id, row.operation
        try:
            response = await send("POST", path, actor=actor, scope=scope, key=key, raw=raw)
            if response.status_code not in {200, 404, 409, 422}:
                mark_unknown(key, "upstream_unconfirmed")
                return
            # A body alone is not proof of execution: confirm the durable receipt.
            mark_unknown(key, "awaiting_receipt")
            await reconcile_unlocked(key)
        except Exception:
            mark_unknown(key, "transport_or_persistence_error")


async def retry_command(key, admin):
    with SessionLocal() as db:
        row = db.get(AdminCommand, key)
        if not row:
            raise HTTPException(404, "命令不存在")
        if admin.role != "super_admin" and (row.actor_id != admin.id or not can(admin.role, row.operation)):
            raise HTTPException(403, "没有重试原命令的权限")
        if row.status in TERMINAL:
            return
        record(db, admin.id, "commands.retry", target_type=row.target_type, target_id=row.target_id,
               detail={"command_id": key})
        db.commit()
    await dispatch_command(key)


async def recovery_scan():
    while True:
        with SessionLocal() as db:
            keys = db.scalars(select(AdminCommand.command_id).where(
                AdminCommand.status.in_(["pending", "unknown"])).order_by(AdminCommand.updated_at).limit(20)).all()
        for key in keys:
            await reconcile_command(key)
            await asyncio.sleep(.1)
        await asyncio.sleep(10)

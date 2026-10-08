from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.database.session import get_session_factory
from app.models.account import Account
from app.models.recruitment import RecruitmentJob
from app.models.admin_receipt import BusinessAdminReceipt
from .queries import envelope


def replay(row, actor):
    if row.actor_id != actor.id or row.request_hash != actor.request_hash:
        raise HTTPException(409, "幂等键已用于其他请求")
    return row.http_status, row.response_json


def execute(*, kind, resource_id, key, body, actor):
    model = Account if kind == "accounts" else RecruitmentJob
    field = "is_active" if kind == "accounts" else "moderation_status"
    desired = getattr(body, field)
    factory = get_session_factory()
    try:
        with factory.begin() as db:
            receipt = db.get(BusinessAdminReceipt, key)
            if receipt:
                return replay(receipt, actor)
            receipt = BusinessAdminReceipt(command_id=key, actor_id=actor.id, operation=actor.scope,
                        resource_id=str(resource_id), request_hash=actor.request_hash, reason=body.reason,
                        before_json={}, after_json={}, http_status=500, response_json={})
            db.add(receipt)
            db.flush()
            current = db.execute(select(getattr(model, field), model.management_version).where(model.id == resource_id)).mappings().first()
            if not current:
                status, payload = 404, envelope(code=6404, message="对象不存在", request_id=key)
            elif current["management_version"] != body.expected_version or current[field] == desired:
                status, payload = 409, envelope(code=6409, message="对象已变化或已处于目标状态，请刷新", request_id=key)
            else:
                values = {field: desired, "management_version": model.management_version + 1}
                if kind == "accounts":
                    values["token_version"] = Account.token_version + 1
                changed = db.execute(update(model).where(model.id == resource_id,
                            model.management_version == body.expected_version, getattr(model, field) == current[field])
                            .values(**values), execution_options={"synchronize_session": False})
                if changed.rowcount != 1:
                    status, payload = 409, envelope(code=6409, message="对象已变化，请刷新", request_id=key)
                else:
                    receipt.before_json = dict(current)
                    receipt.after_json = {field: desired, "management_version": body.expected_version+1}
                    status, payload = 200, envelope({"command_id": key, "id": resource_id, **receipt.after_json}, request_id=key)
            receipt.http_status, receipt.response_json = status, payload
        return status, payload
    except IntegrityError:
        with factory() as db:
            committed = db.get(BusinessAdminReceipt, key)
            if not committed:
                raise
            return replay(committed, actor)


def receipt_dto(row):
    return {"command_id": row.command_id, "actor_id": row.actor_id, "operation": row.operation,
            "resource_id": row.resource_id, "request_hash": row.request_hash, "reason": row.reason,
            "before": row.before_json, "after": row.after_json, "http_status": row.http_status,
            "response": row.response_json, "created_at": row.created_at}

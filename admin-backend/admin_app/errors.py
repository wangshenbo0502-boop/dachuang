from datetime import datetime, timezone
from uuid import uuid4
from fastapi.encoders import jsonable_encoder

ERROR_CODES = {401: 6101, 403: 6103, 404: 6404, 409: 6409, 422: 6422, 429: 6429, 502: 6502, 503: 6503}


def envelope(data=None, *, message="success", code=0, request_id=None):
    def utc(value):
        return value.replace(tzinfo=timezone.utc).isoformat() if value.tzinfo is None else value.astimezone(timezone.utc).isoformat()
    return jsonable_encoder({"code": code, "message": message, "data": data, "request_id": request_id or str(uuid4())},
                            custom_encoder={datetime: utc})

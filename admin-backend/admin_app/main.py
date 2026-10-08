from contextlib import asynccontextmanager
import asyncio
from contextlib import suppress
import httpx
from fastapi import FastAPI, HTTPException, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from .db import Base, engine
from . import models
from .api_auth import router as auth_router
from .api_queries import router as query_router
from .api_commands import router as command_router
from .api_admins import router as admin_router
from .api_audit import router as audit_router
from .config import get_settings
from .errors import envelope, ERROR_CODES
from .services import business
from .services.commands import recovery_scan


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with engine.connect() as db:
        if db.execute(text("SELECT COUNT(*) FROM admin_security_lock")).scalar_one() == 0:
            db.execute(text("INSERT INTO admin_security_lock (id, revision) VALUES (1, 0)"))
            db.commit()
    business.client = httpx.AsyncClient(base_url=get_settings().business_base_url,
        timeout=httpx.Timeout(10.0, connect=2.0, pool=2.0), trust_env=False, follow_redirects=False)
    task = asyncio.create_task(recovery_scan())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        await business.client.aclose()
        business.client = None


app = FastAPI(title="独立管理员控制台", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root():
    return {"service": "admin-backend", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/health/live")
def live():
    return {"status": "alive"}


@app.get("/health/ready")
def ready():
    try:
        with engine.connect() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(503, "管理数据库不可用") from None


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content=envelope(
        code=ERROR_CODES.get(exc.status_code, 6503), message=str(exc.detail)))


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    fields = [{"loc": list(x["loc"]), "type": x["type"]} for x in exc.errors()]
    return JSONResponse(status_code=422, content=envelope(fields, code=6422, message="参数校验失败"))


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    return JSONResponse(status_code=503, content=envelope(code=6503, message="管理服务暂不可用"))


app.include_router(auth_router, prefix="/admin-api/v1")
app.include_router(query_router, prefix="/admin-api/v1")
app.include_router(command_router, prefix="/admin-api/v1")
app.include_router(admin_router, prefix="/admin-api/v1")
app.include_router(audit_router, prefix="/admin-api/v1")

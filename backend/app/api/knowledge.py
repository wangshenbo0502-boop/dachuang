"""Read-only knowledge retrieval API backed exclusively by PostgreSQL/pgvector.

Document writes, re-indexing and retrieval debugging are operator tasks and are
performed through scripts/seed_knowledge.py, not through the student API.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.knowledge.knowledge_service import KnowledgeService, KnowledgeUnavailableError
from app.schemas.knowledge import KnowledgeSearchRequest
from app.utils.exceptions import AppException, ResourceNotFoundError
from app.utils.response import success

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/knowledge", tags=["知识库"])


def _service() -> KnowledgeService:
    return KnowledgeService.instance()


def _knowledge_error(exc: Exception) -> AppException:
    # 异常原文可能包含数据库地址等内部信息，只写日志不返回给前端
    logger.warning("knowledge service unavailable: %s", exc, exc_info=exc)
    return AppException(message="知识库服务暂不可用，请稍后重试", code=3101, status_code=503)


@router.get("")
def list_documents(
    category: str | None = Query(default=None),
) -> dict:
    try:
        return success(_service().list_documents(category), message="知识文档列表获取成功")
    except Exception as exc:
        raise _knowledge_error(exc) from exc


@router.post("/search")
def search_knowledge(body: KnowledgeSearchRequest) -> dict:
    try:
        results = _service().search(body.query, category=body.category, top_k=body.top_k, filters=body.filters)
        return success({"query": body.query, "results": results}, message="知识检索完成")
    except Exception as exc:
        raise _knowledge_error(exc) from exc


@router.get("/health")
def knowledge_health() -> dict:
    result = _service().health()
    if "error" in result:
        logger.warning("knowledge health check failed: %s", result["error"])
        result = {key: value for key, value in result.items() if key != "error"}
    payload = success(result, message="知识库健康检查完成")
    if result.get("status") == "failed":
        return JSONResponse(status_code=503, content=payload)
    return payload


@router.get("/documents/{document_id}")
def get_document(document_id: int = Path(ge=1)) -> dict:
    try:
        item = _service().get_document_by_id(document_id)
    except Exception as exc:
        raise _knowledge_error(exc) from exc
    if not item:
        raise ResourceNotFoundError(f"知识文档 {document_id} 不存在")
    return success(item, message="知识文档获取成功")


@router.get("/stats")
def knowledge_stats() -> dict:
    try:
        return success(_service().stats(), message="知识库统计获取成功")
    except Exception as exc:
        raise _knowledge_error(exc) from exc

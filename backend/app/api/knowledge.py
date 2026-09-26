"""Knowledge management and retrieval API backed exclusively by PostgreSQL/pgvector."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.knowledge.knowledge_service import KnowledgeService, KnowledgeUnavailableError
from app.schemas.knowledge import KnowledgeDocumentCreate, KnowledgeSearchRequest
from app.utils.exceptions import AppException, ResourceNotFoundError
from app.utils.response import success

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/knowledge", tags=["知识库"])


def _service() -> KnowledgeService:
    return KnowledgeService.instance()


def _knowledge_error(exc: Exception) -> AppException:
    return AppException(message=f"知识库服务暂不可用：{exc}", code=3101, status_code=503)


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


@router.post("/search/debug")
def debug_search_knowledge(body: KnowledgeSearchRequest) -> dict:
    try:
        result = _service().debug_search(body.query, category=body.category, top_k=body.top_k, filters=body.filters)
        return success(result, message="RAG 检索链路调试完成")
    except Exception as exc:
        raise _knowledge_error(exc) from exc


@router.get("/health")
def knowledge_health() -> dict:
    result = _service().health()
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


@router.post("/documents", status_code=201)
def create_document(body: KnowledgeDocumentCreate) -> dict:
    try:
        document_id = _service().create_document(
            title=body.title,
            source=body.source,
            category=body.category,
            content=body.content,
            metadata=body.metadata,
        )
        return success({"id": document_id, "status": "pending"}, message="知识文档创建成功")
    except Exception as exc:
        raise _knowledge_error(exc) from exc


@router.delete("/documents/{document_id}")
def delete_document(document_id: int = Path(ge=1)) -> dict:
    try:
        deleted = _service().delete_document(document_id)
    except Exception as exc:
        raise _knowledge_error(exc) from exc
    if not deleted:
        raise ResourceNotFoundError(f"知识文档 {document_id} 不存在")
    return success({"id": document_id}, message="知识文档删除成功")


@router.post("/documents/{document_id}/index")
def index_document(document_id: int = Path(ge=1)) -> dict:
    try:
        result = _service().index_document(document_id, force=True)
    except KeyError as exc:
        raise ResourceNotFoundError(f"知识文档 {document_id} 不存在") from exc
    except Exception as exc:
        raise _knowledge_error(exc) from exc
    return success(result, message="知识文档索引完成")


@router.post("/reindex")
def reindex_documents() -> dict:
    try:
        results = []
        for item in _service().list_documents():
            results.append(_service().index_document(item["id"], force=True))
        return success({"documents": len(results), "results": results}, message="知识库重建完成")
    except Exception as exc:
        raise _knowledge_error(exc) from exc


@router.get("/stats")
def knowledge_stats() -> dict:
    try:
        return success(_service().stats(), message="知识库统计获取成功")
    except Exception as exc:
        raise _knowledge_error(exc) from exc

"""Backend adapter for the PostgreSQL + pgvector knowledge service."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Optional

_KNOWLEDGE_ROOT = Path(__file__).resolve().parents[3] / "knowledge"
if str(_KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(_KNOWLEDGE_ROOT))


class KnowledgeUnavailableError(RuntimeError):
    pass


class KnowledgeService:
    """Stable backend facade; all formal retrieval is delegated to pgvector."""

    _instance: Optional["KnowledgeService"] = None

    def __init__(self) -> None:
        self._service = None

    @classmethod
    def instance(cls) -> "KnowledgeService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _core(self):
        if self._service is None:
            try:
                from service.knowledge_service import KnowledgeService as CoreKnowledgeService
                self._service = CoreKnowledgeService()
            except Exception as exc:
                raise KnowledgeUnavailableError(f"knowledge service initialization failed: {exc}") from exc
        return self._service

    def initialize(self) -> None:
        self._core().initialize()

    def search(self, query: str, category: str | None = None, top_k: int = 10, filters=None) -> list[dict[str, Any]]:
        results = self._core().search(query, top_k=top_k, category=category, filters=filters)
        return [self._legacy_result(item) for item in results]

    def retrieve_context(self, query: str, category: str | None = None, top_k: int = 5) -> dict[str, Any]:
        return self._core().retrieve_context(query, top_k=top_k, category=category)

    def debug_search(self, query: str, category: str | None = None, top_k: int = 5, filters=None) -> dict[str, Any]:
        return self._core().debug_search(query, top_k=top_k, category=category, filters=filters)

    def health(self) -> dict[str, Any]:
        return self._core().health()

    def list_documents(self, category: str | None = None) -> list[dict[str, Any]]:
        return [self._legacy_document(item) for item in self._core().list_documents(category=category)]

    def get_document(self, category: str, doc_id: str) -> dict[str, Any] | None:
        for item in self.list_documents(category):
            if item["doc_id"] == doc_id:
                return item
        return None

    def get_document_by_id(self, document_id: int) -> dict[str, Any] | None:
        item = self._core().get_document(document_id)
        return self._legacy_document(item) if item else None

    def create_document(self, title: str, source: str, category: str, content: str, metadata: dict | None = None) -> int:
        return self._core().create_document(title, source, category, content, metadata)

    def index_document(self, document_id: int, force: bool = True) -> dict[str, Any]:
        return self._core().index_existing_document(document_id, force=force)

    def delete_document(self, document_id: int) -> bool:
        return self._core().delete_document(document_id)

    def stats(self) -> dict[str, Any]:
        return self._core().stats()

    def list_categories(self) -> list[dict[str, Any]]:
        stats = self.stats()
        return [{"category": key, "count": value} for key, value in sorted(stats.get("categories", {}).items())]

    def get_skill_requirements(self, job_id: str) -> list[str]:
        doc = self.get_document("jobs", job_id)
        if not doc:
            return []
        tags = doc.get("metadata", {}).get("tags", [])
        if tags:
            return [str(tag).lower() for tag in tags if tag]
        content = doc.get("content", "")
        match = re.search(r"核心技能要求.*?\n((?:\s*[-*]\s*.+\n?)+)", content, re.IGNORECASE)
        if not match:
            return []
        return [value.strip().lower() for value in re.findall(r"[-*]\s*(.+)", match.group(1)) if value.strip()]

    @staticmethod
    def _legacy_document(item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        result.setdefault("doc_id", Path(result.get("source", "unknown")).stem)
        result.setdefault("filename", Path(result.get("source", "unknown")).name)
        result.setdefault("metadata", {})
        result["metadata"] = {
            "title": result.get("title") or result["doc_id"],
            "category": result.get("category", "general"),
            **result["metadata"],
        }
        return result

    @classmethod
    def _legacy_result(cls, item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        result["doc_id"] = Path(result.get("source", "unknown")).stem
        result["filename"] = Path(result.get("source", "unknown")).name
        result["metadata"] = {
            "title": result.get("title") or result["doc_id"],
            "category": result.get("category", "general"),
            **(result.get("metadata") or {}),
        }
        return result

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

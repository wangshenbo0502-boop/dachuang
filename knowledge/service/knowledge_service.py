"""Application-facing knowledge operations and retrieval orchestration."""
from __future__ import annotations

import logging
from typing import Any

from config import KnowledgeSettings, get_knowledge_settings, normalize_category
from embedding.factory import create_embedding_model
from loaders.base import Document
from pipeline.index_pipeline import IndexPipeline
from pipeline.rag_pipeline import RAGPipeline
from reranker.factory import create_reranker
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.keyword_retriever import KeywordRetriever
from retrieval.query_rewriter import QueryRewriteService
from retrieval.vector_retriever import VectorRetriever
from service.context_builder import ContextBuilder
from vector_store.pgvector_store import PgVectorStore

logger = logging.getLogger(__name__)


class KnowledgeService:
    def __init__(self, settings: KnowledgeSettings | None = None) -> None:
        self.settings = settings or get_knowledge_settings()
        self._store: PgVectorStore | None = None
        self._embeddings = None
        self._retriever = None
        self._pipeline = None
        self.context_builder = ContextBuilder(self.settings)
        self.query_rewriter = QueryRewriteService(
            self.settings.query_rewrite_enabled,
            self.settings.query_rewrite_llm_enabled,
        )
        self.reranker = create_reranker(self.settings)
        self._rag_pipeline = None

    @property
    def store(self) -> PgVectorStore:
        if self._store is None:
            self._store = PgVectorStore(self.settings)
        return self._store

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = create_embedding_model(self.settings)
        return self._embeddings

    @property
    def retriever(self):
        if self._retriever is None:
            self._retriever = HybridRetriever(
                VectorRetriever(self.embeddings, self.store),
                KeywordRetriever(self.store),
                self.settings,
            )
        return self._retriever

    @property
    def pipeline(self) -> IndexPipeline:
        if self._pipeline is None:
            self._pipeline = IndexPipeline(self.settings, self.embeddings, self.store)
        return self._pipeline

    @property
    def rag_pipeline(self) -> RAGPipeline:
        if self._rag_pipeline is None:
            self._rag_pipeline = RAGPipeline(
                self.retriever,
                self.reranker,
                self.context_builder,
                self.query_rewriter,
                self.settings,
            )
        return self._rag_pipeline

    def initialize(self) -> None:
        self.store.initialize()

    def run_pipeline(self, query: str, top_k: int | None = None, category: str | None = None, filters=None) -> dict[str, Any]:
        return self.rag_pipeline.run(query, top_k=top_k, category=category, filters=filters)

    def search(self, query: str, top_k: int | None = None, category: str | None = None, filters=None) -> list[dict[str, Any]]:
        return self.run_pipeline(query, top_k=top_k, category=category, filters=filters)["results"]

    def retrieve_context(self, query: str, top_k: int | None = None, category: str | None = None) -> dict[str, Any]:
        payload = self.run_pipeline(query, top_k=top_k, category=category)
        return {key: payload[key] for key in ("context", "sources", "results")}

    def debug_search(self, query: str, top_k: int | None = None, category: str | None = None, filters=None) -> dict[str, Any]:
        return self.run_pipeline(query, top_k=top_k, category=category, filters=filters)

    def health(self) -> dict[str, Any]:
        checks = self.store.health()
        checks["embedding"] = {"provider": self.settings.embedding_provider, "model": self.settings.embedding_model}
        checks["reranker"] = {
            "enabled": self.settings.reranker_enabled,
            "provider": self.settings.reranker_provider,
            "model": self.settings.reranker_model if self.settings.reranker_enabled else None,
            "status": "configured" if self.settings.reranker_enabled else "fallback_noop",
        }
        return checks

    @staticmethod
    def sources(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return RAGPipeline.sources(results)

    def list_documents(self, category: str | None = None, limit: int = 500, offset: int = 0) -> list[dict[str, Any]]:
        return self.store.list_documents(category=category, limit=limit, offset=offset)

    def get_document(self, document_id: int) -> dict[str, Any] | None:
        return self.store.get_document(document_id)

    def create_document(self, title: str, source: str, category: str, content: str, metadata: dict | None = None) -> int:
        document = Document(
            title=title,
            source=source,
            category=normalize_category(category),
            content=content,
            metadata=metadata or {},
        )
        digest = IndexPipeline.content_hash(document)
        return self.store.create_document(
            {"title": title, "source": source, "category": category, "content": content, "metadata": metadata or {}, "content_hash": digest}
        )

    def index_existing_document(self, document_id: int, force: bool = True) -> dict[str, Any]:
        row = self.store.get_document(document_id)
        if row is None:
            raise KeyError(document_id)
        document = Document(
            id=row["id"], title=row["title"], source=row["source"], category=row["category"], content=row["content"], metadata=row["metadata"]
        )
        return self.pipeline.index_document(document, force=force)

    def delete_document(self, document_id: int) -> bool:
        return self.store.delete_document(document_id)

    def stats(self) -> dict[str, Any]:
        return self.store.stats()

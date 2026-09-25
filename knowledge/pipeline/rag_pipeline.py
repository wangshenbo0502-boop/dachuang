"""唯一的生产 RAG 技术执行链。"""
from __future__ import annotations

import time
from typing import Any

from config import KnowledgeSettings, get_knowledge_settings
from retrieval.filters import KnowledgeFilter
from retrieval.query_rewriter import QueryRewriteService


class RAGPipeline:
    """Query -> rewrite -> filter -> hybrid retrieval -> rerank -> context."""

    def __init__(
        self,
        retriever,
        reranker,
        context_builder,
        query_rewriter: QueryRewriteService | None = None,
        settings: KnowledgeSettings | None = None,
    ) -> None:
        self.settings = settings or get_knowledge_settings()
        self.retriever = retriever
        self.reranker = reranker
        self.context_builder = context_builder
        self.query_rewriter = query_rewriter or QueryRewriteService(
            self.settings.query_rewrite_enabled,
            self.settings.query_rewrite_llm_enabled,
        )

    def run(
        self,
        query: str,
        *,
        top_k: int | None = None,
        category: str | None = None,
        filters: KnowledgeFilter | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not query or not query.strip():
            return {"results": [], "context": "", "sources": [], "trace": {}}

        limit = top_k or self.settings.top_k
        total_started = time.perf_counter()
        trace: dict[str, Any] = {"query": query.strip(), "latency": {}, "counts": {}}
        rewrite_started = time.perf_counter()
        rewrite = self.query_rewriter.analyze(query)
        trace.update(rewrite.as_dict())
        trace["latency"]["query_rewrite_ms"] = self._elapsed(rewrite_started)

        effective_filters = KnowledgeFilter.from_value(filters or rewrite.filters, category=category)
        trace["filters"] = {
            "categories": effective_filters.categories,
            "job_type": effective_filters.job_type,
            "skill": effective_filters.skill,
            "source": effective_filters.source,
            "document_id": effective_filters.document_id,
            "tags": effective_filters.tags,
        }

        retrieval_started = time.perf_counter()
        candidates = self.retriever.retrieve(
            rewrite.original_query,
            top_k=self.settings.fusion_candidate_k,
            category=category,
            vector_query=rewrite.rewritten_query,
            filters=effective_filters,
            trace=trace,
        )
        trace["latency"]["retrieval_and_rrf_ms"] = self._elapsed(retrieval_started)

        rerank_started = time.perf_counter()
        results = self.reranker.rerank(rewrite.original_query, candidates, limit)
        trace["latency"]["rerank_ms"] = self._elapsed(rerank_started)
        trace["rerank_results"] = results

        context_started = time.perf_counter()
        context = self.context_builder.build(results)
        trace["latency"]["context_build_ms"] = self._elapsed(context_started)
        trace["latency"]["llm_ms"] = None
        trace["counts"] = {
            "vector_candidates": len(trace.get("vector_results", [])),
            "keyword_candidates": len(trace.get("keyword_results", [])),
            "rrf_candidates": len(trace.get("rrf_results", [])),
            "rerank_candidates": len(results),
            "final_context_count": len(results),
        }
        trace["latency"]["total_ms"] = self._elapsed(total_started)
        return {
            "results": results,
            "context": context,
            "sources": self.sources(results),
            "trace": trace,
        }

    @staticmethod
    def _elapsed(started: float) -> float:
        return round((time.perf_counter() - started) * 1000, 3)

    @staticmethod
    def sources(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "chunk_id": item.get("chunk_id"),
                "document_id": item.get("document_id"),
                "title": item.get("title"),
                "category": item.get("category"),
                "score": item.get("score"),
                "source": item.get("source"),
                "retrieval_source": item.get("retrieval_source", item.get("retrieval_mode")),
                "vector_score": item.get("vector_score", 0.0),
                "keyword_score": item.get("keyword_score", 0.0),
                "rrf_score": item.get("rrf_score", 0.0),
                "rerank_score": item.get("rerank_score"),
            }
            for item in results
        ]

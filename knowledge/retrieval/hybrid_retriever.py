from __future__ import annotations
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from config import KnowledgeSettings, get_knowledge_settings
from retrieval.rrf import RRFMerger

logger = logging.getLogger(__name__)


class HybridRetriever:
    def __init__(self, vector_retriever, keyword_retriever, settings: KnowledgeSettings | None = None) -> None:
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.settings = settings or get_knowledge_settings()
        self.merger = RRFMerger(self.settings.rrf_k)

    @staticmethod
    def _retrieve(retriever, query, top_k, category, filters):
        try:
            return retriever.retrieve(query, top_k, category, filters)
        except TypeError as exc:
            if "positional" not in str(exc):
                raise
            return retriever.retrieve(query, top_k, category)

    def retrieve(self, query: str, top_k: int | None = None, category: str | None = None, *, vector_query: str | None = None, filters=None, trace: dict | None = None) -> list[dict]:
        limit = top_k or self.settings.top_k
        vector_results: list[dict] = []
        keyword_results: list[dict] = []
        vector_error: Exception | None = None
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="rag-retrieval") as executor:
            vector_future = executor.submit(self._retrieve, self.vector_retriever, vector_query or query, self.settings.vector_candidate_k, category, filters)
            keyword_future = executor.submit(self._retrieve, self.keyword_retriever, query, self.settings.keyword_candidate_k, category, filters)
            try:
                vector_results = vector_future.result()
            except Exception as exc:
                vector_error = exc
                logger.exception("vector_retrieval_failed category=%s", category)
            try:
                keyword_results = keyword_future.result()
            except Exception:
                logger.exception("keyword_retrieval_failed category=%s", category)
        parallel_ms = round((time.perf_counter() - started) * 1000, 3)
        if trace is not None:
            latency = trace.setdefault("latency", {})
            latency["embedding_ms"] = getattr(self.vector_retriever, "last_embedding_ms", 0.0)
            latency["vector_search_ms"] = getattr(self.vector_retriever, "last_search_ms", parallel_ms)
            latency["keyword_search_ms"] = getattr(self.keyword_retriever, "last_search_ms", parallel_ms)
        if not vector_results and not keyword_results and vector_error:
            raise vector_error
        started = time.perf_counter()
        results = self.merger.merge([vector_results, keyword_results], top_k=limit)
        if trace is not None:
            trace.setdefault("latency", {})["rrf_ms"] = round((time.perf_counter() - started) * 1000, 3)
            trace["vector_results"] = vector_results
            trace["keyword_results"] = keyword_results
            trace["rrf_results"] = results
        return results

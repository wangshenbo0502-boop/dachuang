from __future__ import annotations
import time
from vector_store.pgvector_store import PgVectorStore


class KeywordRetriever:
    def __init__(self, store: PgVectorStore) -> None:
        self.store = store
        self.last_search_ms = 0.0

    def retrieve(self, query: str, top_k: int = 5, category: str | None = None, filters=None) -> list[dict]:
        if not query.strip():
            return []
        started = time.perf_counter()
        results = self.store.keyword_search(query.strip(), top_k=top_k, category=category, filters=filters)
        self.last_search_ms = round((time.perf_counter() - started) * 1000, 3)
        return results

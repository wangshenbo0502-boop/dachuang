from __future__ import annotations
import logging
import time
from embedding.base import EmbeddingModel
from vector_store.pgvector_store import PgVectorStore

logger = logging.getLogger(__name__)


class VectorRetriever:
    def __init__(self, embeddings: EmbeddingModel, store: PgVectorStore) -> None:
        self.embeddings = embeddings
        self.store = store
        self.last_embedding_ms = 0.0
        self.last_search_ms = 0.0

    def retrieve(self, query: str, top_k: int = 5, category: str | None = None, filters=None) -> list[dict]:
        if not query.strip():
            return []
        started = time.perf_counter()
        vector = self.embeddings.embed_query(query.strip())
        self.last_embedding_ms = round((time.perf_counter() - started) * 1000, 3)
        started = time.perf_counter()
        results = self.store.search(vector, top_k=top_k, category=category, filters=filters)
        self.last_search_ms = round((time.perf_counter() - started) * 1000, 3)
        return results


HNSWRetriever = VectorRetriever

"""Production local embedding provider backed by sentence-transformers."""
from __future__ import annotations

import logging
import time
from typing import Any

from embedding.base import EmbeddingError, EmbeddingModel

logger = logging.getLogger(__name__)


class LocalEmbeddingProvider(EmbeddingModel):
    def __init__(self, model_name: str, dimension: int, batch_size: int = 32) -> None:
        self.model_name = model_name
        self.dimension = dimension
        self.batch_size = batch_size
        self._model: Any = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise EmbeddingError("sentence-transformers is not installed; install backend requirements") from exc
            started = time.perf_counter()
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as exc:
                raise EmbeddingError(f"failed to load embedding model {self.model_name}: {exc}") from exc
            logger.info("embedding_model_loaded model=%s elapsed_ms=%.2f", self.model_name, (time.perf_counter() - started) * 1000)
        return self._model

    def embed_query(self, text: str) -> list[float]:
        values = self.embed_documents([text])
        if not values:
            raise EmbeddingError("embedding provider returned no query vector")
        return values[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if any(not text or not text.strip() for text in texts):
            raise EmbeddingError("cannot embed empty text")
        if not texts:
            return []
        started = time.perf_counter()
        try:
            vectors = self._get_model().encode(
                texts,
                batch_size=self.batch_size,
                normalize_embeddings=True,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
        except Exception as exc:
            raise EmbeddingError(f"embedding failed: {exc}") from exc
        result = [[float(value) for value in vector] for vector in vectors]
        for vector in result:
            if len(vector) != self.dimension:
                raise EmbeddingError(f"embedding dimension mismatch: expected {self.dimension}, got {len(vector)}")
        logger.info("embedding_completed count=%s elapsed_ms=%.2f", len(result), (time.perf_counter() - started) * 1000)
        return result

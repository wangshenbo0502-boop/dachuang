from __future__ import annotations
import os
from embedding.base import EmbeddingError, EmbeddingModel
from embedding.local import LocalEmbeddingProvider
from config import KnowledgeSettings, get_knowledge_settings


class MockEmbeddingProvider(EmbeddingModel):
    """Deterministic test double. Factory refuses it outside testing."""
    def __init__(self, dimension: int = 8) -> None:
        self.dimension = dimension

    def _embed(self, text: str) -> list[float]:
        values = [0.0] * self.dimension
        for index, byte in enumerate(text.encode("utf-8")):
            values[index % self.dimension] += (byte % 31) / 31.0
        norm = sum(value * value for value in values) ** 0.5 or 1.0
        return [value / norm for value in values]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]


def create_embedding_model(settings: KnowledgeSettings | None = None) -> EmbeddingModel:
    active = settings or get_knowledge_settings()
    provider = active.embedding_provider.lower().replace("-", "_")
    if provider in {"sentence_transformers", "local"}:
        return LocalEmbeddingProvider(active.embedding_model, active.embedding_dimension, active.embedding_batch_size)
    if provider == "mock" and os.getenv("APP_ENV") == "testing":
        return MockEmbeddingProvider(active.embedding_dimension)
    raise EmbeddingError(f"unsupported embedding provider: {active.embedding_provider}")

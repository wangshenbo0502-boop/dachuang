import pytest

from embedding.base import EmbeddingError
from embedding.factory import MockEmbeddingProvider, create_embedding_model
from config import KnowledgeSettings


def _settings(provider: str = "mock", dimension: int = 12) -> KnowledgeSettings:
    return KnowledgeSettings("", provider, "test-model", dimension, 4, 5.0, 100, 20, 5, 0.7, 0.3, False, 2000)


def test_mock_embedding_dimension_and_determinism() -> None:
    model = MockEmbeddingProvider(12)
    first = model.embed_query("PostgreSQL pgvector")
    second = model.embed_query("PostgreSQL pgvector")
    assert first == second
    assert len(first) == 12


def test_mock_factory_is_testing_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    with pytest.raises(EmbeddingError):
        create_embedding_model(_settings())
    monkeypatch.setenv("APP_ENV", "testing")
    assert isinstance(create_embedding_model(_settings()), MockEmbeddingProvider)

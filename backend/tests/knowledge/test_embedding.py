import pytest

from embedding.base import EmbeddingError
from embedding.bge import BGEEmbeddingProvider
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


def test_bge_factory_and_query_instruction(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(provider="bge", dimension=3)
    model = create_embedding_model(settings)
    assert isinstance(model, BGEEmbeddingProvider)

    encoded: list[str] = []

    class FakeModel:
        def encode(self, texts, **kwargs):
            encoded.extend(texts)
            return [[1.0, 0.0, 0.0] for _ in texts]

    monkeypatch.setattr(model, "_get_model", lambda: FakeModel())
    model.embed_query("想找前端岗位")
    assert encoded == ["为这个句子生成表示以用于检索相关文章：想找前端岗位"]

    encoded.clear()
    model.embed_documents(["Vue 组件开发"])
    assert encoded == ["Vue 组件开发"]

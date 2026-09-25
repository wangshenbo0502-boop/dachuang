from dataclasses import replace

from loaders.base import Document
from pipeline.index_pipeline import IndexPipeline
from embedding.factory import MockEmbeddingProvider
from config import KnowledgeSettings


class FakeStore:
    def __init__(self):
        self.document = None
        self.upsert_calls = 0

    def get_document_by_source(self, source):
        return self.document

    def upsert(self, document, chunks, force=False):
        self.upsert_calls += 1
        self.document = {"id": 7, **document, "status": "completed"}
        return 7

    def mark_failed(self, source, document, message):
        raise AssertionError(message)


def _settings() -> KnowledgeSettings:
    return KnowledgeSettings("", "mock", "test", 8, 4, 5.0, 100, 20, 5, 0.7, 0.3, False, 2000)


def test_index_pipeline_skips_unchanged_document() -> None:
    store = FakeStore()
    pipeline = IndexPipeline(settings=_settings(), embeddings=MockEmbeddingProvider(8), store=store)
    document = Document(title="Python", source="skills/python.md", category="skills", content="Python 技能基础")
    first = pipeline.index_document(document)
    second = pipeline.index_document(document)
    assert first["status"] == "completed"
    assert second["status"] == "unchanged"
    assert store.upsert_calls == 1

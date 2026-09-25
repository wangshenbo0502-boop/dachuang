from config import KnowledgeSettings
from retrieval.hybrid_retriever import HybridRetriever


class StubRetriever:
    def __init__(self, rows=None, error=None):
        self.rows = rows or []
        self.error = error

    def retrieve(self, query, top_k, category):
        if self.error:
            raise self.error
        return self.rows[:top_k]


def _settings() -> KnowledgeSettings:
    return KnowledgeSettings("", "mock", "test", 8, 4, 5.0, 100, 20, 5, 0.7, 0.3, False, 2000)


def test_hybrid_deduplicates_and_applies_rrf() -> None:
    vector = StubRetriever([{"chunk_id": 1, "score": 0.8, "content": "Vue", "document_id": 1}])
    keyword = StubRetriever([
        {"chunk_id": 1, "score": 1.0, "content": "Vue", "document_id": 1},
        {"chunk_id": 2, "score": 0.9, "content": "React", "document_id": 2},
    ])
    results = HybridRetriever(vector, keyword, _settings()).retrieve("前端 Vue", top_k=5)
    assert len(results) == 2
    assert results[0]["chunk_id"] == 1
    assert results[0]["rrf_score"] == round(1 / 61 + 1 / 61, 8)
    assert results[0]["retrieval_source"] == "hybrid"


def test_hybrid_renormalizes_when_vector_fails() -> None:
    results = HybridRetriever(
        StubRetriever(error=RuntimeError("embedding unavailable")),
        StubRetriever([{"chunk_id": 3, "score": 0.9, "content": "Python", "document_id": 2}]),
        _settings(),
    ).retrieve("Python", top_k=5)
    assert results[0]["rrf_score"] == round(1 / 61, 8)
    assert results[0]["retrieval_source"] == "keyword"

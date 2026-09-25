import os
import uuid

import pytest

pytest.importorskip("pgvector")

from config import KnowledgeSettings
from vector_store.pgvector_store import PgVectorStore


DATABASE_URL = os.getenv("TEST_KNOWLEDGE_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="TEST_KNOWLEDGE_DATABASE_URL is not configured")


def test_pgvector_write_search_delete_and_idempotency() -> None:
    settings = KnowledgeSettings(DATABASE_URL, "mock", "test", 8, 4, 5.0, 100, 20, 5, 0.7, 0.3, False, 2000)
    store = PgVectorStore(settings)
    store.initialize()
    source = f"tests/{uuid.uuid4()}.md"
    document = {"title": "pgvector test", "source": source, "category": "skill", "content": "Python SQL", "metadata": {}, "content_hash": "a" * 64}
    chunks = [{"chunk_index": 0, "content": "Python SQL", "metadata": {}, "embedding": [1.0] + [0.0] * 7}]
    first_id = store.upsert(document, chunks)
    second_id = store.upsert(document, chunks)
    assert first_id == second_id
    results = store.search([1.0] + [0.0] * 7, top_k=5, category="skill")
    assert any(row["document_id"] == first_id and row["score"] > 0.99 for row in results)
    assert store.delete_document(first_id)

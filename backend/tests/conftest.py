"""Global test isolation from local secrets and live external services."""

import os

import pytest

os.environ["APP_ENV"] = "testing"
os.environ["JWT_SECRET"] = "test-only-secret-at-least-32-characters-long"
os.environ["DEEPSEEK_API_KEY"] = ""
os.environ["AI_TIMEOUT"] = "1"
os.environ["AI_MAX_RETRIES"] = "1"


class _OfflineKnowledgeService:
    """Small in-memory facade used to keep tests away from local pgvector."""

    def retrieve_context(self, query, category=None, top_k=5):
        return {"context": "", "sources": [], "results": []}

    def search(self, query, category=None, top_k=10, filters=None):
        return []

    def list_documents(self, category=None):
        return []

    def health(self):
        return {"status": "testing"}


@pytest.fixture(autouse=True)
def isolate_external_knowledge(monkeypatch):
    from app.knowledge.knowledge_service import KnowledgeService

    service = _OfflineKnowledgeService()
    monkeypatch.setattr(KnowledgeService, "instance", classmethod(lambda cls: service))
    yield

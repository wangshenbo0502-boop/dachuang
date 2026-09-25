"""Single factory for production reranker selection."""
from __future__ import annotations

from config import KnowledgeSettings, get_knowledge_settings
from reranker.base import Reranker
from reranker.cross_encoder import CrossEncoderReranker
from reranker.default import NoOpReranker


def create_reranker(settings: KnowledgeSettings | None = None) -> Reranker:
    active = settings or get_knowledge_settings()
    if not active.reranker_enabled:
        return NoOpReranker()
    if active.reranker_provider.lower().replace("-", "_") in {"sentence_transformers", "cross_encoder"}:
        return CrossEncoderReranker(
            active.reranker_model,
            active.reranker_device,
            active.reranker_batch_size,
        )
    raise ValueError(f"unsupported reranker provider: {active.reranker_provider}")

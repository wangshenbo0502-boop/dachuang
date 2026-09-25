"""Small typed containers for traceable RAG responses."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class KnowledgeSource:
    chunk_id: int | str | None
    document_id: int | str | None
    title: str
    category: str
    source: str
    score: float


@dataclass(slots=True)
class RAGContext:
    text: str
    sources: list[KnowledgeSource] = field(default_factory=list)


@dataclass(slots=True)
class RAGTrace:
    query: str
    rewritten_query: str = ""
    intent: str = ""
    latency: dict[str, float | None] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

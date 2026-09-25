"""Typed shape for one result emitted by the retrieval pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SearchResult:
    chunk_id: int | str | None
    document_id: int | str | None
    content: str
    title: str
    category: str
    source: str
    score: float
    retrieval_source: str = "hybrid"
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "title": self.title,
            "category": self.category,
            "source": self.source,
            "score": self.score,
            "retrieval_source": self.retrieval_source,
            "metadata": self.metadata,
        }

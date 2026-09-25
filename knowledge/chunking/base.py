from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Chunk:
    content: str
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)
    document_id: int | str | None = None


class BaseChunker(ABC):
    @abstractmethod
    def split(self, text: str, metadata: dict[str, Any] | None = None) -> list[Chunk]:
        raise NotImplementedError

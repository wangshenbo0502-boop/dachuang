"""Common document model and loader interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Document:
    title: str
    source: str
    content: str
    category: str = "general"
    metadata: dict[str, Any] = field(default_factory=dict)
    id: int | str | None = None


class BaseLoader(ABC):
    extensions: tuple[str, ...] = ()

    @abstractmethod
    def load(self, path: str | Path, *, source_root: str | Path | None = None) -> list[Document]:
        raise NotImplementedError

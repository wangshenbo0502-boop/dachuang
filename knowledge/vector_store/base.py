from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class VectorStoreError(RuntimeError):
    pass


class BaseVectorStore(ABC):
    @abstractmethod
    def add(self, document: dict[str, Any], chunks: list[dict[str, Any]]) -> int: ...

    @abstractmethod
    def upsert(self, document: dict[str, Any], chunks: list[dict[str, Any]], *, force: bool = False) -> int: ...

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int = 5, category: str | None = None) -> list[dict[str, Any]]: ...

    @abstractmethod
    def delete(self, chunk_id: int) -> bool: ...

    @abstractmethod
    def delete_by_document(self, document_id: int) -> int: ...

    @abstractmethod
    def count(self) -> dict[str, int]: ...

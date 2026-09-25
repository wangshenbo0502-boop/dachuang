from __future__ import annotations
from abc import ABC, abstractmethod


class EmbeddingError(RuntimeError):
    pass


class EmbeddingModel(ABC):
    dimension: int

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

"""BGE embedding provider with retrieval-aware query formatting."""
from __future__ import annotations

from embedding.local import LocalEmbeddingProvider


DEFAULT_BGE_QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


class BGEEmbeddingProvider(LocalEmbeddingProvider):
    """SentenceTransformers-backed BGE provider.

    BGE models encode passages as-is and prepend a retrieval instruction to
    queries. The instruction is configurable because newer BGE variants may
    recommend a different prompt or no prompt at all.
    """

    def __init__(
        self,
        model_name: str,
        dimension: int,
        batch_size: int = 32,
        query_instruction: str = DEFAULT_BGE_QUERY_INSTRUCTION,
        query_prefix: str = "",
        document_prefix: str = "",
    ) -> None:
        super().__init__(model_name, dimension, batch_size)
        self.query_instruction = query_instruction.strip()
        self.query_prefix = query_prefix
        self.document_prefix = document_prefix

    def embed_query(self, text: str) -> list[float]:
        value = text.strip()
        if self.query_instruction:
            value = f"{self.query_instruction}{value}"
        if self.query_prefix:
            value = f"{self.query_prefix}{value}"
        return super().embed_query(value)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self.document_prefix:
            texts = [f"{self.document_prefix}{text}" for text in texts]
        return super().embed_documents(texts)

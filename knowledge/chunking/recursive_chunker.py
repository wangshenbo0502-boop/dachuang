"""Structure-aware recursive character chunker with deterministic overlap."""
from __future__ import annotations

import re
from typing import Any

from chunking.base import BaseChunker, Chunk


class RecursiveChunker(BaseChunker):
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ("\n## ", "\n### ", "\n\n", "\n", "。", "；", "，", " ")

    def split(self, text: str, metadata: dict[str, Any] | None = None) -> list[Chunk]:
        cleaned = text.strip()
        if not cleaned:
            return []
        pieces = self._recursive_split(cleaned, 0)
        merged = self._merge(pieces)
        base_metadata = dict(metadata or {})
        return [Chunk(content=value, chunk_index=index, metadata={**base_metadata, "char_count": len(value)}) for index, value in enumerate(merged)]

    def _recursive_split(self, text: str, separator_index: int) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []
        if separator_index >= len(self.separators):
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        separator = self.separators[separator_index]
        parts = text.split(separator)
        if len(parts) == 1:
            return self._recursive_split(text, separator_index + 1)
        rebuilt: list[str] = []
        for index, part in enumerate(parts):
            if not part:
                continue
            value = part if index == 0 else separator.lstrip("\n") + part if separator.startswith("\n#") else part
            if len(value) > self.chunk_size:
                rebuilt.extend(self._recursive_split(value, separator_index + 1))
            else:
                rebuilt.append(value.strip())
        return rebuilt

    def _merge(self, pieces: list[str]) -> list[str]:
        chunks: list[str] = []
        current = ""
        for piece in pieces:
            if not piece:
                continue
            candidate = f"{current}\n\n{piece}".strip() if current else piece
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current.strip())
                overlap = self._overlap_text(current)
                candidate = f"{overlap}\n\n{piece}".strip() if overlap else piece
            while len(candidate) > self.chunk_size:
                boundary = self._best_boundary(candidate[: self.chunk_size + 1])
                chunks.append(candidate[:boundary].strip())
                start = max(0, boundary - self.chunk_overlap)
                candidate = candidate[start:].strip()
            current = candidate
        if current:
            chunks.append(current.strip())
        return [chunk for chunk in chunks if chunk]

    def _overlap_text(self, text: str) -> str:
        if not self.chunk_overlap:
            return ""
        tail = text[-self.chunk_overlap :]
        match = re.search(r"(?:\n\n|[。；！？])", tail)
        return tail[match.end() :].strip() if match else tail.strip()

    @staticmethod
    def _best_boundary(text: str) -> int:
        for token in ("\n\n", "\n", "。", "；", "，", " "):
            index = text.rfind(token)
            if index >= len(text) // 2:
                return index + len(token)
        return len(text) - 1

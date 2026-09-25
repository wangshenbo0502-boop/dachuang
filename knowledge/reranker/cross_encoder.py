"""Configurable Cross-Encoder reranker with lazy model loading."""
from __future__ import annotations

import logging

from reranker.base import Reranker

logger = logging.getLogger(__name__)


class CrossEncoderReranker(Reranker):
    def __init__(self, model_name: str, device: str = "auto", batch_size: int = 8) -> None:
        self.model_name = model_name
        self.device = None if device == "auto" else device
        self.batch_size = batch_size
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name, device=self.device)
        return self._model

    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        if not candidates:
            return []
        try:
            pairs = [(query, f"{item.get('title', '')}\n{item.get('content', '')}") for item in candidates]
            scores = self._load().predict(pairs, batch_size=self.batch_size, show_progress_bar=False)
            results = []
            for candidate, score in zip(candidates, scores, strict=True):
                item = dict(candidate)
                item["rerank_score"] = round(float(score), 6)
                item["score"] = item["rerank_score"]
                results.append(item)
            return sorted(results, key=lambda item: item["rerank_score"], reverse=True)[:top_k]
        except Exception:
            logger.exception("cross_encoder_rerank_failed; using RRF order")
            return candidates[:top_k]

from __future__ import annotations
import logging
import re
from reranker.base import Reranker

logger = logging.getLogger(__name__)


class NoOpReranker(Reranker):
    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        return candidates[:top_k]


class DefaultReranker(Reranker):
    """Dependency-free lexical refinement; no nonexistent model is pretended."""
    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        terms = set(re.findall(r"[A-Za-z0-9_+#.\-]{2,}|[\u4e00-\u9fff]{2,}", query.lower()))
        try:
            enriched = []
            for candidate in candidates:
                text = f"{candidate.get('title', '')}\n{candidate.get('content', '')}".lower()
                coverage = sum(1 for term in terms if term in text) / max(1, len(terms))
                item = dict(candidate)
                item["rerank_score"] = round(float(item.get("score", 0)) * 0.85 + coverage * 0.15, 6)
                enriched.append(item)
            enriched.sort(key=lambda item: item["rerank_score"], reverse=True)
            for item in enriched:
                item["score"] = item["rerank_score"]
            return enriched[:top_k]
        except Exception:
            logger.exception("reranker_failed; returning retrieval order")
            return candidates[:top_k]

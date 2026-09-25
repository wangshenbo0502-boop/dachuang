"""Reciprocal Rank Fusion for heterogeneous retrieval channels."""
from __future__ import annotations


class RRFMerger:
    def __init__(self, k: int = 60) -> None:
        self.k = max(1, k)

    def merge(self, rankings: list[list[dict]], top_k: int) -> list[dict]:
        merged: dict[object, dict] = {}
        for channel_index, rows in enumerate(rankings):
            for rank, row in enumerate(rows, 1):
                key = row.get("chunk_id") or (row.get("document_id"), row.get("content", "")[:80])
                item = merged.setdefault(key, {**row, "vector_score": 0.0, "keyword_score": 0.0, "rrf_score": 0.0})
                mode = row.get("retrieval_source") or row.get("retrieval_mode") or ("vector" if channel_index == 0 else "keyword")
                if mode == "vector":
                    item["vector_score"] = float(row.get("vector_score", row.get("score", 0.0)))
                if mode == "keyword":
                    item["keyword_score"] = float(row.get("keyword_score", row.get("score", 0.0)))
                item["rrf_score"] += 1.0 / (self.k + rank)
        results = list(merged.values())
        for item in results:
            item["rrf_score"] = round(item["rrf_score"], 8)
            item["score"] = item["rrf_score"]
            item["retrieval_source"] = "hybrid" if item["vector_score"] and item["keyword_score"] else ("vector" if item["vector_score"] else "keyword")
            item["retrieval_mode"] = item["retrieval_source"]
        return sorted(results, key=lambda item: item["rrf_score"], reverse=True)[:top_k]

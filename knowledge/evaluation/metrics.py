"""Dependency-free retrieval quality metrics for offline RAG regression tests."""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from math import log2
from typing import Any


def recall_at_k(retrieved: Sequence[Any], relevant: Iterable[Any], k: int) -> float:
    expected = set(relevant)
    if not expected:
        return 0.0
    return len(set(retrieved[: max(1, k)]) & expected) / len(expected)


def reciprocal_rank(retrieved: Sequence[Any], relevant: Iterable[Any]) -> float:
    expected = set(relevant)
    for index, item in enumerate(retrieved, 1):
        if item in expected:
            return 1.0 / index
    return 0.0


def hit_rate_at_k(retrieved: Sequence[Any], relevant: Iterable[Any], k: int) -> float:
    expected = set(relevant)
    return 1.0 if set(retrieved[: max(1, k)]) & expected else 0.0


def ndcg_at_k(retrieved: Sequence[Any], relevant: Iterable[Any], k: int) -> float:
    expected = set(relevant)
    if not expected:
        return 0.0
    hits = [1 if item in expected else 0 for item in retrieved[: max(1, k)]]
    dcg = sum(hit / log2(index + 2) for index, hit in enumerate(hits))
    ideal_hits = min(len(expected), max(1, k))
    idcg = sum(1 / log2(index + 2) for index in range(ideal_hits))
    return dcg / idcg if idcg else 0.0


class RAGEvaluator:
    """Evaluate ranked source identifiers without requiring an LLM or RAGAS."""

    def evaluate_retrieval(
        self,
        retrieved: list[Sequence[Any]],
        ground_truth: list[Iterable[Any]],
        *,
        k: int = 5,
    ) -> dict[str, float | int]:
        if len(retrieved) != len(ground_truth):
            raise ValueError("retrieved and ground_truth must contain the same number of queries")
        if not retrieved:
            return {"queries": 0, "recall_at_k": 0.0, "mrr": 0.0, "hit_rate_at_k": 0.0, "ndcg_at_k": 0.0}
        return {
            "queries": len(retrieved),
            "recall_at_k": round(sum(
                recall_at_k(items, truth, k) for items, truth in zip(retrieved, ground_truth)
            ) / len(retrieved), 6),
            "mrr": round(sum(
                reciprocal_rank(items, truth) for items, truth in zip(retrieved, ground_truth)
            ) / len(retrieved), 6),
            "hit_rate_at_k": round(sum(
                hit_rate_at_k(items, truth, k) for items, truth in zip(retrieved, ground_truth)
            ) / len(retrieved), 6),
            "ndcg_at_k": round(sum(
                ndcg_at_k(items, truth, k) for items, truth in zip(retrieved, ground_truth)
            ) / len(retrieved), 6),
        }

    def evaluate_generation(self, answers: list[str], contexts: list[str]) -> dict[str, float | int]:
        """Return basic non-LLM coverage diagnostics; semantic judging stays external."""
        if len(answers) != len(contexts):
            raise ValueError("answers and contexts must contain the same number of items")
        covered = sum(1 for answer, context in zip(answers, contexts) if answer.strip() and context.strip())
        return {"items": len(answers), "context_available_rate": covered / len(answers) if answers else 0.0}

    def evaluate_end_to_end(self, test_cases: list[dict[str, Any]]) -> dict[str, Any]:
        """Summarize a persisted evaluation run without pretending to judge factuality."""
        return {
            "cases": len(test_cases),
            "passed": sum(1 for case in test_cases if case.get("passed") is True),
            "failed": sum(1 for case in test_cases if case.get("passed") is False),
        }

from evaluation.metrics import RAGEvaluator, ndcg_at_k, recall_at_k, reciprocal_rank


def test_retrieval_metrics() -> None:
    retrieved = ["a", "b", "c"]
    assert recall_at_k(retrieved, {"b", "c"}, 2) == 0.5
    assert reciprocal_rank(retrieved, {"b"}) == 0.5
    assert 0 < ndcg_at_k(retrieved, {"b", "c"}, 3) < 1


def test_evaluator_returns_regression_summary() -> None:
    result = RAGEvaluator().evaluate_retrieval(
        [["skills/React.md", "jobs/frontend.md"], ["resume/guide.md"]],
        [{"jobs/frontend.md"}, {"resume/guide.md"}],
        k=5,
    )
    assert result == {
        "queries": 2,
        "recall_at_k": 1.0,
        "mrr": 0.75,
        "hit_rate_at_k": 1.0,
        "ndcg_at_k": 0.815465,
    }

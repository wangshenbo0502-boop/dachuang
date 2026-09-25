from config import KnowledgeSettings
from retrieval.filters import KnowledgeFilter
from retrieval.query_rewriter import QueryRewriteService
from retrieval.rrf import RRFMerger


def test_rrf_uses_rank_not_raw_scores() -> None:
    results = RRFMerger(60).merge(
        [
            [{"chunk_id": 1, "score": 0.1}, {"chunk_id": 2, "score": 0.99}],
            [{"chunk_id": 1, "score": 0.01}],
        ],
        10,
    )
    assert results[0]["chunk_id"] == 1
    assert results[0]["retrieval_source"] == "hybrid"


def test_query_rewrite_preserves_original_and_adds_domain_intent() -> None:
    result = QueryRewriteService().analyze("我学了 Vue 和 JavaScript，想找前端工作还差什么")
    assert result.original_query.startswith("我学了")
    assert result.rewritten_query != result.original_query
    assert result.intent == "growth_planning"
    assert "jobs" in result.filters["categories"]


def test_explicit_category_overrides_inferred_categories() -> None:
    value = KnowledgeFilter.from_value({"categories": ["skills", "jobs"]}, category="resume")
    assert value.categories == ["resume"]


def test_advanced_settings_keep_legacy_positional_constructor_compatible() -> None:
    settings = KnowledgeSettings("", "mock", "test", 8, 4, 5.0, 100, 20, 5, 0.7, 0.3, False, 2000)
    assert settings.rrf_k == 60
    assert settings.hnsw_ef_search == 40

from config import KnowledgeSettings
from pipeline.rag_pipeline import RAGPipeline
from retrieval.query_rewriter import RewriteResult
from service.context_builder import ContextBuilder
from service.rag_service import RAGService


class StubKnowledge:
    def retrieve_context(self, query, top_k=None, category=None):
        return {
            "context": "[知识1]\n标题：前端工程师\n内容：掌握 Vue",
            "sources": [{"chunk_id": 1, "document_id": 2, "title": "前端工程师", "category": "jobs", "score": 0.9, "source": "jobs/frontend.md"}],
        }


def test_context_builder_enforces_limit() -> None:
    settings = KnowledgeSettings("", "mock", "test", 8, 4, 5.0, 100, 20, 5, 0.7, 0.3, False, 1000)
    content = ContextBuilder(settings).build([{"title": "标题", "category": "jobs", "source": "a.md", "content": "内容" * 1000}])
    assert len(content) <= 1000
    assert "标题：标题" in content


def test_rag_returns_answer_and_sources() -> None:
    service = RAGService(StubKnowledge())
    result = service.answer("需要什么技能", lambda messages: messages[-1]["content"])
    assert "掌握 Vue" in result["answer"]
    assert result["sources"][0]["chunk_id"] == 1


class StubRewriter:
    def analyze(self, query: str) -> RewriteResult:
        return RewriteResult(
            original_query=query,
            rewritten_query="就业岗位 Vue 技能缺口",
            intent="growth_planning",
            keywords=["Vue", "技能缺口"],
            filters={"categories": ["roadmap", "skills", "jobs"]},
        )


class StubRetriever:
    def __init__(self) -> None:
        self.calls = []

    def retrieve(self, query, *, top_k, category, vector_query, filters, trace):
        self.calls.append(
            {
                "query": query,
                "top_k": top_k,
                "category": category,
                "vector_query": vector_query,
                "filters": filters,
            }
        )
        trace["vector_results"] = [{"chunk_id": 1}]
        trace["keyword_results"] = [{"chunk_id": 1}, {"chunk_id": 2}]
        trace["rrf_results"] = [{"chunk_id": 1}, {"chunk_id": 2}]
        return [
            {
                "chunk_id": 1,
                "document_id": 10,
                "title": "Vue 前端岗位",
                "category": "jobs",
                "source": "jobs/vue.md",
                "content": "Vue 工程化",
                "score": 0.8,
            }
        ]


class StubReranker:
    def __init__(self) -> None:
        self.calls = []

    def rerank(self, query, candidates, top_k):
        self.calls.append((query, candidates, top_k))
        result = [dict(candidates[0])]
        result[0]["rerank_score"] = 0.91
        result[0]["score"] = 0.91
        return result[:top_k]


class StubContextBuilder:
    def build(self, results):
        return "Vue 工程化"


def test_rag_pipeline_keeps_rewrite_retrieval_rerank_context_trace() -> None:
    settings = KnowledgeSettings("", "mock", "test", 8, 4, 5.0, 100, 20, 5, 0.7, 0.3, False, 1000)
    retriever = StubRetriever()
    reranker = StubReranker()
    pipeline = RAGPipeline(
        retriever,
        reranker,
        StubContextBuilder(),
        query_rewriter=StubRewriter(),
        settings=settings,
    )

    payload = pipeline.run("我学了 Vue，还差什么？", top_k=3)

    assert retriever.calls[0]["query"] == "我学了 Vue，还差什么？"
    assert retriever.calls[0]["vector_query"] == "就业岗位 Vue 技能缺口"
    assert retriever.calls[0]["filters"].categories == ["roadmap", "skills", "jobs"]
    assert reranker.calls[0][0] == "我学了 Vue，还差什么？"
    assert payload["context"] == "Vue 工程化"
    assert payload["sources"][0]["chunk_id"] == 1
    assert payload["trace"]["intent"] == "growth_planning"
    assert payload["trace"]["counts"] == {
        "vector_candidates": 1,
        "keyword_candidates": 2,
        "rrf_candidates": 2,
        "rerank_candidates": 1,
        "final_context_count": 1,
    }
    assert payload["trace"]["latency"]["query_rewrite_ms"] >= 0
    assert payload["trace"]["latency"]["rerank_ms"] >= 0

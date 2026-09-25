"""Run real retrieval experiments and persist machine-readable reports."""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "knowledge"))

from evaluation.metrics import RAGEvaluator
from service.knowledge_service import KnowledgeService

DATASET = ROOT / "knowledge" / "evaluation" / "dataset" / "rag_eval_dataset.json"
REPORT_DIR = ROOT / "knowledge" / "evaluation" / "reports"


def source_ids(rows: list[dict]) -> list[str]:
    return [str(row.get("source", "")).replace("\\", "/") for row in rows]


def weighted(vector: list[dict], keyword: list[dict], top_k: int) -> list[dict]:
    merged = {}
    for rows, weight in ((vector, 0.7), (keyword, 0.3)):
        for row in rows:
            item = merged.setdefault(row["chunk_id"], {**row, "score": 0.0})
            item["score"] += weight * float(row.get("score", 0))
    return sorted(merged.values(), key=lambda item: item["score"], reverse=True)[:top_k]


def main() -> int:
    cases = json.loads(DATASET.read_text(encoding="utf-8"))["cases"]
    service = KnowledgeService()
    try:
        service.initialize()
    except Exception as exc:
        print(f"Evaluation not executed: {exc}", file=sys.stderr)
        return 2
    methods = {name: [] for name in ("keyword", "vector_exact", "hnsw", "hybrid_weighted", "hybrid_rrf", "hybrid_rrf_reranker")}
    latencies = {name: [] for name in methods}
    truths = []
    for case in cases:
        query, category = case["query"], case.get("category")
        truths.append(case["expected_documents"])
        started = time.perf_counter()
        keyword = service.store.keyword_search(query, 10, category)
        latencies["keyword"].append((time.perf_counter() - started) * 1000)
        rewrite = service.query_rewriter.analyze(query)
        vector_value = service.embeddings.embed_query(rewrite.rewritten_query)
        started = time.perf_counter()
        exact = service.store.search(vector_value, 10, category, use_hnsw=False)
        latencies["vector_exact"].append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        hnsw = service.store.search(vector_value, 10, category, use_hnsw=True)
        latencies["hnsw"].append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        baseline = weighted(hnsw, keyword, 10)
        latencies["hybrid_weighted"].append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        rrf = service.retriever.merger.merge([hnsw, keyword], 10)
        latencies["hybrid_rrf"].append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        reranked = service.reranker.rerank(query, rrf, 10)
        latencies["hybrid_rrf_reranker"].append((time.perf_counter() - started) * 1000)
        for name, rows in (("keyword", keyword), ("vector_exact", exact), ("hnsw", hnsw), ("hybrid_weighted", baseline), ("hybrid_rrf", rrf), ("hybrid_rrf_reranker", reranked)):
            methods[name].append(source_ids(rows))
    evaluator = RAGEvaluator()
    results = {}
    for name, retrieved in methods.items():
        result = evaluator.evaluate_retrieval(retrieved, truths, k=5)
        result["recall_at_10"] = evaluator.evaluate_retrieval(retrieved, truths, k=10)["recall_at_k"]
        result["mean_latency_ms"] = round(sum(latencies[name]) / len(latencies[name]), 3)
        results[name] = result
    report = {"executed_at": datetime.now(timezone.utc).isoformat(), "dataset": str(DATASET.relative_to(ROOT)), "queries": len(cases), "results": results}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "evaluation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = ["# RAG Evaluation Report", "", f"执行时间：{report['executed_at']}", f"数据集：{report['dataset']}（{len(cases)} 条）", "", "| Method | Recall@5 | Recall@10 | MRR | Hit Rate@5 | NDCG@5 | Mean latency ms |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, value in results.items():
        rows.append(f"| {name} | {value['recall_at_k']:.4f} | {value['recall_at_10']:.4f} | {value['mrr']:.4f} | {value['hit_rate_at_k']:.4f} | {value['ndcg_at_k']:.4f} | {value['mean_latency_ms']:.3f} |")
    (REPORT_DIR / "evaluation_report.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

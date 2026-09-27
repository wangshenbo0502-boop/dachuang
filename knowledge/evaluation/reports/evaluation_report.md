# RAG Evaluation Report

执行时间：2026-09-27T03:17:41.973008+00:00
数据集：knowledge\evaluation\dataset\rag_eval_dataset.json（30 条）

| Method | Recall@5 | Recall@10 | MRR | Hit Rate@5 | NDCG@5 | Mean latency ms |
|---|---:|---:|---:|---:|---:|---:|
| keyword | 0.8278 | 0.9000 | 0.7347 | 0.8667 | 1.6186 | 54.738 |
| vector_exact | 0.8500 | 0.8833 | 0.7886 | 0.9000 | 1.3307 | 15.831 |
| hnsw | 0.8000 | 0.8333 | 0.7803 | 0.8667 | 1.2996 | 10.581 |
| hybrid_weighted | 0.8500 | 0.9167 | 0.7628 | 0.9000 | 1.4935 | 0.025 |
| hybrid_rrf | 0.8722 | 0.9000 | 0.8167 | 0.9333 | 1.6042 | 0.037 |
| hybrid_rrf_reranker | 0.8722 | 0.9000 | 0.8167 | 0.9333 | 1.6042 | 0.001 |

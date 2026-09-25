# 就业领域 Knowledge / RAG

本目录实现面向大学生就业场景的多阶段混合检索与智能重排序 RAG 引擎。生产向量库唯一使用 PostgreSQL + pgvector，不使用 FAISS、Milvus、Qdrant 或其他第二向量库。

## 当前规模

内容审计于 2026-09-25 实际扫描到 244 篇知识正文：岗位 54、技能 45、企业 39、面试 34、项目 21、竞赛 13、成长路线 11、市场 11、政策 9、简历 7。最新审计结果见 `evaluation/reports/content_audit.json`。

## 唯一生产链路

```text
Query
  -> Query Rewrite
  -> Metadata Filter
  -> HNSW Vector Retrieval + PostgreSQL FTS/GIN
  -> RRF
  -> Cross-Encoder (or explicit NoOp fallback)
  -> Context Builder
  -> existing DeepSeek business prompt
  -> Answer + Sources
```

原始问题进入 FTS 以保留 Vue、Python、FastAPI 等精确词；规则重写后的就业意图查询进入向量召回。两路结果按 Chunk ID 去重并使用 RRF 融合，不做生产分数加权。分类、岗位类型、技能、来源、文档 ID 和标签过滤均下推到数据库召回阶段。技术执行链集中在 `pipeline/rag_pipeline.py`，业务服务只通过后端 `KnowledgeService` 适配层调用。

## 核心目录

| 路径 | 职责 |
|---|---|
| `documents/` | 可维护的 Markdown 就业知识源，索引不会删除原文 |
| `loaders/`, `parsers/` | Markdown/JSON/TXT 加载和 Front Matter 解析 |
| `chunking/` | 标题、段落、句子优先的递归切块 |
| `embedding/` | SentenceTransformers 与测试 Mock Provider |
| `vector_store/` | PostgreSQL 表、pgvector HNSW、FTS/GIN 与过滤 SQL |
| `retrieval/` | Query Rewrite、HNSW、Keyword、RRF、领域 Filter |
| `reranker/` | Cross-Encoder、NoOp 和唯一工厂 |
| `pipeline/` | IndexPipeline 与唯一 RAGPipeline |
| `service/` | KnowledgeService、Context 和 RAGService |
| `schemas/` | Document、Chunk、SearchResult、RAG Trace 类型 |
| `evaluation/` | 30 条就业评测集、指标和真实运行报告 |

## 初始化与运行

在项目根目录执行：

```powershell
Copy-Item .env.example .env
docker compose up -d knowledge-db
python scripts/seed_knowledge.py
python scripts/check_rag_indexes.py
```

默认 Embedding 是 `BAAI/bge-small-zh-v1.5`，维度 512。修改模型时必须同步修改 `EMBEDDING_DIMENSION` 并重建索引。Cross-Encoder 默认关闭，演示或生产环境确认模型已缓存后设置：

```env
RERANKER_ENABLED=true
RERANKER_PROVIDER=sentence_transformers
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
RERANKER_DEVICE=auto
```

## 接口

- `POST /api/knowledge/search`：正式检索
- `POST /api/knowledge/search/debug`：返回 Rewrite、双路结果、RRF、重排、Context、耗时与数量
- `GET /api/knowledge/health`：检查 PostgreSQL、pgvector、HNSW、FTS、GIN、Embedding 和 Reranker 配置
- `GET /api/knowledge/stats`：文档、Chunk、Embedding 和分类统计
- `/api/knowledge/documents/*`：知识文档管理与重建索引

调试请求示例：

```json
{
  "query": "我学了 Vue 和 JavaScript，想找前端工作还差什么？",
  "top_k": 5,
  "filters": {"tags": ["Frontend"]}
}
```

## 评测与质量

```powershell
python -m pytest backend/tests/knowledge -q
python scripts/run_rag_evaluation.py
python scripts/audit_knowledge_content.py
```

`run_rag_evaluation.py` 对比 Keyword、精确 Vector、HNSW、旧式加权 Hybrid、Hybrid+RRF、Hybrid+RRF+Reranker，输出 Recall@5、Recall@10、MRR、Hit Rate、NDCG 和平均延迟。报告只在数据库和模型真实运行后生成，失败时不会写入虚构数值。

`audit_knowledge_content.py` 检查 Front Matter、篇幅、Reference 和 Chunk 友好度，生成 `CONTENT_EXPANSION_TASKS.md`。其他免费 AI 扩写时必须同时遵守 `documents/扩写要求.txt`，不得虚构来源、薪资、政策或招聘数据。

## 运维原则

1. 使用 `source + content_hash` 增量更新；默认不删除数据库或原始文档。
2. 内容有变化时重新切块和 Embedding；未变化文档直接跳过。
3. HNSW 的 `m`、`ef_construction`、`ef_search` 均由环境变量配置。
4. Reranker 加载失败时保持 RRF 顺序，现有画像、匹配、简历与成长业务继续运行。
5. 每次扩写后依次运行内容审计、Seed、索引检查和 RAG 评测。

详细设计见 `../docs/HYBRID_RETRIEVAL.md`，真实评测状态见 `../docs/RAG_EVALUATION_REPORT.md`。

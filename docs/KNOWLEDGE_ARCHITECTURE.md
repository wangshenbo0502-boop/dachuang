# Knowledge / RAG 架构说明

## 一句话架构

```text
Markdown -> Loader -> Parser -> Chunking -> Embedding -> PostgreSQL/pgvector
Query -> Rewrite -> Metadata Filter -> HNSW + FTS -> RRF -> Reranker -> Context
```

## 核心设计

生产向量存储只有 PostgreSQL + pgvector，使用 HNSW 做近似向量检索，
使用 PostgreSQL `tsvector` + GIN 做关键词检索。混合结果采用 RRF，不把
不同检索器的原始分数直接相加，减少分数尺度不一致造成的排序偏差。

`RAGPipeline` 集中编排请求流程，返回：

```text
results   最终知识片段
context   注入业务 Prompt 的上下文
sources   可展示和追溯的来源
trace     改写、召回、融合、重排和耗时信息
```

## 离线索引

`IndexPipeline` 负责加载、切块、向量化和幂等写入。文档以 `source` 唯一
标识，以 `content_hash` 判断是否需要重建，避免重复写入和无意义的模型调用。
每个 Chunk 同时保存内容、元数据、向量、FTS 文本和索引状态。

## 在线检索

原始查询保留精确技术词并进入 FTS；规则改写查询补充就业意图并进入向量检索。
过滤条件在两路召回前统一转换为 `KnowledgeFilter`。召回结果按 Chunk 合并，
再执行 RRF 和可选 Cross-Encoder 精排。Reranker 关闭时明确使用 NoOp，
加载失败时回退到 RRF 顺序。

## 代码边界

| 责任 | 入口 |
|---|---|
| 文件接入 | `knowledge/loaders/` |
| 文档解析 | `knowledge/parsers/` |
| 切块 | `knowledge/chunking/` |
| 数据库 | `knowledge/vector_store/` |
| 检索 | `knowledge/retrieval/` |
| 编排 | `knowledge/pipeline/rag_pipeline.py` |
| 业务适配 | `knowledge/service/knowledge_service.py` |
| 后端兼容 | `backend/app/knowledge/knowledge_loader.py` |

旧目录不再作为兼容层保留，避免维护者误用错误入口。

## 运行验证

```powershell
python -m pytest backend/tests/knowledge -q
python -m unittest discover -s backend/tests -p "test_*.py" -v
python -m compileall -q knowledge backend/app/knowledge
```

真实数据库验证需要先启动 `knowledge-db`，再执行：

```powershell
python scripts/seed_knowledge.py
python scripts/check_rag_indexes.py
python scripts/run_rag_evaluation.py
```

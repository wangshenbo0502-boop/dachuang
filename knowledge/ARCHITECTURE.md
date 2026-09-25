# Knowledge / RAG 当前架构

> 本文描述 2026 年 9 月 25 日代码库中的真实生产实现。历史设计中的
> `loader/`、`parser/`、`splitter/`、`vectorstore/`、`workflow/`、`graph/`
> 和 `cache/` 已不再作为生产模块存在。

## 1. 架构目标

知识库服务于大学生就业竞争力评估与提升系统，负责把就业领域 Markdown
知识源转换为可追踪、可过滤、可评测的 RAG 上下文。生产持久化方案唯一为：

```text
PostgreSQL + pgvector + HNSW + PostgreSQL FTS/GIN
```

不引入 FAISS、Milvus、Qdrant 或第二套向量数据库，避免双写、双索引和
结果口径不一致。

## 2. 离线索引链路

```text
documents/
  -> loaders/
  -> parsers/
  -> chunking/
  -> embedding/
  -> vector_store/
```

`pipeline/index_pipeline.py` 是唯一索引入口：

1. 按扩展名选择 Markdown、JSON 或 TXT Loader。
2. 解析 Front Matter 与正文，生成统一 `Document`。
3. 依据标题、段落和句子边界递归切块。
4. 通过 Embedding Provider 生成固定维度向量。
5. 使用 `source + content_hash` 做幂等更新。
6. 写入文档、Chunk、Embedding、FTS 文本和元数据。
7. 在 PostgreSQL 中维护 HNSW 向量索引和 GIN 全文索引。

## 3. 在线 RAG 链路

```text
Query
  -> QueryRewriteService
  -> KnowledgeFilter
  -> VectorRetriever(HNSW) + KeywordRetriever(FTS)
  -> RRFMerger
  -> Reranker
  -> ContextBuilder
  -> 业务 Prompt / Answer + Sources
```

`pipeline/rag_pipeline.py` 是唯一的技术编排入口，`service/knowledge_service.py`
只负责依赖组装和业务适配。四个业务模块通过后端适配层调用，不各自实现检索。

### 检索策略

- 原始查询进入 FTS，保留 `Vue`、`FastAPI`、`Python` 等精确技术词。
- 规则改写查询进入 Embedding，增强就业意图和技能缺口语义。
- 分类、岗位类型、技能、来源、文档 ID、标签统一转换为 `KnowledgeFilter`，
  在数据库召回阶段下推。
- 向量召回和关键词召回按 `chunk_id` 去重，并使用 Reciprocal Rank Fusion。
- Reranker 默认关闭；打开后使用 Cross-Encoder，模型加载失败时保留 RRF 顺序。
- 最终返回 `results`、`context`、`sources` 和可观测 `trace`。

## 4. 目录职责

| 目录 | 唯一职责 |
|---|---|
| `documents/` | 可维护的 Markdown 知识源，不存放索引缓存 |
| `corpus/` | 可选原始资料存放区 |
| `loaders/` | 文件读取与统一 `Document` 生成 |
| `parsers/` | Front Matter 和正文解析 |
| `chunking/` | 面向检索的递归切块 |
| `embedding/` | 本地 SentenceTransformers 与测试 Mock Provider |
| `vector_store/` | PostgreSQL/pgvector ORM、建表、索引、查询和健康检查 |
| `retrieval/` | Query Rewrite、过滤、双路召回、RRF |
| `reranker/` | Cross-Encoder、NoOp fallback 和工厂 |
| `pipeline/` | 唯一索引流水线与唯一 RAG 流水线 |
| `service/` | 对业务暴露的 KnowledgeService、Context、RAGService |
| `schemas/` | Document、Chunk、SearchResult、RAG Trace 类型 |
| `evaluation/` | 评测数据集、指标和运行报告 |
| `metadata/` | 分类、标签和知识治理元数据 |
| `prompts/` | 业务 Prompt 资源 |

## 5. 数据契约

模块间不再重复定义文档和切块对象：

- `schemas.document.Document` 复用 `loaders.base.Document`。
- `schemas.chunk.Chunk` 复用 `chunking.base.Chunk`。
- `schemas.search_result.SearchResult` 规定检索结果最小字段。
- `schemas.rag` 提供来源、上下文和 Trace 类型。

兼容入口 `backend/app/knowledge/knowledge_loader.py` 只负责把正式 Loader
适配到后端既有调用方式，不复制解析逻辑。

## 6. 数据库和可观测性

初始化时源码会创建或校验：

- `vector` 扩展；
- `knowledge_documents`、`knowledge_chunks`；
- `embedding vector(N)`；
- `embedding` 上的 HNSW cosine index；
- `search_vector` 生成列；
- `search_vector` 上的 GIN index；
- `hnsw.ef_search` 会话级参数。

`/api/knowledge/search/debug` 和 `RAGPipeline` Trace 记录改写、双路候选、
RRF、重排数量及各阶段耗时，便于答辩演示和回归排查。

## 7. 质量边界

代码架构可以通过单元测试验证，但 HNSW、FTS、GIN、Embedding 维度和真实
召回指标必须在 PostgreSQL + pgvector 环境中验证。当前环境若没有 Docker
或数据库，只能报告“未完成真实数据库验证”，不能把单元测试当作替代结果。

知识正文共 244 篇。内容审计会生成 `CONTENT_EXPANSION_TASKS.md`，其中列出的
Front Matter、来源数量和 Chunk 长度问题需要按 `documents/扩写要求.txt`
逐篇由人工或其他 AI 扩写后复核，不能在架构改造阶段伪造完成。

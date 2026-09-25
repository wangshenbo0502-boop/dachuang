# 多阶段混合检索设计

## 技术路线

系统使用 PostgreSQL 作为知识元数据、全文索引和向量的统一存储。Dense 通道通过 pgvector `vector_cosine_ops` HNSW 索引召回；Lexical 通道通过 PostgreSQL `tsvector`、GIN 和 `ts_rank_cd` 召回。中文正文入库时补充 2 到 4 字检索词面，避免 `simple` 配置无法切分连续中文，同时保持排序和匹配发生在 PostgreSQL 内。

原始 Query 进入 FTS，规则或可选 LLM 生成的 Rewrite Query 进入 Embedding/HNSW。结果使用 `1 / (RRF_K + rank)` 融合。RRF Top-N 再进入可配置 Cross-Encoder，最终 Top-K 构建 DeepSeek Context。

## 数据库索引

- `ix_knowledge_chunks_embedding_hnsw`：`embedding vector_cosine_ops`
- `ix_knowledge_chunks_search_vector_gin`：`search_vector`
- `HNSW_M`、`HNSW_EF_CONSTRUCTION` 在建索引时生效
- `HNSW_EF_SEARCH` 在每次向量查询事务内通过 `SET LOCAL` 生效

已有数据库通过 `PgVectorStore.initialize()` 增量补充 `search_text`、`search_vector` 和 GIN 索引，不删除知识表。修改 HNSW 建库参数会重建 HNSW 索引，不重写文档内容。

## 元数据过滤

`KnowledgeFilter` 支持 `category/categories`、`job_type`、`skill`、`source`、`document_id` 和 `tags`。Vector 与 FTS 使用同一过滤对象并在 SQL 层执行。`JobFilter`、`SkillFilter`、`ResumeFilter`、`GrowthFilter` 为业务提供领域默认值，业务服务不拼 SQL。

## 降级边界

- Embedding 通道失败：FTS 仍可召回并进入 RRF。
- FTS 通道失败：HNSW 结果仍可进入 RRF。
- Cross-Encoder 未启用或推理失败：保持 RRF 顺序。
- 整个知识库不可用：已有 AI 业务的 `rag_integration` 记录错误并使用原 Prompt，避免破坏主业务。

## 可观测性

Debug API 返回 Query Rewrite、每条候选的四类分数、各阶段结果、候选数量、Context 和阶段耗时。Health API 和 `scripts/check_rag_indexes.py` 从数据库系统表实际检查扩展、列和索引，不能用配置值冒充健康状态。

## 开源项目对照

2026-09-25 通过 GitHub API 核对以下活跃项目：

| 项目 | 借鉴点 | 本项目取舍 |
|---|---|---|
| `pgvector/pgvector` | HNSW、Cosine 运算类、查询参数 | 直接采用，保持 PostgreSQL 为唯一向量库 |
| `infiniflow/ragflow` | 分阶段检索、重排、可追踪来源 | 采用流程思想，不引入其独立服务和存储体系 |
| `deepset-ai/haystack` | 显式 Pipeline、组件可替换和评测 | 采用接口边界，不增加框架依赖 |
| `langchain-ai/langchain-postgres` | PostgreSQL 后端抽象 | 保持当前 SQLAlchemy 实现，减少迁移风险 |
| `run-llama/llama_index` | Retriever/Reranker 分层和评测 | 采用分层结构，不引入第二套索引抽象 |

本项目进一步保留就业领域规则重写、领域 Filter 和原业务安全降级，避免变成通用聊天框架。

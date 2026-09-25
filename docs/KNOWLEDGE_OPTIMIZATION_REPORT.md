# Knowledge 知识库架构优化报告

## 目标

围绕 PostgreSQL + pgvector + RAG 完成代码收敛，保留 HNSW、FTS、Hybrid
Retrieval、RRF、Reranker、Query Rewrite、RAG 和 Evaluation，并让后端业务
只依赖一个稳定入口。

## 已完成改造

1. 统一 Loader、Parser、Chunking、Embedding、Vector Store、Retrieval、
   Pipeline 和 Service 的生产边界。
2. 新增唯一 `RAGPipeline`，固定 Query Rewrite -> Filter -> 双路召回 ->
   RRF -> Reranker -> Context 的顺序。
3. 新增 Reranker 工厂，统一 Cross-Encoder 与显式 NoOp fallback。
4. 统一 Document、Chunk、SearchResult、RAG Trace Schema，减少重复数据契约。
5. 让后端 Loader 适配正式 `loaders/` 和 `parsers/`，保持原业务调用方式。
6. 保留 `source + content_hash` 增量索引和 PostgreSQL 健康检查。
7. 清理旧目录、死代码、预留工作流和缓存残留。
8. 增加 RAG 编排顺序、来源和 Trace 统计的回归测试。

## 当前真实链路

```text
Index: documents -> loaders -> parsers -> chunking -> embedding -> pgvector
Query: rewrite -> filters -> HNSW/FTS -> RRF -> reranker -> context -> business AI
```

## 验证结果

| 项目 | 结果 |
|---|---|
| `pytest backend/tests/knowledge -q` | 19 passed, 1 skipped |
| 全后端 `unittest` | 8 passed |
| `compileall` | 通过 |
| PostgreSQL 容器 | 当前环境无 Docker 命令，未启动 |
| HNSW/FTS/GIN 真实检查 | 未执行，不能伪造结果 |
| 真实 RAG 评测 | 未执行，等待 PostgreSQL + pgvector |

全后端测试中看到的 `knowledge vector store requires PostgreSQL with pgvector`
是本机未配置数据库时的降级日志；业务测试仍通过，说明知识库不可用时不会
阻断已有 AI 接口。

## 内容治理结果

当前知识正文共 244 篇，已生成逐篇扩写清单。审计发现的主要问题是旧正文
尚未统一补齐 `id`、`keywords`、`status`、`summary`、`updated_at` 等字段，
部分长文也需要拆成更适合 Chunk 的语义章节。由于这些内容涉及真实来源和
时效性，本轮不自动编造或批量伪造，交由其他免费 AI 按扩写规则逐篇处理后
再运行审计和真实评测。

## 下一步执行顺序

1. 安装 Docker 并启动 `knowledge-db`。
2. 复制 `.env.example` 到 `.env`，确认 Embedding 维度与模型一致。
3. 执行 Seed、索引健康检查和 RAG Evaluation。
4. 按 `CONTENT_EXPANSION_TASKS.md` 逐篇补齐高优先级正文。
5. 每批扩写后重新 Seed、评测和检查来源可追溯性。

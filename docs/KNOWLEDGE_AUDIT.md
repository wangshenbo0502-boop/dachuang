# Knowledge 知识库审计报告

## 审计范围

审计日期：2026-09-25  
范围：`knowledge/` 代码、`knowledge/documents/` 知识正文、后端引用、测试与数据库脚本。  
约束：不修改前端，不删除知识正文，不切换 PostgreSQL + pgvector。

## 审计结论

知识库代码已收敛到一条生产链路，原来同时存在的旧目录、预留接口和重复
Schema 已清理。当前正文规模为 244 篇，分类如下：

| 分类 | 数量 |
|---|---:|
| jobs | 54 |
| skills | 45 |
| companies | 39 |
| interview | 34 |
| projects | 21 |
| competition | 13 |
| roadmap | 11 |
| market | 11 |
| policies | 9 |
| resume | 7 |

## 生产实现判定

确认保留并投入生产的模块：

- `loaders/`、`parsers/`、`chunking/`
- `embedding/`
- `vector_store/`
- `retrieval/`
- `reranker/`
- `pipeline/`
- `service/`
- `schemas/`
- `evaluation/`

后端只通过 `backend/app/knowledge/knowledge_loader.py` 和后端
`KnowledgeService` 适配正式模块，四个 AI 业务不再分别维护检索实现。

## 删除项

已删除的旧实现或预留目录：

```text
knowledge/cache/
knowledge/config/
knowledge/graph/
knowledge/indexes/
knowledge/ingestion/
knowledge/loader/
knowledge/parser/
knowledge/splitter/
knowledge/vectorstore/
knowledge/workflow/
knowledge/test_pipeline.py
knowledge/retrieval/context_builder.py
knowledge/embedding/embedding_model.py
knowledge/reranker/reranker.py
```

本次清理还会删除这些旧目录残留的 `__pycache__`，不触碰 `documents/`、
`corpus/`、评测数据和评测报告。

## 内容质量现状

内容审计脚本当前将 244 篇正文标记为需要改善，主要原因是旧内容尚未统一
补齐新的 Front Matter 字段、来源数量或 Chunk 友好结构。这不是代码错误，
也不能通过修改审计结果来掩盖。具体逐篇任务见：

`knowledge/CONTENT_EXPANSION_TASKS.md`

扩写必须遵守：

`knowledge/documents/扩写要求.txt`

## 真实验证边界

- Python 知识库专项测试：19 passed, 1 skipped。
- 全后端 unittest：已通过。
- Python 编译检查：已通过。
- PostgreSQL、pgvector、HNSW、FTS、GIN、真实召回指标：本次运行环境未安装
  Docker，且未提供可连接的 PostgreSQL，因此不能宣称已完成真实数据库验证。

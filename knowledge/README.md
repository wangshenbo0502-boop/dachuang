# Knowledge 知识库模块

> **文件名称**：README.md  
> **作用**：knowledge 模块总览，说明 RAG 架构、目录职责、数据流和升级路线。  
> **版本**：v0.3.0（RAG Architecture）  
> **更新**：2026-07-28

---

## 一、架构升级说明

| 项目 | v0.2（旧） | v0.3（新） |
|------|-----------|-----------|
| 知识格式 | JSON（大文件维护） | Markdown（按知识条目拆分） |
| 架构思想 | 四层工程化 | **轻量级 RAG** |
| 检索方式 | 配置式关键词匹配 | Retrieval 模块（Query Rewriter + Retriever + Context Builder） |
| 文档加载 | 无统一入口 | Loader 模块（6 种加载器） |
| 解析 | 直接读 JSON | Parser 模块（Markdown 解析 + 清洗） |
| 索引 | 无 | KeywordIndex（倒排索引） |
| 数据模型 | ad-hoc dict | schemas/ 统一类型契约 |
| 数据摄取 | 手动处理 | Ingestion Pipeline 协调层 |
| 扩展性 | 四层耦合 | 20 个模块解耦，可独立升级 |

---

## 二、完整目录结构

```
knowledge/
├── README.md                       ← 本文档
├── ARCHITECTURE.md                 ← 完整架构设计文档
│
├── corpus/                         # 原始语料（PDF/Word/Excel）【预留】
│
├── documents/                      # Markdown 知识文档（当前主力）
│   ├── jobs/                       # 岗位知识（5 篇）
│   ├── companies/                  # 企业知识（8 篇）
│   ├── skills/                     # 技能知识（22 篇）
│   ├── interview/                  # 面试知识（6 篇）
│   ├── projects/                   # 项目案例（12 篇）
│   ├── roadmap/                    # 学习路线（2 篇）
│   ├── resume/                     # 简历知识（1 篇）
│   ├── market/                     # 市场分析（1 篇）
│   ├── competition/                # 竞赛知识【预留】
│   └── policies/                   # 政策知识【预留】
│
├── ingestion/                      # 数据摄取流水线（Loader→Parser→Splitter→Indexes）
│
├── loader/                         # 文档加载器（Markdown/JSON/PDF/docx/Excel/Web）
├── parser/                         # 文档解析器（Markdown 解析 + 文本清洗）
├── splitter/                       # 文本切块器【预留，激活 Embedding 后启用】
│
├── schemas/                        # 数据模型定义（Document / Chunk / SearchResult）
│
├── indexes/                        # 索引存储（KeywordIndex 倒排索引，当前主力）
├── retrieval/                      # 检索模块（QueryRewriter + KeywordRetriever + SearchEngine + ContextBuilder）
├── reranker/                       # 重排序器【预留】
│
├── embedding/                      # Embedding 模型接口【预留】
├── vectorstore/                    # 向量数据库接口【预留，FAISS/ChromaDB/Milvus】
├── graph/                          # 知识图谱接口【预留，Neo4j/NetworkX】
│
├── evaluation/                     # RAG 评估模块【预留，MRR/NDCG/Faithfulness】
│
├── workflow/                       # RAG Pipeline（6 条业务流水线）
├── prompts/                        # Prompt 模板（4 个，四段式结构）
│
├── config/                         # 配置文件（knowledge/retrieval/embedding/llm/chunk）
├── metadata/                       # 元数据管理（分类/标签/版本/来源/日志）
└── cache/                          # 查询缓存【预留】
```

---

## 三、RAG 数据流

### 离线：数据预处理

```
corpus/（原始文件）【预留】
  │
  ▼
┌──────────────────────────────────────────┐
│           Ingestion Pipeline              │
│  Loader  →  Parser  →  Splitter  →  Index │
│  (加载)     (解析)     (切块)【预留】 (建索引) │
└────────────────────────────────┬─────────┘
                                 │
                                 ▼
                          indexes/（索引就绪）
```

### 在线：查询响应

```
User Query
  │
  ▼
QueryRewriter（查询改写 + 关键词提取）
  │
  ▼
KeywordRetriever（从 indexes/ 检索 TopK）
  │
  ▼
[Reranker]（重排序）【预留】
  │
  ▼
ContextBuilder（组装 LLM 上下文）
  │
  ▼
Prompt Builder（注入 prompts/ 模板 + Context）
  │
  ▼
DeepSeek API
  │
  ▼
Output Parser → Response
```

---

## 四、模块职责速查

| 模块 | 职责 | 状态 | 关键文件 |
|------|------|------|---------|
| `corpus/` | 存放原始二进制文件 | ⬜ 预留 | — |
| `documents/` | Markdown 知识文档 | ✅ 就绪 | 57+ .md |
| `ingestion/` | 摄取流水线协调层 | 🟡 框架 | `pipeline.py` |
| `loader/` | 加载各类文档 | ✅ 就绪 | `markdown_loader.py` |
| `parser/` | 解析文档内容 | 🟡 框架 | `markdown_parser.py` |
| `splitter/` | 文本切块 | ⬜ 预留 | `text_splitter.py` |
| `schemas/` | 数据模型定义 | ✅ 就绪 | `document.py`, `search_result.py` |
| `indexes/` | 关键词倒排索引 | 🟡 框架 | `keyword_index.py` |
| `retrieval/` | 检索 + 上下文组装 | 🟡 框架 | `search_engine.py`, `context_builder.py` |
| `reranker/` | 结果重排序 | ⬜ 预留 | `reranker.py` |
| `embedding/` | 文本向量化 | ⬜ 预留 | `embedding_model.py` |
| `vectorstore/` | 向量存储与检索 | ⬜ 预留 | `vectorstore.py` |
| `graph/` | 知识图谱 | ⬜ 预留 | `knowledge_graph.py` |
| `evaluation/` | RAG 质量评估 | ⬜ 预留 | `metrics.py` |
| `workflow/` | 6 条业务 Pipeline | 🟡 框架 | `career_pipeline.py` 等 |
| `prompts/` | 4 个 Prompt 模板 | ✅ 就绪 | `profile_prompt.md` 等 |
| `config/` | 5 个配置文件 | ✅ 就绪 | `knowledge_config.json` 等 |
| `metadata/` | 5 个元数据文件 | ✅ 就绪 | `category.json` 等 |
| `cache/` | 查询缓存 | ⬜ 预留 | `query_cache.json` |

> ✅ 已就绪 · 🟡 框架已就绪（待实现） · ⬜ 预留（未来激活）

---

## 五、升级路线

```
v0.3.0：Markdown + Keyword Retrieval（当前）
   │ ✅ 架构就绪，可开始实现各模块业务逻辑
   │
   ▼
v0.4.0：+ Embedding + FAISS
   │ 激活：splitter/ + embedding/ + vectorstore/（FAISS）
   │ 改动：retrieval/ 新增向量检索分支
   │
   ▼
v0.5.0：+ Hybrid Retrieval
   │ Keyword + Vector 融合检索
   │
   ▼
v0.6.0：+ Reranker
   │ 激活：reranker/
   │ 激活：evaluation/ 建立质量基线
   │
   ▼
v1.0.0：+ Milvus + Graph RAG
   │ 激活：graph/（Knowledge Graph）
   │ 可选：vectorstore/ 升级 Milvus
```

---

## 六、给 AI Agent 的工作建议

| 你想做什么 | 去哪里 |
|-----------|--------|
| 查找知识内容 | `documents/<category>/` 下查找对应 .md 文件 |
| 添加新知识 | `documents/<category>/` 下新增 .md（必须含 YAML Front Matter） |
| 了解架构设计 | 阅读 [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| 修改检索逻辑 | `retrieval/` 下的 `keyword_retriever.py`、`search_engine.py` |
| 新增业务场景 | `workflow/` 下新增 Pipeline 文件 |
| 调整 Prompt | `prompts/` 下修改对应模板 |
| 修改配置 | `config/` 下修改 JSON 文件 |
| 查分类/标签 | `metadata/` 下查看 `category.json`、`tags.json` |
| 查版本信息 | `metadata/version.json` |
| 新增文档加载器 | `loader/` 下新增 `*_loader.py` |
| 新增解析器 | `parser/` 下新增 `*_parser.py` |
| 处理数据预处理 | `ingestion/pipeline.py` |

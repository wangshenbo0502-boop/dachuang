# Knowledge 模块架构设计文档

> **版本**：v0.3.0  
> **架构范式**：轻量级 RAG（Retrieval-Augmented Generation）  
> **更新**：2026-07-28  
> **作者**：AI 架构工程师  

---

## 一、项目背景

**项目名称**：AI 驱动的大学生就业竞争力评估与提升助手

**定位**：面向计算机专业大学生，通过 AI 结合知识库，实现就业画像分析、岗位匹配、简历优化、成长规划、面试辅导、就业市场分析等功能。

**技术路线**：

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| Frontend | Vue3 + Vite + TypeScript | 后续迁移 React + Next.js |
| Backend | FastAPI（Python） | 异步高性能 Web 框架 |
| LLM | DeepSeek API | 主力大模型 |
| 知识库 | Markdown | 当前格式 |
| 检索 | Keyword Retrieval | 当前策略 |
| 索引 | 内存倒排索引 | 当前策略 |

**未来升级路线**：

```
Keyword Retrieval（当前）
  → Embedding（BGE-M3 / Qwen3-Embedding）
    → FAISS（本地向量索引）
      → Hybrid Search（关键词 + 向量融合）
        → Reranker（BGE-Reranker / Jina-Reranker）
          → Milvus（分布式向量数据库，可选）
            → Graph RAG（知识图谱增强）
```

---

## 二、v0.3 架构优化说明

### 相比原始设计的优化点

| 优化项 | 原因 |
|--------|------|
| `chunk/` → `splitter/` | `splitter` 是 RAG 社区（LangChain/LlamaIndex）的标准命名，语义更准确 |
| `indexing/` → `indexes/` | 名词形式表示"索引存储"，与 `loader/parser/retriever` 等动词行为模块形成清晰边界 |
| `vector_store/` → `vectorstore/` | 单单词命名，与 FAISS/ChromaDB/Milvus 社区一致，避免下划线歧义 |
| 新增 `ingestion/` | 协调 Loader → Parser → Splitter → Indexes 的数据处理流水线，弥补独立模块缺乏协调层的缺陷 |
| 新增 `schemas/` | 统一数据契约（Document/Chunk/SearchResult），避免各模块各自定义 dict，支持 IDE 类型提示 |
| 新增 `evaluation/` | RAG 评估基础设施，企业级项目必需的回归测试和线上监控锚点 |
| 新增 `graph/` | 为 Knowledge Graph 和 Graph RAG 预留完整接口，不需要等到需要时再重构 |
| 统一 `__init__.py` 导出 | 每个模块通过 `__init__.py` 对外暴露接口，模块间通过接口耦合而非实现耦合 |

---

## 三、设计目标

1. **当前阶段**：Markdown + Keyword Retrieval + DeepSeek API，纯 Python 实现，零框架依赖
2. **架构要求**：模块化、低耦合、高内聚
3. **扩展能力**：无需修改目录结构即可逐步激活 Embedding、FAISS、Hybrid Retrieval、Reranker、Graph RAG
4. **知识来源**：预留多格式接入能力（PDF、Word、Excel、Web、Database、Notion、GitHub）
5. **设计思想**：参考 LangChain/LlamaIndex/Dify/RagFlow 的模块划分经验，但不依赖任何框架

---

## 四、完整目录结构

```
knowledge/
│
├── corpus/                        # 原始语料（PDF、Word、Excel 等二进制文件）
│
├── documents/                     # Markdown 知识文档【核心数据层】
│   ├── jobs/                      # 岗位知识（5 篇）
│   ├── companies/                 # 企业知识（8 篇）
│   ├── skills/                    # 技能知识（22 篇）
│   ├── interview/                 # 面试知识（6 篇）
│   ├── projects/                  # 项目案例（12 篇）
│   ├── roadmap/                   # 学习路线（2 篇）
│   ├── resume/                    # 简历知识（1 篇）
│   ├── market/                    # 市场分析（1 篇）
│   ├── competition/               # 竞赛知识【预留】
│   └── policies/                  # 政策知识【预留】
│
├── ingestion/                     # 数据摄取流水线【协调层】
│   ├── __init__.py
│   ├── pipeline.py                # IngestionPipeline（Loader → Parser → Splitter → Index）
│   └── README.md
│
├── loader/                        # 文档加载器【数据接入层】
│   ├── __init__.py
│   ├── markdown_loader.py         # Markdown 加载（当前主力）
│   ├── json_loader.py             # JSON 加载（兼容旧数据）
│   ├── pdf_loader.py              # PDF 加载【预留】
│   ├── docx_loader.py             # Word 加载【预留】
│   ├── excel_loader.py            # Excel 加载【预留】
│   └── web_loader.py              # 网页加载【预留】
│   └── README.md
│
├── parser/                        # 文档解析器【数据处理层】
│   ├── __init__.py
│   ├── markdown_parser.py         # Markdown 解析（YAML Front Matter + Body）
│   ├── document_parser.py         # 通用解析器（按文件类型分发）
│   ├── text_cleaner.py            # 文本清洗
│   └── README.md
│
├── splitter/                      # 文本切块器【预处理层，当前关闭】
│   ├── __init__.py
│   ├── text_splitter.py           # RecursiveCharacterTextSplitter【预留】
│   └── README.md
│
├── schemas/                       # 数据模型定义【类型契约层】
│   ├── __init__.py
│   ├── document.py                # Document 数据类
│   ├── chunk.py                   # Chunk 数据类【预留】
│   ├── search_result.py           # SearchResult 数据类
│   └── README.md
│
├── indexes/                       # 索引模块【索引存储层】
│   ├── __init__.py
│   ├── keyword_index.py           # 关键词倒排索引（当前主力）
│   ├── base_index.py              # 索引基类（统一接口）【建议新增】
│   └── README.md
│
├── retrieval/                     # 检索模块【核心检索层】
│   ├── __init__.py
│   ├── query_rewriter.py          # Query 改写器
│   ├── keyword_retriever.py       # 关键词检索器（当前主力）
│   ├── search_engine.py           # 检索引擎统一入口
│   ├── context_builder.py         # 上下文组装器
│   └── README.md
│
├── reranker/                      # 重排序器【精排层，当前关闭】
│   ├── __init__.py
│   ├── reranker.py                # Reranker 接口【预留】
│   └── README.md
│
├── embedding/                     # Embedding 模型接口【向量化层，当前关闭】
│   ├── __init__.py
│   ├── embedding_model.py         # Embedding 接口【预留】
│   └── README.md
│
├── vectorstore/                   # 向量数据库接口【向量存储层，当前关闭】
│   ├── __init__.py
│   ├── vectorstore.py             # VectorStore 接口【预留】
│   └── README.md
│
├── graph/                         # 知识图谱模块【图谱层，当前关闭】
│   ├── __init__.py
│   ├── knowledge_graph.py         # KnowledgeGraph 接口【预留】
│   └── README.md
│
├── workflow/                      # RAG 工作流【业务编排层】
│   ├── __init__.py
│   ├── career_pipeline.py         # 就业画像分析 Pipeline
│   ├── job_pipeline.py            # 岗位匹配 Pipeline
│   ├── resume_pipeline.py         # 简历优化 Pipeline
│   ├── planner_pipeline.py        # 成长规划 Pipeline
│   ├── interview_pipeline.py      # 面试辅导 Pipeline
│   ├── market_pipeline.py         # 市场分析 Pipeline
│   └── README.md
│
├── evaluation/                    # RAG 评估模块【质量保障层，当前关闭】
│   ├── __init__.py
│   ├── metrics.py                 # 评估指标接口【预留】
│   ├── test_cases.json            # 测试用例集
│   └── README.md
│
├── prompts/                       # Prompt 模板【LLM 交互层】
│   ├── profile_prompt.md          # 就业画像 Prompt
│   ├── job_prompt.md              # 岗位匹配 Prompt
│   ├── resume_prompt.md           # 简历优化 Prompt
│   ├── growth_prompt.md           # 成长规划 Prompt
│   └── README.md
│
├── config/                        # 配置文件【配置层】
│   ├── knowledge_config.json      # 知识库全局配置
│   ├── retrieval_config.json      # 检索策略配置
│   ├── embedding_config.json      # Embedding 模型配置
│   ├── llm_config.json            # LLM 调用配置
│   ├── chunk_config.json          # 文本切块配置
│   └── README.md
│
├── metadata/                      # 元数据管理【元数据层】
│   ├── category.json              # 知识分类体系
│   ├── tags.json                  # 统一标签体系
│   ├── version.json               # 版本记录
│   ├── source.json                # 知识来源追溯
│   ├── update_log.json            # 更新日志
│   └── README.md
│
├── cache/                         # 查询缓存【加速层，当前关闭】
│   ├── query_cache.json           # 查询缓存
│   └── README.md
│
└── README.md                      # 模块总览
```

---

## 五、数据流与模块协作关系

### 离线流程（数据预处理）

```
corpus/（原始文件）
  │
  ▼
┌─────────────────────────────────────────┐
│             Ingestion Pipeline           │ ← ingestion/pipeline.py
│                                          │
│  Loader  →  Parser  →  Splitter  →  Index │
│  (加载)     (解析)     (切块)      (建索引) │
│                                          │
│  Markdown    YAML/       [未来]    Keyword │
│  JSON        Body                   Index  │
└────────────────────────────────┬────────┘
                                 │
                                 ▼
                          indexes/（索引就绪）
```

### 在线流程（查询响应）

```
用户 Query
  │
  ▼
Query Rewriter（查询改写 + 关键词提取）
  │
  ▼
Keyword Retriever（关键词检索 → TopK Documents）
  │
  ▼
[ Reranker ]（重排序，未来激活）
  │
  ▼
Context Builder（组装 LLM 上下文）
  │
  ▼
Prompt Builder（注入 Prompt 模板 + Context）
  │
  ▼
DeepSeek API（调用大模型）
  │
  ▼
Output Parser（解析输出）
  │
  ▼
Response（返回结果）
```

### 升级触发后新增的数据流

```
【激活 Embedding】
  Chunk → Embedding Model → Vector Embeddings → VectorStore

【激活 Hybrid Retrieval】
  Query → Keyword Retriever ─┐
  Query → Embedding → Vector Search ─┤ → Fusion → TopK → Reranker → Context

【激活 Graph RAG】
  Query → Entity Extraction → Graph Query → Graph Context ─┐
  Query → Keyword/Hybrid Retriever ────────────────────────┤ → Fusion → LLM
```

---

## 六、各目录详细职责说明

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【corpus/】— 原始语料库

**目录作用**：保存知识的原始二进制文件（PDF、Word、Excel、招聘JD截图、行业报告等），是知识库的数据源头。

**为什么需要**：
- `documents/` 存放的是解析整理后的 Markdown 知识文档
- `corpus/` 保留原始文件，支持后续重新解析、更新源数据
- 原始文件可能包含 Markdown 无法保留的信息（排版、图片、表格精确位置）

**当前版本**：空目录。所有知识已直接整理为 `documents/` 下的 Markdown。

**未来扩展**：
- 上传 PDF 简历模板、企业招聘简章 PDF
- 通过 `loader/pdf_loader.py`、`loader/docx_loader.py` 提取文本
- 通过 `ingestion/pipeline.py` 自动转化为 Markdown 并更新索引

**RAG 流程位置**：数据流的起点。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【documents/】— Markdown 知识文档

**目录作用**：存放整个系统的核心知识文档，是 RAG 检索的主要数据源。

**为什么需要**：
- Prompt 不能保存大量知识（Token 上限、成本）
- 知识必须独立管理，与 Prompt 分离
- Markdown 是当前最适合的关键词检索格式

**当前版本**：
- 10 个子分类目录，共 57+ 篇 Markdown 文档
- 每篇文档含 YAML Front Matter（title/category/tags/source/date）
- 使用结构化标题（H1/H2/H3）便于解析

**子目录说明**：

| 子目录 | 知识类型 | 文档数 | 示例 |
|--------|---------|--------|------|
| `jobs/` | 岗位要求与技能 | 5 | Java后端开发工程师.md |
| `companies/` | 企业招聘特点 | 8 | 字节跳动.md |
| `skills/` | 技能学习方法 | 22 | JavaScript.md, Python.md |
| `interview/` | 面试题库 | 6 | Java面试题.md |
| `projects/` | 练手项目案例 | 12 | 个人博客系统.md |
| `roadmap/` | 职业成长路径 | 2 | career_paths.md |
| `resume/` | 简历规范知识 | 1 | resume_guide.md |
| `market/` | 就业市场数据 | 1 | market_2026.md |
| `competition/` | 竞赛信息 | 0 | 【预留】 |
| `policies/` | 就业政策 | 0 | 【预留】 |

**最终目的**：成为 RAG 系统唯一的权威知识来源（Single Source of Truth）。

**未来扩展**：
- 支持自动从外部数据源同步更新
- 支持知识版本管理（Git 管理 .md 文件天然支持）
- 支持 CMS 后台管理编辑

**RAG 流程位置**：Loader 读取 → Parser 解析 → Indexes 索引 → Retriever 检索。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【ingestion/】— 数据摄取流水线

**目录作用**：协调 Loader → Parser → Splitter → Indexes 的全流程。将原始文档转化为可供检索的索引。

**为什么需要（vs 原文档）**：
- 原文档将 Loader/Parser/Splitter/Indexes 定义为独立模块，但缺少协调层
- 每个 Pipeline 如果各自调用 Loader + Parser，会导致代码重复
- Ingestion 是 RAG 系统的"ETL 层"，将数据处理职责收敛到一个入口

**当前版本**：
- `IngestionPipeline.run()`：一次性全量摄取 `documents/` 下所有 Markdown 文件
- `dry_run()`：预演模式，统计将要处理的文件数量

**最终目的**：提供统一的数据预处理入口，避免各模块自行组装数据处理线。

**未来扩展**：
- 增量摄取（检测新增/修改的文件，只更新增量索引）
- 定时调度（cron 表达式自动更新）
- 多来源并发摄取

**RAG 流程位置**：数据预处理的总协调入口。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【loader/】— 文档加载器

**目录作用**：负责从各种来源读取原始文档内容，统一返回字符串或 Document 对象。

**为什么需要**：
- 不同知识来源格式不同（Markdown / JSON / PDF / Word / Excel / 网页）
- 需要统一的读取接口，让上游（Parser）无需关心文件类型

**当前版本**：
- `MarkdownLoader`：读取 `documents/` 下的 .md 文件（主力加载器）
- `JsonLoader`：兼容旧版 JSON 数据

**未来版本**：
- `PdfLoader`：集成 PyMuPDF 提取 PDF 文本
- `DocxLoader`：集成 python-docx 提取 Word 文本
- `ExcelLoader`：集成 openpyxl/pandas 读取 Excel 数据
- `WebLoader`：集成 requests + BeautifulSoup 抓取网页

**最终目的**：将所有知识来源统一转换为 Document 对象，交给 Parser 继续处理。

**RAG 流程位置**：数据接入层，corpus/ → Loader → Parser。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【parser/】— 文档解析器

**目录作用**：将 Loader 读取的原始文本解析为结构化数据（提取元数据、标题层级、清洗无效字符）。

**为什么需要**：
- 原始文本包含各种格式标记（YAML Front Matter、Markdown 语法）
- 需要提取结构化元数据（title/tags/category）供检索使用
- 需要清洗无意义字符，减少 Token 浪费

**当前版本**：
- `MarkdownParser.parse()`：解析 YAML Front Matter + Markdown Body
- `TextCleaner.clean()`：基础文本清洗

**最终目的**：将所有知识统一为 AI 可处理的结构化数据格式。

**RAG 流程位置**：数据处理层，Loader → Parser → Splitter。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【splitter/】— 文本切块器

**目录作用**：将长文档切分为适合 Embedding 模型的文本块（Chunk）。

**为什么需要**：
- Embedding 模型有最大 Token 限制（如 BGE-M3 最大 8192 tokens）
- 长文档整体向量化会丢失局部语义
- 切块是向量检索的必需前置步骤

**当前版本**：【关闭】。关键词检索阶段不需要切块。仅保留接口框架。

**未来版本**：
- 采用 Recursive Character Text Splitter 算法
- 参考 LangChain `RecursiveCharacterTextSplitter`
- 按 `config/chunk_config.json` 配置切块参数（chunk_size/chunk_overlap）
- 支持按文档类型定制切块策略

**最终目的**：提高向量检索的命中精度，减少单次检索的 Token 消耗。

**RAG 流程位置**：预处理层，Parser → Splitter → Indexes（激活 Embedding 后）。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【schemas/】— 数据模型定义

**目录作用**：定义 RAG 系统中所有模块共享的核心数据结构（Document / Chunk / SearchResult）。

**为什么需要（vs 原文档）**：
- 原文档缺少统一的数据契约层，各模块可能各自定义 ad-hoc dict
- 统一 dataclass 支持 IDE 类型提示和静态检查
- 未来迁移到 Pydantic v2 可获得 JSON Schema 导出和自动校验
- 所有模块通过 schemas 定义的接口类型耦合，而非实现耦合

**当前版本**：
- `Document`：doc_id + content + metadata + source_path
- `SearchResult`：doc_id + content + score + metadata + rank
- `Chunk`：【预留】chunk_id + doc_id + content + embedding

**最终目的**：建立模块间的类型契约，减少数据格式不一致导致的 Bug。

**RAG 流程位置**：横切层，所有模块共享使用。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【indexes/】— 索引存储

**目录作用**：为知识文档建立检索索引，让 Retriever 能快速定位相关知识。

**为什么需要**：
- 直接遍历所有 Markdown 文件效率太低
- 索引可以预计算词频/位置，加速检索
- 索引与检索策略解耦（同一份索引可服务不同检索策略）

**当前版本**：
- `KeywordIndex`：基于内存的关键词倒排索引
  - `build(documents)`：构建索引
  - `search(query, top_k)`：检索
  - `add_document()` / `remove_document()`：增量维护

**未来升级路线**：
```
KeywordIndex（当前）
→ EmbeddingIndex（BGE-M3/Qwen3-Embedding）
→ FAISSIndex（本地持久化）
→ HybridIndex（关键词 + 向量融合）
→ MilvusIndex（分布式，可选）
```

**最终目的**：提供高性能、可扩展的检索索引基础设施。

**RAG 流程位置**：索引存储层，Splitter → Indexes → Retriever。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【retrieval/】— 检索模块

**目录作用**：整个 RAG 系统的核心模块。负责接收用户查询，从索引中检索相关文档，组装为 LLM 可消费的上下文。

**检索流程图**：

```
User Query
  → QueryRewriter（查询改写 + 关键词提取）
    → KeywordRetriever（从索引检索 TopK）
      → ContextBuilder（组装 LLM 上下文）
        → 输出给 Workflow Pipeline
```

**当前版本**：
- `QueryRewriter`：基础同义词扩展 + 关键词提取
- `KeywordRetriever`：从 KeywordIndex 检索 TopK 文档
- `SearchEngine`：统一检索入口，协调 Rewriter + Retriever
- `ContextBuilder`：按相关性排序组装上下文，控制 Token 预算

**未来版本**：
- 激活 Embedding 后：`search_engine.py` 中增加向量检索分支
- 激活 Hybrid 后：关键词 + 向量融合排序
- 激活 Reranker 后：在 ContextBuilder 之前插入重排序

**最终目的**：从知识库中找到最相关的内容提供给 LLM，显著提升回答质量。

**RAG 流程位置**：核心检索层，Indexes → Retrieval → Workflow Pipeline。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【reranker/】— 重排序器

**目录作用**：对 Retriever 返回的 TopK 结果进行二次精排，进一步提高相关性。

**为什么需要**：
- 关键词检索是粗排（召回率高，但精度有限）
- Hybrid 检索也需要精排来融合关键词和向量结果
- Reranker 用专用排序模型（Cross-Encoder）重新打分

**当前版本**：【关闭】。仅保留接口框架。

**未来模型候选**：
| 模型 | 提供方 |
|------|--------|
| BGE-Reranker-v2-m3 | BAAI |
| Jina Reranker v2 | Jina AI |
| Cohere Rerank | Cohere |

**最终目的**：将最相关的结果排在最前面，提升 Context Builder 的上下文质量。

**RAG 流程位置**：Retriever → Reranker → ContextBuilder。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【embedding/】— Embedding 模型接口

**目录作用**：提供文本向量化的统一接口。

**为什么需要**：
- 关键词检索只能匹配字面意思，无法理解语义
- Embedding 将文本映射到语义空间，支持"意思相似"的检索
- 统一接口可以无缝切换不同的 Embedding 模型

**当前版本**：【关闭】。仅保留接口框架。

**未来模型候选**：
| 模型 | 提供方 | 维度 | 推荐理由 |
|------|--------|------|---------|
| BGE-M3 | BAAI | 1024 | 多语言、社区活跃、中文效果最优 |
| Qwen3-Embedding | 阿里 | 2048 | 中文能力极强 |
| Jina Embedding v3 | Jina AI | 1024 | 多语言、Task-specific LoRA |
| SentenceTransformer | UKP | 可变 | 生态丰富、模型选择多 |

**最终目的**：支持语义检索，将关键词 RAG 升级为向量 RAG。

**RAG 流程位置**：向量化层，Splitter → Embedding → VectorStore。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【vectorstore/】— 向量数据库接口

**目录作用**：提供向量存储和相似度检索的统一接口。

**为什么需要**：
- Embedding 向量需要在专用数据结构中存储和检索
- 不同阶段可能需要不同的向量数据库（开发用 FAISS、生产用 Milvus）
- 统一接口可以在不修改业务代码的情况下切换底层存储

**当前版本**：【关闭】。仅保留接口框架。

**未来候选**：
| 数据库 | 类型 | 适用场景 |
|--------|------|---------|
| FAISS | 本地/内存 | 开发测试、小规模部署 |
| ChromaDB | 本地/嵌入式 | 轻量级应用、原型验证 |
| Milvus | 分布式 | 生产环境、大规模数据 |
| Pinecone | 云 SaaS | 免运维 |

**最终目的**：提供高性能的向量相似度检索能力。

**RAG 流程位置**：向量存储层，Embedding → VectorStore → Hybrid Retriever。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【graph/】— 知识图谱模块

**目录作用**：构建技能-岗位-企业的领域知识图谱，支持图检索增强生成（Graph RAG）。

**为什么需要（vs 原文档）**：
- 传统 RAG 只能检索相似文本，无法理解实体间的结构化关系
- "学 Vue 之前需要先掌握 JavaScript" 这种依赖关系需要图来表达
- Graph RAG 是 2025-2026 年的前沿 RAG 增强技术（Microsoft Graph RAG）

**当前版本**：【关闭】。仅保留接口框架。

**未来实体与关系**：
- 实体：Skill（技能）、Job（岗位）、Company（企业）、Project（项目）
- 关系：REQUIRES（前置依赖）、RECOMMENDS（推荐）、BELONGS_TO（归属）

**技术选型**：
- 开发阶段：NetworkX（纯 Python）
- 生产阶段：Neo4j

**最终目的**：语义检索 + 图谱推理 = 更精准的知识发现。

**RAG 流程位置**：图谱增强层，与 Retrieval 并行工作，结果在 Context Builder 融合。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【workflow/】— RAG 工作流

**目录作用**：编排完整的 RAG 流程，每个 Pipeline 对应一个业务场景。

**为什么需要**：
- retrieval/ 模块只负责检索，不负责业务流程编排
- 不同业务场景需要组合不同的知识来源和 Prompt 模板
- Pipeline 将检索、上下文组装、Prompt 注入、LLM 调用、输出解析串联起来

**当前版本**：6 条 Pipeline 框架：

| Pipeline | 业务场景 | 核心流程 |
|----------|---------|---------|
| `CareerPipeline` | 就业画像分析 | 检索用户技能差距 → 生成画像报告 |
| `JobPipeline` | 岗位匹配 | 检索匹配岗位 → 输出匹配列表 |
| `ResumePipeline` | 简历优化 | 检索简历规范 → ATS 优化建议 |
| `PlannerPipeline` | 成长规划 | 检索学习路线 → 生成阶段计划 |
| `InterviewPipeline` | 面试辅导 | 检索面试题库 → 生成答题指导 |
| `MarketPipeline` | 市场分析 | 检索薪资行情 → 输出市场报告 |

**每个 Pipeline 的标准流程**：

```
Receive Query
  → SearchEngine.search(query, category)
    → ContextBuilder.build(documents)
      → Prompt Builder（注入对应 Prompt 模板）
        → DeepSeek API
          → Output Parser
            → Response
```

**最终目的**：统一 AI 调用流程，每个业务场景只需配置 Pipeline 参数即可运转。

**RAG 流程位置**：业务编排层，调用 retrieval/ + prompts/，输出最终结果。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【evaluation/】— RAG 评估模块

**目录作用**：评估 RAG 系统的检索质量和生成质量，是线上监控和迭代优化的锚点。

**为什么需要（vs 原文档）**：
- 没有评估就无法衡量 RAG 系统的真实效果
- 每次 Prompt/索引/检索策略变更后，需要回归测试
- 企业级 RAG 项目必须建立质量基线

**当前版本**：【关闭】。仅保留接口框架。

**未来评估维度**：

| 维度 | 指标 | 含义 |
|------|------|------|
| 检索质量 | MRR | 正确答案排在第几位 |
| 检索质量 | Recall@K | TopK 中是否包含正确答案 |
| 生成质量 | Faithfulness | 回答是否忠于上下文（不瞎编） |
| 生成质量 | Answer Relevance | 回答是否切题 |
| 端到端 | RAGAS Score | 综合评分 |

**最终目的**：建立 RAG 系统的量化质量保障体系。

**RAG 流程位置**：质量保障层，对 Workflow 输出进行离线评估。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【prompts/】— Prompt 模板

**目录作用**：管理所有 LLM Prompt 模板，与知识库完全分离。

**为什么需要**：
- Prompt 与知识必须分离（v0.2 的核心教训）
- 不同场景需要不同的 System Prompt + Instruction
- 统一管理便于批量调试和 A/B 测试

**当前版本**：4 个场景模板（就业画像 / 岗位匹配 / 简历优化 / 成长规划）。

**模板结构（四段式）**：
- `[SYSTEM]`：模型角色 + 行为约束
- `[CONTEXT]`：上下文占位符（由 Context Builder 动态填充）
- `[INSTRUCTION]`：分步指令 + CoT 思考链
- `[OUTPUT]`：JSON Schema 输出格式

**RAG 流程位置**：LLM 交互层，Workflow → Prompt + Context → LLM。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【config/】— 配置文件

**目录作用**：集中管理 RAG 系统的所有配置参数，实现配置与代码分离。

**配置文件清单**：

| 文件 | 说明 |
|------|------|
| `knowledge_config.json` | 全局路径、分类、加载策略 |
| `retrieval_config.json` | 检索策略（keyword/embedding/hybrid）|
| `embedding_config.json` | Embedding 模型候选配置 |
| `llm_config.json` | DeepSeek API 参数 |
| `chunk_config.json` | 切块策略配置 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【metadata/】— 元数据管理

**目录作用**：管理知识库的元数据（分类体系、标签、版本、来源追溯）。

**元数据文件清单**：

| 文件 | 说明 |
|------|------|
| `category.json` | 10 大知识分类定义 |
| `tags.json` | 统一标签体系（语言/框架/难度/地域）|
| `version.json` | 版本记录 + 升级路线图 |
| `source.json` | 知识来源追溯 |
| `update_log.json` | 更新日志 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【cache/】— 查询缓存

**目录作用**：缓存高频查询的检索结果，减少重复的文档扫描和 LLM 调用。

**当前版本**：【关闭】。JSON 文件缓存，预留 Redis 接口。

**最终目的**：降低 AI 重复调用成本，提高响应速度。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 七、模块激活状态总览

```
✅ = 已就绪    🟡 = 框架已就绪（待实现）    ⬜ = 预留接口
```

| 模块 | 状态 | 阶段 | 激活触发条件 |
|------|------|------|-------------|
| `documents/` | ✅ | v0.3 | — |
| `loader/` | ✅ (Markdown) | v0.3 | — |
| `parser/` | ✅ (Markdown) | v0.3 | — |
| `schemas/` | ✅ | v0.3 | — |
| `indexes/` | 🟡 | v0.3 | 实现 `keyword_index.py` |
| `retrieval/` | 🟡 | v0.3 | 实现 4 个文件 |
| `workflow/` | 🟡 | v0.3 | 实现 6 条 Pipeline |
| `prompts/` | ✅ | v0.3 | — |
| `ingestion/` | 🟡 | v0.3 | 实现 `pipeline.py` |
| `corpus/` | ⬜ | v0.4+ | 有原始文件需要管理时 |
| `splitter/` | ⬜ | v0.4 | 激活 Embedding 时 |
| `embedding/` | ⬜ | v0.4 | 需要语义检索时 |
| `vectorstore/` | ⬜ | v0.5 | 有 Embedding 向量需要存储时 |
| `reranker/` | ⬜ | v0.6 | Hybrid Retrieval 后需要精排时 |
| `graph/` | ⬜ | v1.0 | 需要结构化关系推理时 |
| `evaluation/` | ⬜ | v0.4+ | 需要建立质量基线时 |
| `cache/` | ⬜ | v0.4+ | 查询量达到需要缓存时 |

---

## 八、升级路线图

```
v0.3.0：Markdown + Keyword Retrieval（当前）
   │ ✅ 架构就绪，可开始实现各模块业务逻辑
   │
   ▼
v0.4.0：+ Embedding + FAISS
   │ 激活：splitter/ + embedding/ + vectorstore/（FAISS）
   │ 改动：retrieval/ 新增向量检索分支
   │ 改动：indexes/ 新增 EmbeddingIndex
   │
   ▼
v0.5.0：+ Hybrid Retrieval
   │ 激活：Hybrid Search = Keyword + Vector 融合
   │ 改动：SearchEngine 加入融合策略
   │
   ▼
v0.6.0：+ Reranker
   │ 激活：reranker/
   │ 改动：检索流程中 Retriever → Reranker → ContextBuilder
   │ 激活：evaluation/ 建立质量基线
   │
   ▼
v1.0.0：+ Milvus + Graph RAG
   │ 激活：graph/（Knowledge Graph）
   │ 可选：vectorstore/ 升级为 Milvus 分布式
   │ 改动：Context Builder 融合图谱推理结果
```

---

## 九、设计原则

1. **纯 Python 实现**：不依赖 LangChain、LlamaIndex、Haystack 等框架。所有模块自行实现，便于完全掌控底层逻辑。

2. **模块间通过接口耦合**：每个模块通过 `__init__.py` 对外暴露类，其他模块 import 时依赖接口而非实现。

3. **预留即设计**：`splitter/`、`embedding/`、`vectorstore/`、`reranker/`、`graph/`、`evaluation/` 在当前阶段全部关闭，但目录、接口、配置文件均已就绪。未来激活时只需填充实现，无需修改架构。

4. **配置与代码分离**：所有可调参数集中在 `config/` 目录，模块代码不硬编码配置值。

5. **知识格式标准化**：所有知识文档使用 Markdown + YAML Front Matter，便于人类阅读和机器解析。

6. **数据模型统一**：`schemas/` 定义 Document / Chunk / SearchResult 标准模型，消除 ad-hoc dict 传递。

---

## 十、后续开发建议

1. **优先实现 `indexes/keyword_index.py`**：倒排索引是检索的基础，先让检索流程跑通
2. **其次实现 `retrieval/`**：Query Rewriter → Keyword Retriever → Context Builder 串联
3. **然后实现 `workflow/`**：6 条 Pipeline 逐个实现，每条 Pipeline 可以独立调试
4. **最后实现 `ingestion/`**：将 Loader + Parser + Index 串联为自动化流程
5. **Embedding 阶段切换时**：先将 `splitter/text_splitter.py` 实现，再激活 `embedding/` 和 `vectorstore/`

# 05 RAG 知识库设计文档

> **文档版本**：V2.1
> **更新日期**：2026-09-07
> **基准代码**：`knowledge/`（独立 RAG 模块，自述版本 v0.3，见 `knowledge/ARCHITECTURE.md`）+ `backend/app/knowledge/`（后端适配层）
> **前置阅读**：[01-项目开发说明书](./01-项目开发说明书.md) 第 9.2 节（知识访问边界）

---

## 1. 总体结构：独立模块 + 后端适配层

```
knowledge/                     ← 独立于后端的通用 RAG 模块（纯 Python，零框架依赖）
├── documents/                 ← 知识文档（Markdown，10 个分类，248 篇 + 分类 README）
├── prompts/                   ← AI 系统 Prompt（外置，见 04 第 7 章）
├── loader/  parser/           ← 已实现：文档加载 / Front-Matter 解析
├── indexes/ retrieval/        ← 已实现：关键词倒排索引 / 检索管线
├── ingestion/ workflow/       ← 部分实现：摄取编排 / 业务流水线骨架
├── embedding/ vectorstore/ splitter/ reranker/ graph/ evaluation/  ← 预留接口（未实现）
└── config/ cache/ corpus/ metadata/ schemas/  ← 配置与预留

backend/app/knowledge/         ← 后端适配层（业务唯一访问入口）
├── knowledge_loader.py         把 knowledge/ 的 Loader/Parser 包装为 KnowledgeLoader
├── knowledge_service.py        KnowledgeService 单例：索引构建 + 检索 + 技能提取
└── skill_synonyms.py           技能同义词/别名映射表（岗位匹配专用）
```

**边界**：后端业务代码（Service 层）只允许通过 `KnowledgeService.instance()` 访问知识；禁止绕过索引直接读 `knowledge/documents/`，禁止在 backend 内重复实现检索。

---

## 2. 知识文档规范

### 2.1 分类与规模（2026-09-07 盘点）

| 分类目录 | 篇数 | 内容 |
|---------|------|------|
| `jobs/` | 54 | 岗位画像（**岗位匹配的数据源**） |
| `skills/` | 46 | 技能学习资料 |
| `companies/` | 39 | 目标企业情况 |
| `interview/` | 34 | 面试题与指南 |
| `projects/` | 21 | 实战项目案例 |
| `market/` | 12 | 就业市场/行业报告 |
| `roadmap/` | 11 | 学习路线 |
| `competition/` | 14 | 竞赛指南 |
| `policies/` | 10 | 就业政策/劳动权益 |
| `resume/` | 7 | 简历写作指南 |
| 根目录 | README、CHANGELOG | 模块说明与变更记录 |

> 篇数为含分类 README 的文件统计；实际知识内容以目录内文档为准。**内容目前由 AI 生成，未经系统人工审核**（技术债，见 01 第 13 章）。

### 2.2 文档格式（YAML Front Matter + Markdown 正文）

```markdown
---
title: Java后端开发工程师
category: jobs
tags: [java, spring, backend]      # tags 是技能匹配的关键数据源
source: jobs.json
date: 2026-07-28
---

# Java后端开发工程师

## 岗位概述
- **岗位ID**: job_002
- **薪资范围**: 10K-18K

## 核心技能要求
- Java
- Spring Boot
- MySQL
```

约定：

1. `doc_id` = 文件名去掉 `.md`（即对外 `job_id`），**文件名即接口暴露的 ID**，须稳定、可读、可作 URL。
2. `tags` 为小写技能标签；`get_skill_requirements()` 优先取 `tags`，缺失时回退解析正文 `## 核心技能要求` 小节的列表项。
3. 正文使用标准 Markdown；检索按全文分词，标题/小节结构影响不大，但保持规范有利于后续升级为分块（chunking）检索。

### 2.3 新增/修改知识文档流程

1. 在对应分类目录新增 `.md`（遵循 2.2 格式），更新该分类 README 与 `knowledge/documents/CHANGELOG.md`。
2. 重启服务（KnowledgeService 单例**启动后懒加载一次**，运行中不会自动感知新文档；`规划/待实现`：热重载）。
3. 验证：`GET /api/jobs?keyword=<新岗位关键词>` 能命中；新岗位文档 `tags` 与 [05 第 6 章](#6-技能同义词映射) 同义词表对齐。
4. 质量要求：技能要求可被 tags 精确表达；薪资/结论类信息标注数据时间；不写无依据承诺。

---

## 3. 当前检索管线（已实现）

```
用户 Query
  │
  ▼
SearchEngine.search(query, top_k, category)          retrieval/search_engine.py
  ├── QueryRewriter.rewrite()      当前=原样返回（预留扩展点）
  ├── KeywordRetriever.retrieve()  调 KeywordIndex.search()
  │      └── KeywordIndex（内存倒排索引，indexes/keyword_index.py）
  │            分词：英文 [a-zA-Z0-9_+#.-]+ 保留 ≥2 字符并小写；
  │                 中文按"单字 + 相邻二元组(bigram)"切分
  │            打分：Σ(查询词在文档中的词频 count)，无 IDF/归一化
  └── 分类过滤（category 精确匹配文档所属目录）
        │
        ▼
[{doc_id, content, score, metadata, filename}, ...]   （score 为词频计数，仅用于排序）
```

已实现能力：全量加载构建索引（懒加载单例）、关键词检索、分类过滤、TopK 排序；`retrieval/context_builder.py`（Token 预算组装）已具备基础实现，**当前业务流程尚未接入**（Prompt 数据来自业务层拼装）。

当前局限（驱动升级路线）：纯词频打分无语义能力；无分块，长文档整篇参与召回与返回；中文按字/bigram 切分，专业词组依赖同义词表弥补。

---

## 4. 后端适配层（`backend/app/knowledge/`）

### 4.1 KnowledgeLoader（`knowledge_loader.py`）

将 `knowledge/` 加入 `sys.path` 后复用其 `MarkdownLoader`/`MarkdownParser`。输出统一文档结构：

```python
{ "doc_id": "Java后端开发工程师", "filename": "Java后端开发工程师.md",
  "metadata": {title, category, tags, source, date}, "content": "正文" }
```

### 4.2 KnowledgeService（`knowledge_service.py`，单例 + 懒加载）

| 方法 | 说明 |
|------|------|
| `instance()` / `reset()` | 单例管理；`reset` 供测试与知识库重建后调用 |
| `search(query, category=None, top_k=10)` | 全库或指定分类检索 |
| `get_document(category, doc_id)` | 单篇文档，键为 `(category, doc_id)` |
| `list_documents(category)` | 分类内全部文档 |
| `list_categories()` | `[{category, count}]`（10 个分类） |
| `get_skill_requirements(job_id)` | 岗位技能要求：tags 优先 → 正文"核心技能要求"回退，统一小写返回 |

加载时机：首次调用任一方法时全量加载 `documents/` 并构建索引（约 248 篇，进程内缓存）。

### 4.3 技能同义词映射（`skill_synonyms.py`）

岗位匹配的准确率关键件：把技能别名归一到标准名（如 `spring boot`→`springboot`、`vue3`→`vue`、`js`→`javascript`、`mybatis-plus`→`mybatis`），按 Java/Python/前端/数据库/移动端/AI 等生态分组，当前约 200+ 条映射。

| 函数 | 用途 |
|------|------|
| `normalize_skill(skill)` | 别名 → 标准名（未知技能原样小写返回） |
| `is_skill_match(a, b)` | 两个技能是否匹配（标准化后比对） |

**维护约定**：岗位文档 `tags` 使用标准名；新增岗位发现新写法时同步补充映射表（单文件字典，直接追加）。

---

## 5. 知识库在业务中的使用点

| 业务 | 使用方式 | 详见 |
|------|---------|------|
| 岗位搜索 `GET /api/jobs` | `search(keyword, category="jobs")` + 分类推断 | 04 第 8.4 节 |
| 岗位匹配 `POST /api/match` | 粗排检索 + `get_skill_requirements()` + 同义词比对 + AI 精排（岗位正文前 500 字入 Prompt） | 04 第 8.4 节 |
| 岗位分类 | 由文档 `tags` → `TAG_CATEGORY_MAP` 推断（前端/后端/AI/…），标题关键词兜底 | `job_match_service.py` |
| 画像/简历/成长 Prompt | 目前由业务层直接拼装学生数据，**尚未注入知识检索上下文**（`规划/待实现`：复用 ContextBuilder 注入岗位要求/学习路线） | 04 第 7.2 节 |

---

## 6. 预留模块现状表（均为接口框架，`规划/待实现`）

| 模块 | 文件 | 状态 | 升级后职责 |
|------|------|------|-----------|
| embedding | `embedding/embedding_model.py` | 预留 | BGE-M3 / Qwen3-Embedding 向量化 |
| vectorstore | `vectorstore/vector_store.py` | 预留 | FAISS / ChromaDB 本地向量库 |
| splitter | `splitter/text_chunker.py` | 预留 | 递归分块（chunk_size=512 / overlap=50 默认值） |
| reranker | `reranker/reranker.py` | 预留 | BGE-Reranker 二阶段精排 |
| graph | `graph/knowledge_graph.py` | 预留 | 技能-岗位知识图谱（Graph RAG） |
| evaluation | `evaluation/metrics.py` + `test_cases.json` | 预留 | RAGAS 风格检索评估回归 |
| 多格式 Loader | `loader/{pdf,docx,excel,json,web}_loader.py` | 预留 | PDF/Word/Excel/网页摄取 |
| workflow | `workflow/*_pipeline.py` | 骨架 | 按场景（job/resume/career…）编排检索→Prompt |
| ingestion | `ingestion/pipeline.py` | 骨架 | Loader→Parser→Splitter→Indexes 全量摄取编排 |

`knowledge/config/*.json`（chunk/embedding/llm/retrieval/knowledge 配置）与 `cache/query_cache.json` 已备好配置位，随对应模块激活启用。

---

## 7. 升级路线（与 knowledge/ARCHITECTURE.md 一致）

```
Keyword Retrieval（当前，已实现）
  → Embedding（BGE-M3 / Qwen3-Embedding）
  → FAISS 本地向量索引
  → Hybrid Search（关键词 + 向量混合召回）
  → Reranker（BGE-Reranker 精排）
  → Milvus（可选，分布式）
  → Graph RAG（知识图谱增强）
```

升级约束：`KnowledgeService` 的方法签名保持不变（业务层零改动），替换其内部实现；每次升级先用 `evaluation/` 的测试用例跑基线对比。

---

## 8. 测试与验收

| 项 | 方式 |
|----|------|
| 检索可用性 | `python test_job_match.py` 中的断言：关键词检索命中、分类统计、技能要求提取（tags 优先） |
| 新增文档验收 | 第 2.3 节流程第 3 步 + `GET /api/jobs/{新doc_id}` 返回完整 Markdown |
| 内容质量 | 技术信息需标来源/时间；由人工抽检（审核清单 `规划/待实现`） |

### 8.1 检索质量指标（分阶段目标）

| 阶段 | 指标 | 目标值 | 测量方式 |
|------|------|--------|---------|
| 当前（关键词检索） | 关键词命中率 | ≥ 70% | 测试用例集（见 8.2）中，期望文档出现在 Top-10 的比例 |
| 升级（向量检索） | 召回率 Recall@10 | ≥ 85% | 同一用例集，升级后跑基线对比（`evaluation/` 激活后） |
| 升级（Hybrid+Rerank） | 命中率 | ≥ 85% | 同上，对比精排前后排序变化 |

> 指标为**阶段性目标值**：每次知识库变更（新增/修改文档、索引调整）后，用 8.2 用例集回归，命中率不低于上一版本；升级检索管线时必须先跑基线再合并（见第 7 章升级约束）。

### 8.2 检索测试用例集（基础集，可扩充）

| 输入 Query | 期望命中（Top-10 内） |
|-----------|----------------------|
| `Python开发岗位需要什么技能` | `jobs/` 内 Python 相关岗位（含技能要求小节） |
| `Java` | `Java后端开发工程师` 等 Java 岗位 |
| `前端 面试` | `interview/` 前端面试题 + `jobs/` 前端岗位 |
| `Redis 学习路线` | `roadmap/` 或 `skills/` 中间件相关文档 |
| `简历 怎么写 项目经历` | `resume/` 简历指南 |

执行方式（服务运行中）：

```bash
curl "http://localhost:8000/api/jobs?keyword=Python&page_size=10"   # 人工核对命中
# 规划/待实现：POST /api/knowledge/search 后可用全分类用例直接回归
```

---

## 9. 规划/待实现 清单

| 项 | 说明 |
|----|------|
| `POST /api/knowledge/search` HTTP 接口 | 草案：`{query, top_k}` → `[{title, content}]`；服务端能力已具备，缺路由层 |
| 向量检索 / Hybrid / Reranker | 见第 6、7 章 |
| 知识热重载 | 文档变更免重启 |
| 检索上下文注入画像/简历/成长 Prompt | 让四个 AI 功能共享知识库 |
| 知识文档人工审核清单与版本化 | 目前仅 CHANGELOG 记录 |
| 缓存激活 | `cache/query_cache.json` 高频查询缓存 |

# 项目工作进度说明

> **文件名称**：PROGRESS.md  
> **文件作用**：记录项目各模块的开发进度、已实现功能与下一步计划。  
> **版本**：v0.2.0  
> **更新**：2026-07-23

---

## 一、总体进度总览

| 模块 | 阶段 | 状态 | 说明 |
|------|------|------|------|
| 用户管理 | 基础实现 | ✅ 已完成 | 学生资料 CRUD、技能/项目整组替换、AI 上下文生成 |
| **岗位匹配** | **基础实现** | ✅ **已完成** | 岗位搜索、详情、技能匹配、历史记录持久化 |
| 知识库 RAG | 基础实现 | ✅ 已完成 | Keyword Index 检索管线（Loader→Parser→Index→Retriever） |
| AI 就业画像 | 骨架 | ⬜ 待实现 | API 路由已预留，服务层待开发 |
| 简历优化 | 骨架 | ⬜ 待实现 | API 路由已预留，服务层待开发 |
| 成长规划 | 骨架 | ⬜ 待实现 | API 路由已预留，服务层待开发 |
| DeepSeek AI 接入 | 骨架 | ⬜ 待实现 | `app/ai/` 仅定义接口框架 |
| 前端页面 | 骨架 | ⬜ 待实现 | views 已建页面结构，业务逻辑待开发 |

> 状态图例：✅ 已完成 · 🔄 开发中 · ⬜ 待实现

---

## 二、岗位匹配模块（本次完成）

### 2.1 模块职责

根据用户技能列表，从岗位知识库中检索并匹配合适岗位，返回：
- 匹配度评分（0-100）
- 命中技能（用户已具备）
- 缺失技能（用户差距）
- 匹配历史持久化与查询

### 2.2 数据流

```
用户技能列表 (POST /api/match)
  │
  ▼
KnowledgeService（知识库检索：Keyword Index）
  │ 返回候选岗位 TopK
  ▼
JobMatchService（技能匹配算法 + 业务分类推断）
  │
  ├──▶ 返回匹配结果
  └──▶ 保存 JobMatchRecord（匹配历史）
          │
          ▼
GET /api/match/{match_id} 查询历史
```

### 2.3 接口清单

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/jobs?keyword=&category=&page=&page_size=` | 岗位列表搜索（关键词/分类/分页） |
| GET | `/api/jobs/{job_id}` | 岗位详情 |
| POST | `/api/match` | 岗位技能匹配（可选 `user_id` 保存历史） |
| GET | `/api/match/{match_id}` | 查询历史匹配记录 |

### 2.4 实现文件

| 层级 | 文件 | 说明 |
|------|------|------|
| API | [app/api/job_match.py](../backend/app/api/job_match.py) | 4 个 REST 接口 |
| Service | [app/services/job_match_service.py](../backend/app/services/job_match_service.py) | 匹配算法 + 业务组装 |
| Schema | [app/schemas/job.py](../backend/app/schemas/job.py) | 请求/响应数据结构 |
| Model | [app/models/job.py](../backend/app/models/job.py) | `JobMatchRecord` 匹配记录表 |
| Knowledge | [app/knowledge/knowledge_service.py](../backend/app/knowledge/knowledge_service.py) | 通用知识检索服务（单例） |
| Knowledge | [app/knowledge/knowledge_loader.py](../backend/app/knowledge/knowledge_loader.py) | Markdown 知识加载适配层 |

### 2.5 架构要点

- **单一数据源**：`KnowledgeService` 是唯一的知识访问入口（单例 + 懒加载），`JobMatchService` 通过它获取岗位数据，消除了重复加载与索引。
- **分层清晰**：API（校验/序列化）→ Service（业务）→ Knowledge（检索）→ documents（Markdown 知识）。
- **可升级**：`KnowledgeService` 底层为 keyword index，未来切换 Embedding/Hybrid 时业务层无需改动。

### 2.6 验证结果

通过 `backend/test_job_match.py`（SQLite 内存库 + TestClient）端到端验证 8 项检查全部通过：

- 岗位搜索（Java 命中 17 个岗位）
- 岗位详情（AI算法工程师，分类推断正确）
- 岗位不存在返回 404（code=3001）
- 技能匹配 + 记录持久化（record_id 正常返回）
- 历史记录查询（完整快照）
- 记录不存在返回 404
- 知识分类统计（10 个分类，岗位 54 篇）
- 技能要求提取（tags 优先策略）

---

## 三、知识库 RAG 模块

### 3.1 当前能力（Keyword Retrieval）

- Markdown 知识文档加载与 YAML Front Matter 解析
- 中英文分词 + 倒排索引构建
- 关键词检索（支持分类过滤、TopK）
- 上下文组装与 Token 估算（供未来 LLM 调用）
- 技能要求提取（tags 优先，正文回退）

### 3.2 升级路线

```
Keyword Retrieval（当前）
  → Embedding（BGE-M3 / Qwen3-Embedding）
    → FAISS
      → Hybrid Search
        → Reranker
```

目录结构已按 RAG 标准预留：`loader/`、`parser/`、`indexes/`、`retrieval/`、`embedding/`、`vectorstore/`、`reranker/` 等，详见 [knowledge/ARCHITECTURE.md](../knowledge/ARCHITECTURE.md)。

---

## 四、验证方式

### 运行岗位匹配测试

```bash
cd backend
$env:PYTHONPATH="d:\大创项目"
python test_job_match.py
```

### 运行用户模块测试

```bash
cd backend
$env:PYTHONPATH="d:\大创项目"
python -m unittest tests.test_user_api
```

---

## 五、下一步计划

| 优先级 | 任务 | 说明 |
|--------|------|------|
| 高 | AI 就业画像分析 | 调用 DeepSeek 分析技能/项目经历，生成画像报告（复用 KnowledgeService 检索技能要求作上下文） |
| 高 | 简历优化 | 基于简历知识库（resume 分类）+ DeepSeek 生成优化建议 |
| 中 | 成长规划 | 基于 roadmap/skills 知识库 + 用户技能差距生成学习计划 |
| 中 | DeepSeekClient 实现 | `app/ai/deepseek_client.py` + `prompts.py` |
| 低 | 前端页面开发 | 对接 `/api/jobs`、`/api/match` 等接口 |
| 低 | 检索升级 | 激活 Embedding + FAISS，切换到语义检索 |

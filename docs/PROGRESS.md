# 项目工作进度说明

> **文件名称**：PROGRESS.md
> **文件作用**：记录项目各模块的开发进度、已实现功能与下一步计划（随代码同步更新）
> **文档版本**：V2.1
> **更新**：2026-09-07（基于代码实测核对，规则与状态定义见 [01-项目开发说明书](./01-项目开发说明书.md)；开发流程与实操指南见 [开发文档](./开发文档.md)）

---

## 一、总体进度总览

| 模块 | 状态 | 说明 |
|------|------|------|
| 后端基础架构（配置/日志/限流/异常/统一响应/CORS） | ✅ 已完成 | `app/config.py`、`app/utils/*` |
| 数据库层（9 张表，SQLite/MySQL 双支持） | ✅ 已完成 | `app/models/`、`init_db.py` |
| 用户管理（资料/技能/项目/竞赛/实习，8 个接口） | ✅ 已完成 | 含 AI 上下文接口 |
| 岗位匹配（搜索/详情/匹配/历史，4 个接口） | ✅ 已完成 | 同义词粗排 + AI 精排 + 记录落库 |
| AI 就业画像（3 个同步接口） | ✅ 已完成 | Mock/Live 双模式 |
| AI 简历优化（3 个同步接口） | ✅ 已完成 | 同上 |
| AI 成长规划（3 个同步接口） | ✅ 已完成 | 同上 |
| SSE 流式响应（3 个接口） | ✅ 已完成 | start/chunk/complete/error 事件，不落库 |
| AI 客户端（重试/Mock/JSON 容错/Token 统计/预算） | ✅ 已完成 | `app/ai/deepseek_client.py` |
| Prompt 外置管理（4 个系统 Prompt） | ✅ 已完成 | `knowledge/prompts/`，改 Prompt 免重启 |
| 知识库 RAG（Keyword 检索管线） | ✅ 已完成 | 248 篇文档、倒排索引、同义词表 |
| Token 用量与成本控制 | ✅ 已完成 | `GET /api/usage`，进程内存统计 |
| 前端（Vue3 骨架） | 🔄 骨架 | 路由/布局/占位页面就绪，页面业务与 API 封装为 TODO |
| 用户认证（注册/登录/JWT） | ⬜ 待实现 | 无代码；`users` 表无密码字段 |
| 知识库向量检索（Embedding/FAISS/Hybrid/Reranker） | ⬜ 待实现 | 仅预留接口框架 |
| 简历上传/导出、AI 对话、知识库 HTTP 检索接口 | ⬜ 待实现 | 无代码 |
| Docker / CI/CD / Alembic 迁移 / Redis | ⬜ 待实现 | 无配置 |

> 状态图例：✅ 已完成 · 🔄 部分实现/骨架 · ⬜ 待实现。接口契约见 [02-API接口文档](./02-API接口文档.md)。

---

## 二、当前版本要点（v1.2.0，代码实测）

1. **核心业务闭环已打通**：用户资料 → AI 画像 → 岗位匹配 → AI 简历优化 → AI 成长规划，均可在 Mock 模式（无 Key）或 live 模式下完整演示。
2. **两阶段岗位匹配**：技能同义词标准化 → 关键词粗排（Top-50）→ live 模式 AI 精排（失败自动降级粗排）。
3. **Prompt 全部外置**：`knowledge/prompts/system_*.md`，修改免重启。
4. **流式体验**：画像/简历/成长支持 SSE 打字机输出。
5. **可观测性**：请求日志 + Request-ID、Token 用量/成本统计接口、滑动窗口限流。

历史版本变更（v1.0/v1.1 的修复记录）见 `backend/PROGRESS.md`。

---

## 三、验证方式

```bash
cd backend
python init_db.py                            # 建表：应为 9 张表
uvicorn main:app --reload                    # 启动（注意：python main.py 不会启动服务）
# 另开终端：
python -m unittest tests.test_user_api -v    # 用户模块集成测试
python test_job_match.py                     # 岗位匹配集成测试（内存 SQLite）
python test_api.py                           # E2E 冒烟（需服务已启动）
```

接口手工验证：http://localhost:8000/docs （Swagger）。

---

## 四、下一步计划

> 任务按优先级分层（P0 必须 / P1 核心 / P2 优化），与 [开发文档 第 13 章](./开发文档.md) 保持一致；版本里程碑（V0.4 智能求职阶段进行中）见 [开发文档 第 12 章](./开发文档.md)。原则：P0 未清零不启动 P2。

| 优先级 | 任务 | 说明 |
|--------|------|------|
| 高（P0） | 前端页面对接 | 按模块实现 5 个页面业务逻辑与 `src/api/*.ts`，消费 [02 文档](./02-API接口文档.md)；AI 功能优先用 SSE 流式接口（消费示例见 [开发文档 第 5.4 节](./开发文档.md)） |
| 高（P0） | 错误码统一 | `ResourceNotFoundError` 3001→2001；AI 异常映射 3001-3004（见 01 第 13 章） |
| 高（P0） | 启动方式修复 | `main.py` 补 `uvicorn.run` 启动块 |
| 中（P1） | 竞赛/实习全路径注入 Prompt | 画像/简历/成长的部分调用路径尚未传入竞赛/实习数据 |
| 中（P1） | 知识检索上下文注入 | 画像/简历/成长 Prompt 接入 KnowledgeService 检索结果 |
| 中（P1） | 知识库 HTTP 检索接口 | `POST /api/knowledge/search`（02 第 11 章），打通后可用于检索质量回归（05 第 8.2 节用例集） |
| 中（P1） | 知识库内容人工审核 | 248 篇 AI 生成文档建立抽检清单 |
| 中（P1） | 简历导出（Markdown/PDF） | — |
| 低（P2） | 认证体系（JWT） | 先加 `users.password_hash` 与 `/api/v1` 前缀迁移；上线前必须完成权限隔离（见 [开发文档 第 7 章](./开发文档.md)） |
| 低（P2） | 向量检索升级 | Keyword → Embedding → FAISS → Hybrid → Reranker（见 [05 文档](./05-RAG知识库设计文档.md)） |
| 低（P2） | 性能压测 | 引入 locust 验证并发 50+ 与接口耗时基线（见 [开发文档 第 10 章](./开发文档.md)） |
| 低（P2） | Docker / Alembic / Redis | 部署与运维基建（见 [06 文档](./06-部署说明.md) 第 9 章） |

# 前端重构审计报告

审计日期：2026-09-25  
审计范围：`frontend/`、`backend/app/api/`、`backend/app/schemas/`、`backend/app/services/`、`knowledge/`

## 1. 审计结论

原前端是 React + Three.js/R3F 的沉浸式作品集式界面，与“高校就业服务系统”的业务定位不一致。已删除旧前端的正式运行入口、3D 场景、WebGL 资源和旧依赖，改为 Vue 3 + TypeScript 的业务工作台。

当前前端已经形成：

```text
登录
  -> 就业档案
  -> AI 就业画像
  -> 岗位匹配
  -> 简历优化
  -> 成长规划
  -> 就业资源
  -> 分析记录
```

所有主要页面都通过 `src/api/` 调用后端，页面不直接读取 `knowledge/` 文件，也不在浏览器端重新实现 RAG、岗位匹配或 AI 评分。

## 2. 后端能力核对

| 能力 | 实际后端接口 | 前端适配 |
|---|---|---|
| 学生档案 | `GET /api/users/{id}` | `stores/user.ts`、`stores/profile.ts` |
| 基本资料 | `PUT /api/users/{id}` | 就业档案“基本信息” |
| 技能 | `PUT /api/users/{id}/skills` | 技能新增、编辑、删除 |
| 项目 | `PUT /api/users/{id}/projects` | 项目经历维护 |
| 竞赛 | `PUT /api/users/{id}/competitions` | 竞赛经历维护 |
| 实习 | `PUT /api/users/{id}/internships` | 实习经历维护 |
| AI 画像 | `POST /api/analysis`、历史接口 | `AnalysisView.vue` |
| 岗位列表 | `GET /api/jobs` | `JobsView.vue` |
| 岗位详情 | `GET /api/jobs/{job_id}` | `JobDetailView.vue` |
| 岗位匹配 | `POST /api/match` | 岗位列表和详情页 |
| 简历优化 | `POST /api/resume`、历史接口 | `ResumeView.vue` |
| 成长规划 | `POST /api/growth`、历史接口 | `GrowthView.vue` |
| 知识检索 | `POST /api/knowledge/search` | `ResourcesView.vue` |
| AI 流式输出 | `/api/stream/*` SSE 接口 | `src/utils/sse.ts` 统一消费 |

## 3. 认证边界

当前后端没有账号密码、JWT 或 OAuth 登录接口，只有按学生档案编号读取用户信息的能力。因此前端采用“真实档案编号验证”作为最小适配：

- 输入编号后调用 `GET /api/users/{id}`；
- 请求成功才建立本地登录状态；
- 编号保存在 `localStorage` 或 `sessionStorage`；
- 路由守卫会在刷新后重新验证档案；
- 不伪造与后端无关的密码认证。

后续如后端增加正式认证接口，只需替换 `src/stores/user.ts` 的登录适配，不需要重做页面结构。

## 4. 数据真实性审计

- 岗位、技能、分析、历史、成长任务和知识资源均优先展示接口返回值。
- 无数据时使用空状态，不填充演示岗位或虚假 AI 评分。
- 后端知识库不可用时，页面展示明确的知识库服务错误，不伪装为正常搜索结果。
- AI 未配置 DeepSeek 时由后端 Mock 模式返回可标识结果；前端展示后端返回的 `is_mock` 状态，不自行制造 AI 内容。

## 5. 运行时发现

在本机浏览器验收时：

- `GET /api/health` 可正常访问；
- 个人档案、分析、简历、成长、历史和设置页面可以加载；
- `/api/jobs` 和 `/api/knowledge/search` 在 PostgreSQL + pgvector 未启动时返回知识库不可用；
- 该问题属于运行环境未完成知识库初始化，不是 Vue 页面错误；
- 前端已将 HTTP 503 / 业务码 `3101` 转为可操作的中文提示。

知识库启动方式见 [knowledge/README.md](../knowledge/README.md) 和 [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md)。

## 6. 竞品与开源架构对照

本次对照采用成熟开源项目的工程分层思路：Vue 负责组件化视图，Vite 负责构建，Pinia 负责类型安全的组合式状态管理，Element Plus 负责一致的后台业务控件，ECharts 只承载真实业务图表。没有复制与本项目业务无关的页面或演示数据。

对照重点：

1. 页面采用稳定的布局壳层，而不是将导航、数据请求和业务表单堆在单个页面组件中。
2. API 请求集中在 `src/api/`，页面只处理交互状态和展示。
3. 图表组件负责初始化、响应式调整和销毁，避免页面切换产生实例泄漏。
4. RAG、向量库、重排和知识文档仍由后端负责，前端只通过正式接口消费结果。

## 7. 需要部署时完成的事项

1. 启动 PostgreSQL + pgvector。
2. 执行知识库 Seed 和索引检查。
3. 使用真实 DeepSeek Key 时切换后端 AI 配置。
4. 将当前“档案编号验证”替换为正式账号认证。

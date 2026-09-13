# 02 API 接口文档

> **文档版本**：V2.3
> **更新日期**：2026-09-13
> **基准版本**：后端 `APP_VERSION=1.2.0`
> **适用范围**：后端全部 HTTP 接口（前后端联调、测试、AI 辅助编码的唯一接口依据）
> **前置阅读**：[01-项目开发说明书](./01-项目开发说明书.md) 第 7 章（统一响应/错误码/命名）、第 10 章（异常处理）

> **V2.3 变更说明（2026-09-13）**：以当前代码（`backend/main.py`、`backend/app/api/*`、`backend/app/schemas/*`、`backend/app/services/*`、`frontend/src/api/*`、`frontend/src/utils/sse.ts`）为唯一事实来源复审全文。修正时间序列化格式（2.5、4.2、6.1、7.1、8.1）、匹配落库与 `total_matches` 语义（5.3）、岗位分页/分类/检索上限坑（5.1）、context 响应结构（4.8）、详情接口 `is_mock` 固定 false（6.2/7.2/8.2）、`X-Request-ID` 沿用规则（2.3）、SSE 错误码与校验约束（9.1）；补齐每个接口的「状态码/是否需要 user_id/前端调用场景」；成长规划请求体字段表（8.1）；联系我们房间无反馈 API 的明确说明（第 10、11 章）。已知偏差（404 资源不存在实际返回 `code=3001`，规范目标 2001）仍如实保留于 2.2 节，未以改文档掩盖代码问题。

本文档**只描述代码中真实存在的接口**。规划中的接口统一放在第 11 章并标注 `规划/待实现`。

---

## 1. 接口总览

服务地址：`http://localhost:8000`，接口前缀 `/api`。交互式文档：`/docs`（Swagger UI）、`/redoc`。

| # | 方法 | 路径 | 功能 | 模块 |
|---|------|------|------|------|
| 1 | GET | `/` | 服务信息 | 系统 |
| 2 | GET | `/api/health` | 健康检查（含 AI 模式） | 系统 |
| 3 | GET | `/api/usage` | AI Token 用量/成本统计 | 系统 |
| 4 | POST | `/api/users` | 创建学生资料（HTTP 201） | 用户管理 |
| 5 | GET | `/api/users/{user_id}` | 获取学生完整资料 | 用户管理 |
| 6 | PUT | `/api/users/{user_id}` | 更新基本资料（部分字段） | 用户管理 |
| 7 | PUT | `/api/users/{user_id}/skills` | 整组替换技能 | 用户管理 |
| 8 | PUT | `/api/users/{user_id}/projects` | 整组替换项目经历 | 用户管理 |
| 9 | PUT | `/api/users/{user_id}/competitions` | 整组替换竞赛经历 | 用户管理 |
| 10 | PUT | `/api/users/{user_id}/internships` | 整组替换实习经历 | 用户管理 |
| 11 | GET | `/api/users/{user_id}/context` | 获取 AI 用学生上下文 | 用户管理 |
| 12 | GET | `/api/jobs` | 岗位列表搜索（关键词/分类/分页） | 岗位匹配 |
| 13 | GET | `/api/jobs/{job_id}` | 岗位详情 | 岗位匹配 |
| 14 | POST | `/api/match` | 岗位技能匹配（粗排+AI精排，落库） | 岗位匹配 |
| 15 | GET | `/api/match/{match_id}` | 查询历史匹配记录 | 岗位匹配 |
| 16 | POST | `/api/analysis` | AI 就业画像分析（落库） | 画像分析 |
| 17 | GET | `/api/analysis/{analysis_id}` | 分析记录详情 | 画像分析 |
| 18 | GET | `/api/analysis/user/{user_id}` | 用户历史分析列表 | 画像分析 |
| 19 | POST | `/api/resume` | AI 简历优化（落库） | 简历优化 |
| 20 | GET | `/api/resume/{optimization_id}` | 优化记录详情 | 简历优化 |
| 21 | GET | `/api/resume/user/{user_id}` | 用户历史优化列表 | 简历优化 |
| 22 | POST | `/api/growth` | AI 成长规划（落库） | 成长规划 |
| 23 | GET | `/api/growth/{plan_id}` | 规划记录详情 | 成长规划 |
| 24 | GET | `/api/growth/user/{user_id}` | 用户历史规划列表 | 成长规划 |
| 25 | POST | `/api/stream/analysis` | 就业画像分析（SSE 流式，不落库） | 流式响应 |
| 26 | POST | `/api/stream/resume` | 简历优化（SSE 流式，不落库） | 流式响应 |
| 27 | POST | `/api/stream/growth` | 成长规划（SSE 流式，不落库） | 流式响应 |

> 认证：**当前所有接口无需认证**（JWT 见第 9 章规划）。

---

## 2. 通用约定

### 2.1 响应结构

所有接口（除 SSE 流式）返回统一三段式，`code=0` 表示成功：

```json
{ "code": 0, "message": "success", "data": { } }
```

字段语义：`code` 业务码（`0` 成功，非 0 失败）；`message` 提示文案；`data` 业务数据（对象/数组/`null`）。SSE 流式接口（第 9 章）例外，返回原始 `text/event-stream` 流。

失败示例（422 参数校验）：

```json
{
  "code": 1001,
  "message": "参数校验失败",
  "data": [ { "loc": ["body", "skills", 0], "msg": "Field required", "type": "missing" } ]
}
```

### 2.2 错误码与 HTTP 状态

错误码表见 [01 第 7.3 节](./01-项目开发说明书.md)。常用场景速查：

| 场景 | HTTP | code |
|------|------|------|
| 成功（查询） | 200 | 0 |
| 成功（创建用户） | 201 | 0 |
| 资源不存在（用户/岗位/记录） | 404 | 3001（**已知偏差**，规范值为 2001，待统一） |
| 请求体缺字段/类型错误 | 422 | 1001 |
| 触发限流 | 429 | 429 |
| AI 服务故障 | 500 | 1（AI 专用码映射为待修复项） |

> **已知偏差说明（勿以文档掩盖代码问题）**：`ResourceNotFoundError`（用户/岗位/匹配记录/AI 记录不存在）当前实际返回 `HTTP 404 + code=3001`，与规范枚举 `NOT_FOUND=2001` 冲突，且与 `AI_SERVICE_ERROR=3001` 撞号（构造于 [exceptions.py](../backend/app/utils/exceptions.py)）。**规范目标为 2001**，修复需改后端代码（当前未修复，本文档如实记录实际行为）。修复前，前端应以 `HTTP 404` 兜底，勿仅依赖 code 区分（前端 `UserContext` 已同时兼容 404/3001/2001 判定“本地档案失效”）。

### 2.3 请求头与限流

- 客户端可携带 `X-Request-ID` 请求头，**服务端优先沿用客户端值**；缺失时才生成 8 位随机 ID。无论来源，最终值均写入**响应头** `X-Request-ID`，用于链路追踪与日志对账。
- 生产环境按 IP 滑动窗口限流（默认 100 次/60 秒，`RATE_LIMIT_*` 配置），超限返回 429。开发环境默认关闭。

### 2.4 Mock 模式标识

未配置 `DEEPSEEK_API_KEY` 时，三个 AI 同步接口（#16/#19/#22）返回的 `data.is_mock = true`，结果为内置动态模拟数据；岗位匹配（#14）的 AI 精排自动跳过，仅返回关键词粗排结果。前端应展示该标识。

### 2.5 时间与 ID

- `created_at`/`updated_at` 由数据库生成（SQLite 存 `YYYY-MM-DD HH:MM:SS`），**API 响应经 `model_dump(mode="json")` 序列化为 ISO 8601 字符串 `YYYY-MM-DDTHH:MM:SS`**（本文示例均为该格式）。前端勿按空格分隔格式解析，勿假设本地时区。
- 记录 ID 为自增整数；`job_id` 为字符串（知识文档文件名，如 `Java后端开发工程师`，URL 中需 URL 编码中文）。

---

## 3. 系统接口

### 3.1 GET / — 服务信息

```json
// data
{ "service": "AI就业竞争力分析助手 API", "version": "1.2.0", "status": "running", "environment": "development" }
```

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：否。**前端调用场景**：前端 `getServiceInfo` 封装已提供，当前组件未接线（多用于调试/版本展示）。

### 3.2 GET /api/health — 健康检查

```json
// data
{
  "status": "healthy",
  "environment": "development",
  "ai_mode": "mock",            // mock | live
  "modules": ["用户管理（含竞赛/实习经历）", "岗位匹配（关键词+AI增强+同义词映射）", "AI就业画像分析", "AI简历优化", "AI成长规划", "AI流式响应（SSE）", "Token用量统计"]
}
```

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：否。**前端调用场景**：`getHealth` 封装已提供，当前组件未接线（用于探测后端可用性与 AI 模式 mock/live）。

### 3.3 GET /api/usage — Token 用量统计

```json
// data（进程内存统计，每日零点自动重置）
{
  "daily_prompt_tokens": 12345,
  "daily_completion_tokens": 6789,
  "daily_total_tokens": 19134,
  "daily_cost_usd": 0.0036,
  "daily_call_count": 42,
  "is_over_budget": false,
  "is_near_limit": false
}
```

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：否。**前端调用场景**：`getUsage` 封装已提供，当前组件未接线（Token 用量看板预留）。**易踩坑**：数据为**进程内存统计**，后端重启即清零。

---

## 4. 用户管理接口

学生资料是聚合根：一个 `User` 聚合 技能/项目/竞赛/实习 四组经历。四组经历均采用**整组替换**语义（PUT 全量覆盖，空数组即清空）。

### 4.1 POST /api/users — 创建学生资料（HTTP 201）

请求体（`UserCreate`，`*` 为必填）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| name | string | * | 1-50 | 姓名 |
| school | string | * | 1-100 | 学校 |
| major | string | * | 1-100 | 专业 |
| grade | string | * | 1-30 | 年级（如"大三"） |
| bio | string |  | ≤5000 | 自我评价 |
| email | string |  | ≤100 | 邮箱 |
| phone | string |  | ≤20 | 手机 |
| target_city | string |  | ≤50 | 意向城市 |
| target_salary | string |  | ≤50 | 期望薪资 |

```json
{ "name": "张三", "school": "某某大学", "major": "计算机科学与技术", "grade": "大三", "bio": "热爱后端开发", "target_city": "杭州" }
```

响应 `data`：创建后的完整资料，结构同 4.2（`UserProfileResponse`）。

**状态码**：HTTP 201 / `code=0`。**是否需要 user_id**：否（响应返回生成的 `id`）。**前端调用场景**：本地无档案时首次创建（`UserContext.createUser`），创建后 `id` 存入 `localStorage` 作为会话用户。

### 4.2 GET /api/users/{user_id} — 获取学生完整资料

响应 `data`（`UserProfileResponse`）：

```json
{
  "id": 1,
  "name": "张三", "school": "某某大学", "major": "计算机科学与技术", "grade": "大三",
  "bio": "热爱后端开发", "email": "", "phone": "", "target_city": "杭州", "target_salary": "",
  "created_at": "2026-08-14T12:00:00", "updated_at": "2026-08-14T12:00:00",
  "skills":   [ { "id": 1, "user_id": 1, "name": "Java", "proficiency": "掌握", "description": "熟悉集合与并发" } ],
  "projects": [ { "id": 1, "user_id": 1, "name": "校园管理系统", "role": "后端开发",
                  "description": "负责接口开发", "tech_stack": ["SpringBoot", "MySQL"],
                  "start_date": "2025-03-01", "end_date": "2025-06-30" } ],
  "competitions": [ { "id": 1, "user_id": 1, "name": "蓝桥杯", "level": "省级", "award": "二等奖",
                       "description": "", "competition_date": "2025-04-15" } ],
  "internships": [ { "id": 1, "user_id": 1, "company": "某科技公司", "position": "后端实习生",
                      "description": "参与订单模块开发", "tech_stack": ["Java", "Redis"],
                      "start_date": "2025-07-01", "end_date": "2025-09-01" } ]
}
```

约束：`skills[].proficiency` 枚举 `了解/熟悉/掌握/精通`；`tech_stack` 为字符串数组。`user_id` 不存在 → 404。

**状态码**：HTTP 200 / `code=0`；不存在 → 404 / `code=3001`（已知偏差）。**是否需要 user_id**：是（路径参数）。**前端调用场景**：应用启动时按 `localStorage` 中的 id 拉取完整资料（`UserContext.fetchProfile`），404/3001/2001 均视为“本地档案已失效”。

### 4.3 PUT /api/users/{user_id} — 更新基本资料

请求体（`UserUpdate`）：同 4.1 的 9 个字段，**全部可选**（仅更新提供的字段）。

```json
{ "target_city": "上海", "bio": "热爱后端与分布式" }
```

响应：更新后的完整资料（同 4.2）。

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：档案编辑“基本信息”保存（`UserContext.saveBasic` → `updateUser`），仅传发生变化的字段。

### 4.4 PUT /api/users/{user_id}/skills — 整组替换技能

```json
{ "skills": [
  { "name": "Java", "proficiency": "掌握", "description": "熟悉集合与并发" },
  { "name": "SpringBoot", "proficiency": "熟悉", "description": "" }
] }
```

约束：数组 ≤100 项；`proficiency` 必须为枚举值。响应 `data`：替换后的技能数组。**覆盖语义，未提交的技能将被删除。**

**状态码**：HTTP 200 / `code=0`；user 不存在 → 404 / `code=3001`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：档案编辑“技能”保存（`UserContext.replaceSkills`），提交完整技能数组（空数组即清空）。

### 4.5 PUT /api/users/{user_id}/projects — 整组替换项目经历

```json
{ "projects": [
  { "name": "校园管理系统", "role": "后端开发", "description": "负责用户/课程模块接口开发",
    "tech_stack": ["SpringBoot", "MySQL"], "start_date": "2025-03-01", "end_date": "2025-06-30" }
] }
```

约束：数组 ≤50 项；`name/role/description` 必填（1-150/1-100/1-10000）；日期格式 `YYYY-MM-DD`。响应 `data`：替换后的项目数组。

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：档案编辑“项目经历”保存（`UserContext.replaceProjects`），整组覆盖提交。

### 4.6 PUT /api/users/{user_id}/competitions — 整组替换竞赛经历

```json
{ "competitions": [
  { "name": "蓝桥杯", "level": "省级", "award": "二等奖", "description": "C/C++ 程序设计组", "competition_date": "2025-04-15" }
] }
```

约束：数组 ≤20 项；`name` 必填；`level` 默认 `校级`、`award` 默认 `参与奖`。响应 `data`：替换后的竞赛数组。

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：档案编辑“竞赛经历”保存（`UserContext.replaceCompetitions`）。

### 4.7 PUT /api/users/{user_id}/internships — 整组替换实习经历

```json
{ "internships": [
  { "company": "某科技公司", "position": "后端实习生", "description": "参与订单模块开发",
    "tech_stack": ["Java", "Redis"], "start_date": "2025-07-01", "end_date": "2025-09-01" }
] }
```

约束：数组 ≤20 项；`company/position` 必填。响应 `data`：替换后的实习数组。

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：档案编辑“实习经历”保存（`UserContext.replaceInternships`）。

> **整组替换易踩坑**：4.4-4.7 均为 **PUT 全量覆盖**（服务层 `user.skills[:] = ...` 等），前端增/删单项须提交整组数组；漏传的旧项会被删除，传空数组 = 清空该组经历。不存在“单项增删”接口。

### 4.8 GET /api/users/{user_id}/context — AI 学生上下文

供 AI 模块/前端获取稳定结构的学生画像（`StudentContextResponse`）。**注意与 4.2 的差异**：上下文结构以 `user_id` 标识用户（**无** `id`），且**不含** `created_at`/`updated_at`，其余字段（name/school/major/grade/bio/email/phone/target_city/target_salary + 四组经历）与 4.2 一致：

```json
// data（结构示意）
{
  "user_id": 1, "name": "张三", "school": "某某大学", "major": "计算机科学与技术", "grade": "大三",
  "bio": "热爱后端开发", "email": "", "phone": "", "target_city": "杭州", "target_salary": "",
  "skills": [ { "id": 1, "user_id": 1, "name": "Java", "proficiency": "掌握", "description": "" } ],
  "projects": [ { "id": 1, "user_id": 1, "name": "校园管理系统", "role": "后端开发", "description": "…",
                  "tech_stack": ["SpringBoot", "MySQL"], "start_date": null, "end_date": null } ],
  "competitions": [], "internships": []
}
```

**状态码**：HTTP 200 / `code=0`；不存在 → 404 / `code=3001`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：AI 功能发起前可选拉取（前端 `getUserContext` 封装已提供，当前组件未接线）；**AI 模块内部取用户数据的标准方式**（开发边界见 [01 第 9.2 节](./01-项目开发说明书.md)）。

---

## 5. 岗位匹配接口

岗位数据来源于知识库 `knowledge/documents/jobs/`（54 篇），**不存数据库**；匹配记录落库。

### 5.1 GET /api/jobs — 岗位列表搜索

查询参数：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| keyword | string | "" | 关键词（如 Java、前端、AI），走知识库检索 |
| category | string | - | 分类过滤：前端/后端/AI/数据/移动端/运维/测试/产品/运营/安全（未命中映射的岗位归为 `其他`） |
| page | int ≥1 | 1 | 页码 |
| page_size | int 1-50 | 20 | 每页数量 |

**分页/检索易踩坑**：

1. 响应 `data` 仅含 `total/items/keyword`，**无 `page/page_size` 回显**，前端页码状态需自维护。
2. 带 `keyword` 时检索经知识库 `top_k=50` 截断，**`total` 最大 50**（不带 keyword 时才是全量 54）；`page` 翻页基于截断后的集合。
3. `category` 为空或“全部”均不过滤；过滤在检索之后执行。

响应 `data`（`JobListResponse`）：

```json
{
  "total": 54,
  "keyword": "Java",
  "items": [
    { "job_id": "Java后端开发工程师", "title": "Java后端开发工程师", "category": "后端",
      "tags": ["java", "spring", "backend"],
      "snippet": "负责后端服务开发与数据库设计 核心技能要求 Java Spring Boot MySQL Redis …" }
  ]
}
```

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：否。**前端调用场景**：岗位匹配房间首屏加载与搜索（`JobMatchContext.fetchJobs`，实传 `page:1, page_size:8`，可选 `keyword/category`），点击“搜索”时重置 `page=1`。

### 5.2 GET /api/jobs/{job_id} — 岗位详情

`job_id` 为知识文档名（中文需 URL 编码），不存在 → 404。响应 `data`（`JobDetail`）：

```json
{
  "job_id": "Java后端开发工程师",
  "title": "Java后端开发工程师",
  "category": "后端",
  "tags": ["java", "spring", "backend"],
  "content": "# Java后端开发工程师\n\n## 岗位概述\n…（完整 Markdown）",
  "metadata": { "title": "Java后端开发工程师", "category": "jobs", "tags": ["java", "spring", "backend"], "source": "jobs.json", "date": "2026-07-28" }
}
```

**状态码**：HTTP 200 / `code=0`；`job_id` 不存在 → 404 / `code=3001`。**是否需要 user_id**：否。**前端调用场景**：岗位墙点击卡片加载详情（`GalleryRoom.getJobDetail`）。**易踩坑**：`job_id` 含中文，URL 必须 `encodeURIComponent(jobId)`（前端 api 封装已内置）。

### 5.3 POST /api/match — 岗位技能匹配

请求体（`JobMatchRequest`）：

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| skills | string[] | *（1-50 项） | - | 用户技能列表 |
| job_category | string |  | null | 目标分类过滤（null/缺省 = 全部分类） |
| top_k | int 1-20 |  | 10 | 返回匹配数量 |
| user_id | int |  | null | **非必填**；传入时写入匹配记录的 `user_id`，并校验用户存在 |

```json
{ "skills": ["Java", "Spring Boot", "MySQL", "Redis", "Git"], "job_category": "后端", "top_k": 3, "user_id": 1 }
```

匹配算法（详见 [04 第 8.4 节](./04-AI模块设计文档.md)）：①技能同义词标准化（`Spring Boot`→`springboot` 等）→ ②关键词粗排取候选 → ③与岗位 tags 逐项比对算分（命中/缺失技能）→ ④live 模式对 Top-K 做 AI 精排（匹配理由/学习建议/面试重点），AI 失败自动保留粗排。

响应 `data`：

```json
{
  "user_skills": ["Java", "Spring Boot", "MySQL", "Redis", "Git"],
  "total_matches": 3,
  "matches": [
    {
      "job_id": "Java后端开发工程师", "title": "Java后端开发工程师", "category": "后端",
      "tags": ["java", "spring", "backend"],
      "match_score": 78.5,
      "matched_skills": ["java", "springboot", "mysql", "redis"],
      "missing_skills": ["消息队列", "分布式"],
      "snippet": "…",
      "match_reason": "掌握 Java 全栈技能，与岗位核心要求高度匹配（live 模式才有）",
      "learning_suggestions": ["学习 RabbitMQ…"], "interview_focus": ["JVM 调优…"]
    }
  ],
  "record_id": 12
}
```

`record_id`：匹配结果非空时**无条件落库**（无论是否传 `user_id`，`user_id` 仅写入记录；未传时为 `null`），返回落库记录 ID；`matches` 为空 → 不落库、不校验 `user_id`、`record_id=null`。

**total_matches 语义**：等于**返回的匹配条数**（`len(matches[:top_k])`，≤ top_k），不是全部候选匹配数。

**状态码**：HTTP 200 / `code=0`；传了不存在的 `user_id` 且 matches 非空 → 404 / `code=3001`。**是否需要 user_id**：否（可选）。**前端调用场景**：岗位匹配房间“开始匹配”（`JobMatchContext.runMatch`，实传 `skills` 取档案技能名、`top_k:8`、`category` 为“全部”时传 `null`、`user_id` 可为 null）。

> **匹配算法补充**：AI 精排只对 Top-K 执行，`match_score` 上限受 `min(ai_score, 粗排分+20)` 约束（live 模式），mock 模式仅粗排、无 `match_reason/learning_suggestions/interview_focus`。

### 5.4 GET /api/match/{match_id} — 查询历史匹配记录

响应 `data`（`JobMatchRecordResponse`）：`id, user_id, skills, job_id, job_title, match_score, matched_skills, missing_skills, matches（完整快照数组，结构同 5.3 matches 项）, created_at`。不存在 → 404。

**状态码**：HTTP 200 / `code=0`；`match_id` 不存在 → 404 / `code=3001`。**是否需要 user_id**：否（记录本身含 `user_id`，未传时为 `null`）。**前端调用场景**：历史匹配结果回放（前端 `getMatchRecord` 封装已提供，当前组件未接线）。**易踩坑**：`matches` 是匹配**当时**的完整快照（含 AI 增强字段），新榜单不影响旧记录；`created_at` 为 ISO 8601 字符串。

---

## 6. AI 就业画像接口

### 6.1 POST /api/analysis — 就业画像分析

请求体（`ProfileAnalysisRequest`）：**二选一** —— 传 `user_id` 使用已保存资料，或直接内联信息。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 二选一 | 使用已保存用户资料 |
| name / school / major / grade | string | 二选一 | 直接传入（各 ≤50/100/100/30） |
| bio | string ≤2000 |  | 自我评价 |
| skills | object[] |  | `[{name, proficiency, description}]` |
| projects | object[] |  | `[{name, role, description, tech_stack}]` |
| target_job | string ≤100 |  | 目标岗位（可选） |

```json
{ "user_id": 1, "target_job": "Java后端开发工程师" }
```

**校验规则（无 user_id 时）**：`name/school/major/grade` 必须全部提供，否则 422 / `code=1001`（错误明细在 `data`）。

**状态码**：HTTP 200 / `code=0`（AI 调用失败时后端兜底 500 / `code=1`）。**是否需要 user_id**：二选一（user_id 或内联信息）。**前端调用场景**：就业画像房间“分析”按钮（`UserContext.startAnalysis`，有档案传 `user_id`，无档案传内联信息，axios 超时 60s）。**易踩坑**：`user_id` 不存在 → 404 / `code=3001`；`is_mock` 仅创建响应有意义（详情接口恒 false）。

响应 `data`（`ProfileAnalysisResponse`）：

```json
{
  "id": 7, "user_id": 1, "target_job": "Java后端开发工程师", "is_mock": false,
  "created_at": "2026-08-14T12:30:00",
  "result": {
    "profile_summary": "该学生具备 Java、SpringBoot 等技术基础…（200字内）",
    "technical_direction": "后端开发",
    "core_advantages": ["掌握 Java 全栈开发", "有完整项目经验"],
    "current_level": "初级开发工程师（校招入门水平）",
    "recommended_directions": [
      { "job_title": "Java后端开发工程师", "match_rate": 75 },
      { "job_title": "全栈开发工程师", "match_rate": 60 }
    ],
    "areas_to_improve": ["Redis/消息队列等中间件经验", "微服务与分布式知识"],
    "comprehensive_score": 68,
    "skill_assessment": {
      "programming_foundation": 75, "framework_usage": 70, "database_skill": 65,
      "engineering_practice": 50, "project_experience": 55
    }
  }
}
```

### 6.2 GET /api/analysis/{analysis_id} — 分析记录详情

响应结构同 6.1。不存在 → 404。

**状态码**：HTTP 200 / `code=0`；不存在 → 404 / `code=3001`。**是否需要 user_id**：否（记录含 `user_id`）。**前端调用场景**：历史记录点击回看（`UserContext.getAnalysis`）。**易踩坑**：详情响应 `is_mock` **恒为 `false`**（服务层固定），与生成时是否 mock 无关，前端勿据此判断历史记录的 mock 性质。

### 6.3 GET /api/analysis/user/{user_id} — 历史分析列表

响应 `data`：数组（按时间倒序），每项 `{ id, user_id, target_job, technical_direction, comprehensive_score, created_at }`。

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：进入应用/画像页时加载历史列表（`UserContext.loadHistory`）。**易踩坑**：`user_id` 不存在时返回**空数组**（不报 404）；无分页参数，一次返回全部历史。

---

## 7. AI 简历优化接口

### 7.1 POST /api/resume — 简历优化

请求体（`ResumeOptimizationRequest`）：`target_job` **必填**。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 二选一 | 使用已保存用户资料 |
| name | string ≤50 | 二选一 | 直接传入时的姓名 |
| target_job | string 1-100 | * | 目标岗位 |
| skills / projects | object[] |  | 同 6.1 |
| original_resume | string ≤10000 |  | 原始简历文本（可选） |

**校验规则（无 user_id 时）**：`name` 必填，否则 422 / `code=1001`。

**状态码**：HTTP 200 / `code=0`（AI 调用失败时后端兜底 500 / `code=1`）。**是否需要 user_id**：二选一（user_id 或 name）。**前端调用场景**：AI 工作台“简历优化”（`UserContext.optimizeResume`，axios 超时 60s）。**易踩坑**：`user_id` 不存在 → 404 / `code=3001`；`is_mock` 仅创建响应有意义（详情接口恒 false）。

响应 `data.result`（`ResumeOptimizationResult`）：

```json
{
  "id": 3, "user_id": 1, "target_job": "Java后端开发工程师", "is_mock": false,
  "created_at": "2026-08-14T12:40:00",
  "result": {
    "optimized_projects": [
      { "project_name": "校园管理系统",
        "original": "负责后端接口开发",
        "optimized": "基于 SpringBoot + MySQL 构建…接口响应时间 <200ms",
        "highlight_tags": ["SpringBoot", "MySQL", "RESTful API"] }
    ],
    "optimized_skills": [ { "original": "Java", "optimized": "熟练掌握 Java…，熟悉集合框架、多线程" } ],
    "overall_suggestions": ["项目描述使用 STAR 法则", "技能区分精通/熟悉/了解层次"],
    "personal_summary": "计算机专业学生，具备…",
    "resume_score": 72
  }
}
```

### 7.2 GET /api/resume/{optimization_id} — 优化记录详情

同 7.1 结构。不存在 → 404。

**状态码**：HTTP 200 / `code=0`；不存在 → 404 / `code=3001`。**是否需要 user_id**：否（记录含 `user_id`）。**前端调用场景**：历史记录点击回看（`UserContext.getResumeOptimization`）。**易踩坑**：详情响应 `is_mock` **恒为 `false`**。

### 7.3 GET /api/resume/user/{user_id} — 历史优化列表

数组项：`{ id, user_id, target_job, resume_score, created_at }`。

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：进入应用/AI 工作台时加载历史（`UserContext.loadStudioHistory`）。**易踩坑**：`user_id` 不存在时返回**空数组**（不报 404）；无分页参数。

---

## 8. AI 成长规划接口

### 8.1 POST /api/growth — 生成成长规划

请求体（`GrowthPlanRequest`）：`target_job` **必填**；可选 `profile_analysis`（object）传入之前的画像结果作为上下文。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 二选一 | 使用已保存用户资料 |
| name | string ≤50 | 二选一 | 直接传入时的姓名 |
| major | string ≤100 | 二选一 | 专业 |
| grade | string ≤30 | 二选一 | 年级 |
| target_job | string 1-100 | * | 目标岗位 |
| skills / projects | object[] |  | 当前技能/项目列表（同 6.1 结构） |
| profile_analysis | object |  | 之前的画像分析结果（可选，作为上下文） |

**校验规则（无 user_id 时）**：`name/major/grade` 必须全部提供，否则 422 / `code=1001`。

**状态码**：HTTP 200 / `code=0`（AI 调用失败时后端兜底 500 / `code=1`）。**是否需要 user_id**：二选一（user_id 或 name/major/grade）。**前端调用场景**：AI 工作台“成长规划”（`UserContext.generatePlan`，axios 超时 60s）。**易踩坑**：`user_id` 不存在 → 404 / `code=3001`；`is_mock` 仅创建响应有意义（详情接口恒 false）。

```json
{ "user_id": 1, "target_job": "AI应用开发工程师" }
```

响应 `data.result`（`GrowthPlanResult`）：

```json
{
  "id": 2, "user_id": 1, "target_job": "AI应用开发工程师", "is_mock": false,
  "created_at": "2026-08-14T12:50:00",
  "result": {
    "current_situation": "具备 Java 基础，能够完成简单项目开发…",
    "ability_gaps": [
      { "skill": "Redis", "importance": "必须", "difficulty": "低", "description": "缓存中间件，企业必备" }
    ],
    "learning_roadmap": [
      { "stage": "第一阶段（1-2个月）", "focus": "夯实基础 + 中间件入门",
        "tasks": ["深入 Java 并发编程", "掌握 Redis 数据结构"], "milestone": "独立完成带缓存的后端项目" }
    ],
    "recommended_projects": [
      { "name": "在线面试题库系统", "description": "支持题目管理、在线答题、自动评分",
        "tech_stack": ["SpringBoot", "Redis", "MySQL", "Vue"], "difficulty": "中级" }
    ],
    "recommended_resources": ["《Redis设计与实现》", "牛客网/LeetCode"],
    "interview_prep_tips": ["准备 2-3 个项目的深度介绍"],
    "expected_timeline": "3-6 个月可达到校招中级水平"
  }
}
```

枚举约定：`importance`：必须/加分；`difficulty`（差距）：低/中/高；`difficulty`（项目）：入门/中级/进阶。

### 8.2 GET /api/growth/{plan_id} — 规划记录详情

同 8.1 结构。不存在 → 404。

**状态码**：HTTP 200 / `code=0`；不存在 → 404 / `code=3001`。**是否需要 user_id**：否（记录含 `user_id`）。**前端调用场景**：历史记录点击回看（`UserContext.getPlan`）。**易踩坑**：详情响应 `is_mock` **恒为 `false`**。

### 8.3 GET /api/growth/user/{user_id} — 历史规划列表

数组项：`{ id, user_id, target_job, expected_timeline, created_at }`。

**状态码**：HTTP 200 / `code=0`。**是否需要 user_id**：是（路径参数）。**前端调用场景**：进入应用/AI 工作台时加载历史（`UserContext.loadStudioHistory`）。**易踩坑**：`user_id` 不存在时返回**空数组**（不报 404）；无分页参数。

---

## 9. SSE 流式接口

### 9.1 协议说明

- 路径（**共 3 个流式接口**）：`POST /api/stream/analysis`、`POST /api/stream/resume`、`POST /api/stream/growth`
- 请求体：**与对应同步接口完全一致**（6.1 / 7.1 / 8.1 的请求体），**校验规则同样生效**（如无 `user_id` 时 analysis 需 `name/school/major/grade`、resume 需 `name`、growth 需 `name/major/grade`，缺失 → HTTP 422）。
- 响应：`Content-Type: text/event-stream`，响应头含 `Cache-Control: no-cache`、`Connection: keep-alive`、`X-Accel-Buffering: no`。
- **不落库（关键差异）**：流式结果**不生成任何历史记录**，刷新后不可回查；需要历史须走同步接口（6.1 / 7.1 / 8.1）。
- `user_id` 不存在 → 连接建立前返回 `HTTP 404`，body 为三段式 `{"code":3001,...}`（当前实现，规范目标 2001，见 2.2）。
- **不返回统一三段式**：响应为 SSE 原始文本流，每帧形如 `event: <类型>\ndata: <JSON>\n\n`。

### 9.2 事件流（4 类事件）

```
event: start
data: {"type":"start","message":"AI分析开始..."}

event: chunk
data: {"type":"chunk","content":"{\\"profile_summary\\": ..."}

event: complete
data: {"type":"complete","result":{...完整JSON...},"message":"分析完成"}

event: error
data: {"type":"error","message":"AI服务异常: ..."}
```

1. `chunk.content` 是文本片段，前端按序拼接；拼接结果应为一段 JSON 文本（`complete.result` 会给出解析后的对象）。
2. 若 AI 输出无法解析为 JSON，`complete` 事件改为 `{"type":"complete","raw_text":"全文","message":"分析完成（非JSON格式）"}`。
3. Mock 模式下同样适用（模拟逐字输出），前端可用流式接口开发联调。

**前端消费方式**：axios 不支持 SSE，须用 `fetch` + `ReadableStream`（POST 方式，`EventSource` 仅支持 GET 不可用）。项目已内置消费助手 `frontend/src/utils/sse.ts` 的 `streamSSE(path, body, handlers)`，自动解析 `event/data` 帧并分发 `onStart/onChunk/onComplete/onError`（参考 [开发文档 5.4 节](./开发文档.md)）。**当前组件未接线**，接线时按该助手契约调用即可。

---

## 10. 联调约定（前端对接须知）

1. **CORS**：后端已允许 `http://localhost:5173` / `http://127.0.0.1:5173`；生产环境通过 `CORS_ORIGINS` 配置。
2. **代理**：`frontend/vite.config.ts` 中的 `/api` 代理**已默认启用**（`target: http://localhost:8000`，`changeOrigin: true`）；开发期前端 `baseURL:"/api"` 的请求经 Vite 代理转发到后端，无需处理跨域。后端 CORS 白名单（5173 来源）仍保留作为兜底：
   ```ts
   server: { port: 5173, proxy: { "/api": { target: "http://localhost:8000", changeOrigin: true } } }
   ```
3. **成功判断**：仅以 `code === 0` 为准；`404/code` 待统一（见 2.2）。
4. **超时**：AI 同步接口耗时 5-30s，axios 默认 `timeout: 30000` 勉强够用；**建议 AI 功能使用 SSE 流式接口**。
5. **SSE 消费**：浏览器端用 `fetch` + ReadableStream（axios 不支持 SSE）；或使用 `EventSource` 时注意其只支持 GET，本项目流式接口为 POST，需 fetch 实现（参考实现见 [开发文档 第 5.4 节](./开发文档.md)）。
6. 中文 `job_id` 在 URL 中必须 `encodeURIComponent`。
7. **联系我们房间无反馈 API**：当前通过 `mailto:` 邮件链接 + `tel:` 电话链接交互（`ContactRoom`），**不存在** `POST /api/feedback` 等反馈类接口。前端不要调用或臆造该接口；后续若规划反馈能力，须先走第 12 章登记流程再开发。

### 10.1 联调流程

```text
后端完成接口
  ↓
Swagger 自测通过（/docs 全路径走通，含错误场景）
  ↓
确认本文档已同步（字段/示例/错误码）
  ↓
前端按本文档对接（不猜字段）
  ↓
发现问题 → 用 X-Request-ID 对账定位责任侧
  ↓
需要改契约 → 走第 12 章变更流程（更新文档 → 通知双方 → 回归）
  ↓
联调问题清零，进入验收
```

### 10.2 Swagger 自测要求（后端提供联调的前提）

- 每个路由函数有中文 docstring（即 Swagger 上的接口描述）；
- 请求/响应模型用 Pydantic 定义并标注字段语义（`Field(description=…)`）；
- Swagger 中可完成该接口的完整操作路径。

### 10.3 常见联调问题速查

| 现象 | 原因 | 处理 |
|------|------|------|
| 跨域报错 | 前端来源不在 CORS 白名单 | 后端修改 `CORS_ORIGINS` 并重启 |
| 岗位详情 404 | 中文 `job_id` 未编码 | 前端 `encodeURIComponent` |
| HTTP 200 但业务失败 | 以 `code===0` 为唯一成功标准 | 见上文第 3 条 |
| 流式无打字机效果 | Nginx/代理缓冲 | Nginx `proxy_buffering off`（06 第 9.1 节） |
| AI 接口超时 | 同步调用 5-30s | 前端改用 SSE 流式接口 |
| 429 | 触发限流 | 开发环境关闭限流或调大阈值 |
| 岗位列表分页错乱 | 响应 data 无 `page/page_size` 回显 | 前端自维护页码；keyword 检索 `total` 上限 50 |
| 档案经历被清空 | 4.4-4.7 为整组替换语义 | 提交完整数组，勿只传变更单项 |
| 历史详情 mock 判断失真 | 详情接口 `is_mock` 恒为 `false` | 以创建时响应为准 |
| 404 但 code=3001 困惑 | `ResourceNotFoundError` 已知偏差（规范 2001） | 前端以 HTTP 404 兜底（UserContext 已兼容） |

---

## 11. 规划接口（`规划/待实现`，暂勿调用）

以下接口来自 [backend/开发规范文档.md](../backend/开发规范文档.md) 草案与路线图，**代码中尚不存在**，实施时须先更新本文档再开发：

| 接口 | 说明 | 依赖 |
|------|------|------|
| `POST /api/v1/auth/register`、`POST /api/v1/auth/login` | 用户注册/登录，返回 JWT（`access_token/token_type/user_id`） | `users` 表增加密码字段；`/api/v1` 前缀迁移 |
| `/api/v1/*` 版本化前缀整体迁移 | 规范草案定义的前缀；当前代码为 `/api` | 全量回归 |
| `POST /api/knowledge/search` | RAG 知识检索（`{query, top_k}` → 文档列表），服务端能力已具备，缺 HTTP 层 | 见 05 文档第 9 章 |
| `POST /api/chat` | AI 对话助手（`{message}` → `{answer}`） | 对话上下文设计 |
| `POST /api/resume/upload`、`/api/files/upload` | 简历文件上传与解析 | 文件存储方案 |
| 简历导出（Markdown/PDF） | 前端导出或后端生成 | — |
| `DELETE` 类接口 | 当前未提供任何删除接口（经历用整组替换清空） | — |

> 说明：联系我们房间当前以 `mailto:` 邮件 / `tel:` 电话链接交互，**无任何反馈类接口**（不存在 `POST /api/feedback`），上表亦不含此类规划。

---

## 12. 接口变更与冻结规则

已实现并发布的接口契约（本文档第 3-9 章所列）视为**冻结**，包含三个层面：

| 冻结对象 | 规则 |
|---------|------|
| URL 路径 | 不得重命名/改层级（如 `/api/jobs/{job_id}` 不可改为 `/api/jobInfo/{id}`） |
| 字段名称 | 请求/响应字段名不得改名（`match_score` 不可改为 `score`） |
| 响应结构 | 必须保持三段式 `{code, message, data}`，不得增删层级 |

### 12.1 允许的向后兼容变更（无需走变更流程）

- 请求新增**可选**字段（带默认值）；
- 响应 `data` 内**新增**字段（前端对未知字段须容忍，不得因此崩溃）；
- 错误提示文案 `message` 调整。

> 兼容变更仍须同步本文档对应章节的示例与字段表。

### 12.2 破坏性变更流程（必须全流程执行）

```text
① 提出变更申请（说明变更原因、影响接口、前后端影响面）
② 更新本文档对应章节 + 后端版本号次版本 +1（01 第 12.1 节）
③ 通知前后端负责人与测试
④ 后端实现 + 前端适配 + 重新联调
⑤ 回归测试（01 第 12.3 节命令全部通过）
⑥ 发布并归档变更记录（commit message 与本文档变更说明呼应）
```

禁止：为适配前端临时返回非规范字段、绕过文档直接改代码后"事后补文档"。

### 12.3 接口新增流程

新接口不冻结，但必须：先在本文档（第 1 章总览 + 对应详情章节）登记契约 → 再写代码 → Swagger 自测 → 联调。完整开发流程见 [开发文档 第 3 章](./开发文档.md)。

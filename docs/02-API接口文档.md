# 02 API 接口文档

> **文档版本**：V2.1
> **更新日期**：2026-09-07
> **基准版本**：后端 `APP_VERSION=1.2.0`
> **适用范围**：后端全部 HTTP 接口（前后端联调、测试、AI 辅助编码的唯一接口依据）
> **前置阅读**：[01-项目开发说明书](./01-项目开发说明书.md) 第 7 章（统一响应/错误码/命名）、第 10 章（异常处理）

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

### 2.3 请求头与限流

- 客户端可携带 `X-Request-ID` 请求头；服务端会生成（8 位）并在**响应头** `X-Request-ID` 返回，用于链路追踪与日志对账。
- 生产环境按 IP 滑动窗口限流（默认 100 次/60 秒，`RATE_LIMIT_*` 配置），超限返回 429。开发环境默认关闭。

### 2.4 Mock 模式标识

未配置 `DEEPSEEK_API_KEY` 时，三个 AI 同步接口（#16/#19/#22）返回的 `data.is_mock = true`，结果为内置动态模拟数据；岗位匹配（#14）的 AI 精排自动跳过，仅返回关键词粗排结果。前端应展示该标识。

### 2.5 时间与 ID

- `created_at`/`updated_at` 由数据库生成，格式 `YYYY-MM-DD HH:MM:SS`（字符串）。
- 记录 ID 为自增整数；`job_id` 为字符串（知识文档文件名，如 `Java后端开发工程师`，URL 中需 URL 编码中文）。

---

## 3. 系统接口

### 3.1 GET / — 服务信息

```json
// data
{ "service": "AI就业竞争力分析助手 API", "version": "1.2.0", "status": "running", "environment": "development" }
```

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

### 4.2 GET /api/users/{user_id} — 获取学生完整资料

响应 `data`（`UserProfileResponse`）：

```json
{
  "id": 1,
  "name": "张三", "school": "某某大学", "major": "计算机科学与技术", "grade": "大三",
  "bio": "热爱后端开发", "email": "", "phone": "", "target_city": "杭州", "target_salary": "",
  "created_at": "2026-08-14 12:00:00", "updated_at": "2026-08-14 12:00:00",
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

### 4.3 PUT /api/users/{user_id} — 更新基本资料

请求体（`UserUpdate`）：同 4.1 的 9 个字段，**全部可选**（仅更新提供的字段）。

```json
{ "target_city": "上海", "bio": "热爱后端与分布式" }
```

响应：更新后的完整资料（同 4.2）。

### 4.4 PUT /api/users/{user_id}/skills — 整组替换技能

```json
{ "skills": [
  { "name": "Java", "proficiency": "掌握", "description": "熟悉集合与并发" },
  { "name": "SpringBoot", "proficiency": "熟悉", "description": "" }
] }
```

约束：数组 ≤100 项；`proficiency` 必须为枚举值。响应 `data`：替换后的技能数组。**覆盖语义，未提交的技能将被删除。**

### 4.5 PUT /api/users/{user_id}/projects — 整组替换项目经历

```json
{ "projects": [
  { "name": "校园管理系统", "role": "后端开发", "description": "负责用户/课程模块接口开发",
    "tech_stack": ["SpringBoot", "MySQL"], "start_date": "2025-03-01", "end_date": "2025-06-30" }
] }
```

约束：数组 ≤50 项；`name/role/description` 必填（1-150/1-100/1-10000）；日期格式 `YYYY-MM-DD`。响应 `data`：替换后的项目数组。

### 4.6 PUT /api/users/{user_id}/competitions — 整组替换竞赛经历

```json
{ "competitions": [
  { "name": "蓝桥杯", "level": "省级", "award": "二等奖", "description": "C/C++ 程序设计组", "competition_date": "2025-04-15" }
] }
```

约束：数组 ≤20 项；`name` 必填；`level` 默认 `校级`、`award` 默认 `参与奖`。响应 `data`：替换后的竞赛数组。

### 4.7 PUT /api/users/{user_id}/internships — 整组替换实习经历

```json
{ "internships": [
  { "company": "某科技公司", "position": "后端实习生", "description": "参与订单模块开发",
    "tech_stack": ["Java", "Redis"], "start_date": "2025-07-01", "end_date": "2025-09-01" }
] }
```

约束：数组 ≤20 项；`company/position` 必填。响应 `data`：替换后的实习数组。

### 4.8 GET /api/users/{user_id}/context — AI 学生上下文

供 AI 模块/前端获取稳定结构的学生画像（`StudentContextResponse`）。字段与 4.2 相同（含 `user_id`），供 Prompt 构建使用。**AI 模块获取用户数据的标准方式**（开发边界见 [01 第 9.2 节](./01-项目开发说明书.md)）。

---

## 5. 岗位匹配接口

岗位数据来源于知识库 `knowledge/documents/jobs/`（54 篇），**不存数据库**；匹配记录落库。

### 5.1 GET /api/jobs — 岗位列表搜索

查询参数：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| keyword | string | "" | 关键词（如 Java、前端、AI），走知识库检索 |
| category | string | - | 分类过滤：前端/后端/AI/数据/移动端/运维/测试/产品/运营/安全 |
| page | int ≥1 | 1 | 页码 |
| page_size | int 1-50 | 20 | 每页数量 |

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

### 5.3 POST /api/match — 岗位技能匹配

请求体（`JobMatchRequest`）：

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| skills | string[] | *（1-50 项） | - | 用户技能列表 |
| job_category | string |  | null | 目标分类过滤 |
| top_k | int 1-20 |  | 10 | 返回匹配数量 |
| user_id | int |  | null | 传入则保存匹配历史 |

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

`record_id`：匹配结果非空时为落库记录 ID，否则为 `null`。`match_score` 0-100（保留 1 位小数）。

### 5.4 GET /api/match/{match_id} — 查询历史匹配记录

响应 `data`（`JobMatchRecordResponse`）：`id, user_id, skills, job_id, job_title, match_score, matched_skills, missing_skills, matches（完整快照数组，结构同 5.3 matches 项）, created_at`。不存在 → 404。

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

响应 `data`（`ProfileAnalysisResponse`）：

```json
{
  "id": 7, "user_id": 1, "target_job": "Java后端开发工程师", "is_mock": false,
  "created_at": "2026-08-14 12:30:00",
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

### 6.3 GET /api/analysis/user/{user_id} — 历史分析列表

响应 `data`：数组（按时间倒序），每项 `{ id, user_id, target_job, technical_direction, comprehensive_score, created_at }`。

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

响应 `data.result`（`ResumeOptimizationResult`）：

```json
{
  "id": 3, "user_id": 1, "target_job": "Java后端开发工程师", "is_mock": false,
  "created_at": "2026-08-14 12:40:00",
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

### 7.3 GET /api/resume/user/{user_id} — 历史优化列表

数组项：`{ id, user_id, target_job, resume_score, created_at }`。

---

## 8. AI 成长规划接口

### 8.1 POST /api/growth — 生成成长规划

请求体（`GrowthPlanRequest`）：`target_job` **必填**；可选 `profile_analysis`（object）传入之前的画像结果作为上下文。

```json
{ "user_id": 1, "target_job": "AI应用开发工程师" }
```

响应 `data.result`（`GrowthPlanResult`）：

```json
{
  "id": 2, "user_id": 1, "target_job": "AI应用开发工程师", "is_mock": false,
  "created_at": "2026-08-14 12:50:00",
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

### 8.3 GET /api/growth/user/{user_id} — 历史规划列表

数组项：`{ id, user_id, target_job, expected_timeline, created_at }`。

---

## 9. SSE 流式接口

### 9.1 协议说明

- 路径：`POST /api/stream/analysis`、`POST /api/stream/resume`、`POST /api/stream/growth`
- 请求体：**与对应同步接口完全一致**（6.1 / 7.1 / 8.1 的请求体）。
- 响应：`Content-Type: text/event-stream`，响应头含 `Cache-Control: no-cache`、`Connection: keep-alive`、`X-Accel-Buffering: no`。
- **不落库**：流式结果不生成历史记录（与同步接口的关键差异）。
- `user_id` 不存在 → 404（连接建立前返回）。

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

---

## 10. 联调约定（前端对接须知）

1. **CORS**：后端已允许 `http://localhost:5173` / `http://127.0.0.1:5173`；生产环境通过 `CORS_ORIGINS` 配置。
2. **代理**：`frontend/vite.config.ts` 中的 `/api` 代理当前被注释（`规划/待实现` 启用）；开发期前端直连 `baseURL:"/api"` 依赖 CORS，或手动启用代理：
   ```ts
   server: { port: 5173, proxy: { "/api": { target: "http://localhost:8000", changeOrigin: true } } }
   ```
3. **成功判断**：仅以 `code === 0` 为准；`404/code` 待统一（见 2.2）。
4. **超时**：AI 同步接口耗时 5-30s，axios 默认 `timeout: 30000` 勉强够用；**建议 AI 功能使用 SSE 流式接口**。
5. **SSE 消费**：浏览器端用 `fetch` + ReadableStream（axios 不支持 SSE）；或使用 `EventSource` 时注意其只支持 GET，本项目流式接口为 POST，需 fetch 实现（参考实现见 [开发文档 第 5.4 节](./开发文档.md)）。
6. 中文 `job_id` 在 URL 中必须 `encodeURIComponent`。

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

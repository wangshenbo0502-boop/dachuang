# AI就业竞争力分析助手

> **项目代号**：AI Job Competitiveness Analyzer
> **版本**：v1.2.0（后端核心闭环已打通；前端为骨架阶段）
> **技术栈**：Vue3 + FastAPI + SQLite/MySQL + DeepSeek API + Markdown 知识库（RAG）

---

## 📋 项目概述

AI就业竞争力分析助手是一款面向**计算机专业大学生**的智能就业分析平台。通过大语言模型（DeepSeek）分析学生的学习经历、项目经历和技术能力，自动生成就业画像、岗位匹配、简历优化和成长规划建议，帮助大学生清晰认知自身竞争力并制定提升路径。

### 核心功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| 用户管理 | 个人信息、技能/项目/竞赛/实习经历录入（注册/登录待实现） | ✅ 已实现 |
| AI就业画像 | 技术能力综合评估、就业画像报告生成 | ✅ 已实现 |
| 岗位匹配 | 知识库检索 + 同义词粗排 + AI 精排，匹配历史持久化 | ✅ 已实现 |
| 简历优化 | AI 优化建议与评分（文件上传/PDF 导出待实现） | ✅ 已实现 |
| 成长规划 | 个性化学习路线、阶段目标、资源推荐 | ✅ 已实现 |
| SSE 流式输出 | 画像/简历/成长三个 AI 功能的打字机效果 | ✅ 已实现 |
| 前端页面 | Vue3 骨架就绪，页面业务逻辑待开发 | 🔄 骨架 |

> **当前阶段**：后端核心业务闭环已打通（Mock/Live 双模式可演示），前端为骨架。各模块进度详见 [docs/PROGRESS.md](./docs/PROGRESS.md)。

---

## 🏗️ 技术架构

### 技术选型

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 前端框架 | Vue 3 | ^3.5 | Composition API + `<script setup>` |
| 构建工具 | Vite | ^5.4 | 极速开发服务器 |
| 语言 | TypeScript | ^5.5 | 类型安全 |
| 路由 | Vue Router | ^4.4 | 前端路由 |
| 状态管理 | Pinia | ^2.2 | 轻量级状态管理 |
| HTTP 客户端 | Axios | ^1.7 | 前后端通信 |
| 后端框架 | FastAPI | 0.115 | 高性能异步 Python 框架 |
| 数据库 | SQLite（开发）/ MySQL 8（生产） | - | 关系型数据库，通过 SQLAlchemy ORM |
| AI 模型 | DeepSeek API | - | 大语言模型推理（未配置 Key 自动 Mock） |
| 知识库 | Markdown + 关键词倒排索引（RAG） | - | 详见 docs/05-RAG知识库设计文档 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue3)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ 就业画像  │  │ 岗位匹配  │  │ 简历优化  │  │ 成长规划  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼──────────────┼──────────────┼──────────────┼─────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                     后端 API (FastAPI)                        │
│                                                               │
│  ┌───────────┐   ┌───────────┐   ┌─────────────────────┐    │
│  │  API 层   │──▶│  服务层   │──▶│  AI 模块 / 知识库   │    │
│  └─────┬─────┘   └─────┬─────┘   └─────────────────────┘    │
│        │                 │                                   │
│        ▼                 ▼                                   │
│  ┌───────────┐   ┌───────────┐                               │
│  │  模型层   │   │ 数据校验层 │                               │
│  └─────┬─────┘   └───────────┘                               │
│        │                                                     │
│  ┌─────▼─────┐                                               │
│  │  MySQL DB │                                               │
│  └───────────┘                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 项目目录结构

```
d:\大创项目\
├── frontend/                 # Vue3 前端项目
│   ├── index.html            # HTML 入口
│   ├── package.json          # 前端依赖与脚本
│   ├── vite.config.ts        # Vite 构建配置
│   ├── tsconfig.json         # TypeScript 配置
│   ├── tsconfig.node.json    # Node 环境 TS 配置
│   └── src/
│       ├── main.ts           # 应用入口
│       ├── App.vue           # 根组件
│       ├── env.d.ts          # 环境类型声明
│       ├── api/              # 后端接口请求封装
│       ├── assets/           # 静态资源（图片/字体等）
│       ├── components/       # 公共可复用组件
│       │   └── common/       # 通用组件（导航/底部/加载）
│       ├── views/            # 页面级组件（5个核心页面）
│       ├── router/           # Vue Router 路由配置
│       ├── store/            # Pinia 状态管理
│       ├── utils/            # 工具方法
│       └── layouts/          # 页面布局组件
│
├── backend/                  # FastAPI 后端项目
│   ├── main.py               # 应用启动入口
│   ├── requirements.txt      # Python 依赖清单
│   └── app/
│       ├── api/              # 接口层（REST API 路由）
│       ├── models/           # 数据模型层（SQLAlchemy ORM）
│       ├── schemas/          # 数据结构层（Pydantic 校验）
│       ├── services/         # 业务服务层（核心逻辑）
│       ├── database/         # 数据库连接与会话管理
│       ├── ai/               # AI 模型调用模块（DeepSeek）
│       ├── knowledge/        # 知识库调用模块
│       └── utils/            # 工具类（响应/异常等）
│
├── knowledge/                # AI 岗位知识库（独立 RAG 模块）
│   ├── documents/            # Markdown 知识文档（jobs/companies/skills/interview 等 10 个分类，248 篇）
│   ├── prompts/              # 外置 AI Prompt 模板（system_*.md，修改免重启）
│   ├── loader/ parser/ indexes/ retrieval/   # 已实现：加载/解析/倒排索引/检索
│   └── embedding/ vectorstore/ reranker/ …   # 向量检索升级预留接口
│
├── docs/                     # 项目文档（六份编号文档体系 + 开发文档 + 进度）
│   ├── 01-项目开发说明书.md … 06-部署说明.md
│   ├── 开发文档.md            # 开发者实操手册（流程/实操指南/联调/安全/Git/性能/版本规划）
│   └── PROGRESS.md           # 工作进度说明
│
├── .gitignore                # Git 忽略规则
└── README.md                 # 项目说明（本文件）
```

---

## 🚀 快速开始

### 前置条件

- **Node.js** >= 18.x（推荐 LTS 版本）
- **npm** >= 9.x 或 **pnpm** / **yarn**
- **Python** >= 3.10
- **MySQL** >= 8.0（后续数据库功能需要）

### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次必做）
npm install

# 启动开发服务器（默认端口 5173）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

开发服务器启动后，访问：`http://localhost:5173`

### 后端开发

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows 激活
.\venv\Scripts\Activate.ps1
# macOS/Linux 激活
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务（默认端口 8000；注意：直接 python main.py 不会启动服务）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后：
- API 文档（Swagger UI）：`http://localhost:8000/docs`
- API 文档（ReDoc）：`http://localhost:8000/redoc`

---

## 🧭 开发指南

### 前端开发规范

- **组件命名**：PascalCase（如 `NavBar.vue`）
- **组合式 API**：全部使用 `<script setup lang="ts">`
- **路径别名**：使用 `@/` 代替 `src/`（如 `@/components/common/NavBar.vue`）
- **API 封装**：所有后端请求统一放在 `src/api/` 目录，按模块分文件
- **状态管理**：全局状态使用 Pinia，放在 `src/store/`，按领域分文件

### 后端开发规范

- **分层架构**：API → Service → Model/Database，职责分层清晰
- **类型提示**：所有函数必须添加完整的类型注解（Type Hints）
- **数据校验**：请求/响应数据统一使用 Pydantic Schema 校验
- **路由注册**：在 `main.py` 中统一注册各模块路由
- **错误处理**：统一使用 `app/utils/exceptions.py` 中的自定义异常

### 五大功能模块对应关系

| 功能模块 | 前端页面 | 前端 API | 后端 API | 后端 Service |
|---------|---------|---------|---------|-------------|
| 用户管理 | - | `api/user.ts` | `api/user.py` | `services/user_service.py` |
| 就业画像 | `views/Profile.vue` | `api/analysis.ts` | `api/analysis.py` | `services/analysis_service.py` |
| 岗位匹配 | `views/JobMatch.vue` | `api/jobMatch.ts` | `api/job_match.py` | `services/job_match_service.py` |
| 简历优化 | `views/Resume.vue` | `api/resume.ts` | `api/resume.py` | `services/resume_service.py` |
| 成长规划 | `views/Growth.vue` | `api/growth.ts` | `api/growth.py` | `services/growth_service.py` |

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [01-项目开发说明书](./docs/01-项目开发说明书.md) | 全局约定、架构、目录、开发边界、测试/版本/验收规则（总纲） |
| [02-API接口文档](./docs/02-API接口文档.md) | 全部已实现接口的请求/响应契约 + 规划接口清单 |
| [03-数据库设计文档](./docs/03-数据库设计文档.md) | 9 张表的字段定义、约束、初始化与变更流程 |
| [04-AI模块设计文档](./docs/04-AI模块设计文档.md) | DeepSeek 客户端、Prompt 工程、Mock、Token 成本、SSE |
| [05-RAG知识库设计文档](./docs/05-RAG知识库设计文档.md) | knowledge 模块检索管线、知识文档规范、升级路线 |
| [06-部署说明](./docs/06-部署说明.md) | 环境变量、启动步骤、生产部署与常见问题 |
| [开发文档](./docs/开发文档.md) | 开发者实操手册：职责边界、标准开发流程、前后端实操指南、联调、安全/日志/Git 规范、性能验收、版本规划 |
| [docs/PROGRESS.md](./docs/PROGRESS.md) | 各模块开发进度、已实现功能与下一步计划 |

> 历史过程文档（architecture / DEVELOPMENT / PROJECT_NAVIGATION / specs）已被上述文档体系取代并移除。

---

## 🛣️ 后续路线图

- [x] **阶段一**：用户管理模块（资料/技能/项目/竞赛/实习录入；注册登录待实现）
- [x] **阶段二**：AI 就业画像模块（技术能力评估 + 报告生成）
- [x] **阶段三**：岗位匹配模块（知识库 + 同义词粗排 + AI 精排）
- [x] **阶段四**：简历优化模块（AI 优化；文件上传/PDF 导出待实现）
- [x] **阶段五**：成长规划模块（学习路线 + 资源推荐）
- [x] **阶段六**：知识库升级（JSON → Markdown + 关键词检索 RAG）
- [ ] **阶段七**：前端页面对接（5 个页面业务逻辑 + API 封装）
- [ ] **阶段八**：认证体系（注册/登录/JWT）+ `/api/v1` 版本化前缀
- [ ] **阶段九**：知识库向量检索升级（Embedding → FAISS → Hybrid → Reranker）
- [ ] **阶段十**：部署基建（Docker / CI/CD / Alembic / Redis）

---

## 📝 当前阶段说明

> ✅ **后端**：核心业务闭环已打通（v1.2.0）。用户管理、岗位匹配、三大 AI 分析、SSE 流式、知识库检索均可用；未配置 DeepSeek Key 时自动运行 Mock 模式，便于开发与演示。
>
> 🔄 **前端**：Vue3 骨架就绪（路由/布局/占位页面），页面业务逻辑与 API 封装为 TODO，尚无可用界面。
>
> ⬜ **未实现**（详见 [docs/PROGRESS.md](./docs/PROGRESS.md)）：注册/登录认证、简历文件上传与导出、AI 对话助手、向量检索、Docker 部署等均为规划项。
>
> 后端开发/接手请先阅读 [docs/01-项目开发说明书](./docs/01-项目开发说明书.md)；接口联调以 [docs/02-API接口文档](./docs/02-API接口文档.md) 为准。

# AI就业竞争力分析助手

> **项目代号**：AI Job Competitiveness Analyzer
> **版本**：后端 v1.2.0 / 前端 v0.2.0（后端核心闭环已打通；前端 3D 沉浸式界面已成形，岗位匹配与档案编辑已接 API）
> **技术栈**：React 19 + Three.js（R3F）+ FastAPI + SQLite/MySQL + DeepSeek API + Markdown 知识库（RAG）

---

## 📋 项目概述

AI就业竞争力分析助手是一款面向**计算机专业大学生**的智能就业分析平台。通过大语言模型（DeepSeek）分析学生的学习经历、项目经历和技术能力，自动生成就业画像、岗位匹配、简历优化和成长规划建议，帮助大学生清晰认知自身竞争力并制定提升路径。

前端为 **React + Three.js 的 3D 沉浸式多房间应用**（纸张手绘美术风格）：从入口大门进入无限走廊，传送至各功能房间；岗位匹配以"晾绳纸卡"3D 形态呈现。

### 核心功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| 用户管理 | 个人信息、技能/项目/竞赛/实习经历录入（注册/登录待实现） | ✅ 后端已实现，前端已接 API |
| AI就业画像 | 技术能力综合评估、就业画像报告生成 | ✅ 后端已实现，前端已接 API（同步接口） |
| 岗位匹配 | 知识库检索 + 同义词粗排 + AI 精排，匹配历史持久化 | ✅ 后端已实现，前端 3D 房间已接 API |
| 简历优化 | AI 优化建议与评分 | ✅ 后端已实现；前端仅 API 封装，UI 规划/待实现 |
| 成长规划 | 个性化学习路线、阶段目标、资源推荐 | ✅ 后端已实现；前端仅 API 封装，UI 规划/待实现 |
| SSE 流式输出 | 画像/简历/成长三个 AI 功能的打字机效果 | ✅ 后端已实现；前端工具已备、UI 未接线 |
| 3D 前端 | React + R3F 沉浸式房间（入口/走廊/About/Studio/岗位匹配/Contact） | 🔄 部分实现（见下文前端状态） |

> **当前阶段**：后端核心业务闭环已打通（Mock/Live 双模式可演示）；前端 3D 架构成形，岗位匹配房间与用户档案编辑已实际调用后端接口。各模块进度详见 [docs/PROGRESS.md](./docs/PROGRESS.md)。

---

## 🏗️ 技术架构

### 技术选型

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 前端框架 | React | ^19.2 | 函数组件 + Hooks，Context 管理全局状态 |
| 3D 渲染 | Three.js + @react-three/fiber + drei | 0.182 / 9.4 / 10.7 | 沉浸式 3D 场景（无 Vue，无 Vue Router/Pinia） |
| 动画 | GSAP + @gsap/react | 3.14 / 2.1 | 卡片翻转、纸张揭示、镜头编排 |
| HTTP 客户端 | Axios | ^1.7 | `baseURL:"/api"`，统一拦截器 + `ApiError` |
| 构建工具 | Vite + TypeScript + Sass | 7.2 / 5.5 / 1.97 | `/api` 代理已启用 |
| 后端框架 | FastAPI + Uvicorn | >=0.100 | Python >= 3.10 |
| 数据库 | SQLite（开发）/ MySQL 8（生产） | - | SQLAlchemy 2.0 ORM，9 张表 |
| AI 模型 | DeepSeek API | - | OpenAI 兼容 SDK；未配置 Key 自动 Mock |
| 知识库 | Markdown + 关键词倒排索引（RAG） | - | 详见 docs/05-RAG知识库设计文档 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│            前端 (React 19 + Three.js, :5173)                  │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐               │
│  │ 3D 房间   │  │ 岗位匹配房间  │  │ 档案编辑  │  GlobalOverlay │
│  │ (R3F)    │  │ (Gallery)    │  │ (Profile) │  + Context 栈  │
│  └────┬─────┘  └──────┬───────┘  └────┬─────┘               │
│       └───────┬───────┴───────┬───────┘                      │
│         axios (baseURL /api，Vite 代理 → :8000)              │
└───────────────┼─────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────────┐
│                     后端 API (FastAPI)                        │
│  ┌───────────┐   ┌───────────┐   ┌─────────────────────┐    │
│  │  API 层   │──▶│  服务层   │──▶│  AI 模块 / 知识库   │    │
│  └─────┬─────┘   └─────┬─────┘   └─────────────────────┘    │
│        ▼                 ▼                                   │
│  ┌───────────┐   ┌───────────┐                               │
│  │ ORM 模型  │   │ Pydantic  │   SSE 流式 (text/event-stream)│
│  └─────┬─────┘   └───────────┘                               │
│  ┌─────▼─────┐                                               │
│  │ SQLite/   │        DeepSeek API (live) / Mock             │
│  │  MySQL    │        knowledge/ (Markdown 倒排索引)         │
│  └───────────┘                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 项目目录结构（实际）

```
d:\dachuang\
├── frontend/                 # React 3D 前端项目
│   ├── index.html            # HTML 入口
│   ├── package.json          # 前端依赖与脚本（version 0.2.0）
│   ├── vite.config.ts        # Vite 构建配置（/api 代理已启用）
│   └── src/
│       ├── main.jsx          # 应用入口（createRoot）
│       ├── App.jsx           # Provider 栈 + Canvas + 全局 UI
│       ├── api/              # 后端接口封装（index/user/analysis/jobMatch/resume/growth/system/types）
│       ├── adapters/         # 数据适配（profile/jobMatch → Overlay 结构）
│       ├── components/
│       │   ├── canvas/       # 3D 层：Experience、corridor（走廊/传送）、rooms（About/Studio/Gallery/Contact）、shaders
│       │   ├── ui/           # NavigationUI、GlobalOverlay、JobMatchPanel、ProfileOverlay、成就等
│       │   └── dom/          # Preloader、PaperTransition
│       ├── context/          # UserContext、JobMatchContext、SceneContext、Audio、Performance、Achievements
│       ├── hooks/            # useScrollCamera、useDocumentMeta、useSanityData 等
│       ├── utils/            # sse.ts（流式消费助手）、audioManager、deviceDetect
│       └── styles/           # SCSS（main.scss + 组件样式）
│
├── backend/                  # FastAPI 后端项目
│   ├── main.py               # 应用入口（无 __main__ 启动块，须用 uvicorn 启动）
│   ├── init_db.py            # 建表脚本
│   ├── requirements.txt      # Python 依赖清单（9 项）
│   ├── .env.example          # 环境变量样例
│   ├── test_api.py           # E2E 冒烟（httpx，需服务已启动）
│   ├── test_job_match.py     # 岗位匹配集成测试（内存 SQLite）
│   ├── tests/                # 用户/AI 契约/SQLite 迁移集成测试
│   ├── PROGRESS.md           # 后端历史进度快照（v1.1，2026-08-14）
│   └── app/
│       ├── config.py         # Settings 配置单例
│       ├── api/              # 接口层（user/job_match/analysis/resume/growth/streaming）
│       ├── models/           # ORM（9 张表）
│       ├── schemas/          # Pydantic v2 请求/响应模型
│       ├── services/         # 业务服务层
│       ├── database/         # 连接与会话管理
│       ├── ai/               # DeepSeek 客户端 + Prompt 模板
│       ├── knowledge/        # 知识库适配层（loader/service/同义词）
│       └── utils/            # 响应/异常/中间件
│
├── knowledge/                # AI 岗位知识库（独立 RAG 模块）
│   ├── documents/            # Markdown 知识文档（10 个分类，248 篇 .md，含分类 README；jobs 54 篇）
│   ├── prompts/              # 外置 AI Prompt（system_*.md 后端加载，修改免重启）
│   ├── loader/ parser/ indexes/ retrieval/   # 已实现：加载/解析/倒排索引/检索
│   └── embedding/ vectorstore/ reranker/ …   # 向量检索升级预留接口
│
├── docs/                     # 项目文档（编号文档体系 + 开发文档 + 进度 + 审计/改造报告）
├── .gitignore                # Git 忽略规则
└── README.md                 # 项目说明（本文件）
```

---

## 🚀 快速开始

### 前置条件

- **Node.js** >= 18.x（推荐 LTS 版本）
- **npm** >= 9.x
- **Python** >= 3.10
- **MySQL** >= 8.0（可选，开发默认 SQLite）
- **DeepSeek API Key**（可选，不配置则运行 Mock 模式）

### 后端启动

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows 激活
.\venv\Scripts\Activate.ps1
# macOS/Linux 激活
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（SQLite，9 张表）
python init_db.py

# 启动服务（默认端口 8000；注意：直接 python main.py 不会启动服务）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后：
- API 文档（Swagger UI）：`http://localhost:8000/docs`
- API 文档（ReDoc）：`http://localhost:8000/redoc`
- 健康检查：`http://localhost:8000/api/health`（返回 `ai_mode: mock|live`）

### 前端启动

```bash
cd frontend

# 安装依赖（首次必做）
npm install

# 启动开发服务器（默认端口 5173，/api 已代理到 8000）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

访问 `http://localhost:5173`：加载完成后从入口进入 3D 走廊，传送至「岗位匹配」房间体验岗位浏览/搜索/技能匹配（需后端已启动）。

---

## 🧭 前端实现状态（重点）

前端为 **React 19 + Three.js（React Three Fiber）沉浸式 3D 应用**，非传统多页面后台。按"已有 UI/场景 → 已接 API → 已实际验证 → 待完善"区分：

| 功能 | UI/场景 | API 对接 | 验证状态 |
|------|---------|---------|---------|
| 3D 场景（入口/走廊/传送/六个房间） | ✅ | - | 开发期可用 |
| 岗位匹配房间：浏览/关键词/分类筛选 | ✅ 晾绳纸卡 | ✅ `GET /api/jobs` | 代码已实现；浏览器端逐项验收未完成（见 docs/岗位匹配房间二次优化报告.md） |
| 岗位匹配房间：岗位详情 | ✅ GlobalOverlay 纸张卡片 | ✅ `GET /api/jobs/{job_id}` | 同上 |
| 岗位匹配房间：技能匹配 | ✅ 匹配分/已匹配/待补充技能 | ✅ `POST /api/match`（依赖档案技能） | 同上 |
| 用户档案编辑（基本资料/技能/项目/竞赛/实习） | ✅ ProfileOverlay | ✅ 用户管理 8 个接口 | 同上 |
| 就业画像分析 + 历史记录 | ✅ | ✅ `POST /api/analysis`、历史接口 | 同上 |
| SSE 打字机效果 | ❌ 无 UI | 工具已实现（`utils/sse.ts`），未接线 | 规划/待实现 |
| 简历优化 / 成长规划 UI | ❌ 无 UI | `api/resume.ts`、`api/growth.ts` 封装已备，未接线 | 规划/待实现 |

岗位匹配房间要点：
- 岗位数据**全部来自后端接口**（后端读知识库），前端不直接读取 Markdown 文件；
- 后端未启动时，Vite 代理返回 HTTP 500/连接失败，前端提示"岗位数据暂不可用，请检查后端服务"，不伪造数据；
- 岗位详情 Markdown 在前端做轻量文本化解析（标题/段落/列表），不渲染 HTML。

---

## 🧪 测试与验证

```bash
cd backend
python -m unittest tests.test_user_api -v      # 用户模块集成测试（内存 SQLite）
python -m unittest tests.test_ai_api_contract -v  # AI 契约/路由清单/SSE 测试
python test_job_match.py                       # 岗位匹配集成测试（内存 SQLite）
# E2E 冒烟（需先启动服务）：
uvicorn main:app --port 8000
python test_api.py
```

前端当前无自动化测试配置（package.json 无 test 脚本）。

**2026-09-13 实测记录**：

- 前端 `npm run build`：✅ 通过（vite 7.3.6，747 模块，6.31s，exit 0；存在单个 chunk >500kB 的体积警告，非错误）；
- 后端测试：**未验证**（本机 `python`/`py` 均不在 PATH，无可用解释器）。

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
| [docs/文档同步审计报告.md](./docs/文档同步审计报告.md) | 2026-09-13 文档与代码一致性审计快照 |
| [docs/岗位匹配房间改造报告.md](./docs/岗位匹配房间改造报告.md)、[岗位匹配房间二次优化报告.md](./docs/岗位匹配房间二次优化报告.md) | 前端岗位匹配房间改造过程记录（历史文档，不作为当前契约） |

---

## 🛣️ 后续路线图

- [x] **阶段一**：用户管理模块（资料/技能/项目/竞赛/实习录入；注册登录待实现）
- [x] **阶段二**：AI 就业画像模块（技术能力评估 + 报告生成）
- [x] **阶段三**：岗位匹配模块（知识库 + 同义词粗排 + AI 精排）
- [x] **阶段四**：简历优化模块（AI 优化；文件上传/PDF 导出待实现）
- [x] **阶段五**：成长规划模块（学习路线 + 资源推荐）
- [x] **阶段六**：知识库升级（JSON → Markdown + 关键词检索 RAG）
- [x] **阶段七（部分）**：前端 3D 架构 + 岗位匹配房间 + 档案编辑/画像分析接 API
- [ ] **阶段七（剩余）**：简历优化/成长规划 UI、SSE 流式 UI 接线、系统状态展示
- [ ] **阶段八**：认证体系（注册/登录/JWT）+ `/api/v1` 版本化前缀
- [ ] **阶段九**：知识库向量检索升级（Embedding → FAISS → Hybrid → Reranker）
- [ ] **阶段十**：部署基建（Docker / CI/CD / Alembic / Redis）

---

## 📝 当前阶段说明

> ✅ **后端**：核心业务闭环已打通（v1.2.0）。用户管理、岗位匹配、三大 AI 分析、SSE 流式、知识库检索均可用；未配置 DeepSeek Key 时自动运行 Mock 模式，便于开发与演示。
>
> 🔄 **前端**：React 19 + Three.js 沉浸式 3D 应用（v0.2.0）。3D 场景与六个房间完整可用；岗位匹配房间（浏览/详情/技能匹配）与用户档案编辑、就业画像分析已实际调用后端接口；简历优化/成长规划 UI 与 SSE 流式 UI 尚未接线（API 封装已备）。浏览器端逐项验收仍在进行（详见 [docs/PROGRESS.md](./docs/PROGRESS.md)）。
>
> ⬜ **未实现**（详见 [docs/PROGRESS.md](./docs/PROGRESS.md)）：注册/登录认证、简历文件上传与导出、AI 对话助手、向量检索、Docker 部署等均为规划项。
>
> 后端开发/接手请先阅读 [docs/01-项目开发说明书](./docs/01-项目开发说明书.md)；接口联调以 [docs/02-API接口文档](./docs/02-API接口文档.md) 为准。

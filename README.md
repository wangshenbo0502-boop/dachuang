# AI就业竞争力分析助手

> **项目代号**：AI Job Competitiveness Analyzer
> **版本**：v0.1.0（基础框架阶段）
> **技术栈**：Vue3 + FastAPI + MySQL + DeepSeek API

---

## 📋 项目概述

AI就业竞争力分析助手是一款面向**计算机专业大学生**的智能就业分析平台。通过大语言模型（DeepSeek）分析学生的学习经历、项目经历和技术能力，自动生成就业画像、岗位匹配、简历优化和成长规划建议，帮助大学生清晰认知自身竞争力并制定提升路径。

### 核心功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| 用户管理 | 注册/登录、个人信息、学习/项目经历录入 | ⬜ 待实现 |
| AI就业画像 | 技术能力综合评估、就业画像报告生成 | ⬜ 待实现 |
| 岗位匹配 | 基于用户画像的岗位智能匹配与推荐 | ⬜ 待实现 |
| 简历优化 | 简历解析、AI 优化建议、多格式导出 | ⬜ 待实现 |
| 成长规划 | 个性化学习路线、阶段目标、资源推荐 | ⬜ 待实现 |

> **当前阶段**：项目处于**基础架构搭建阶段**，已完成目录结构和代码骨架，所有业务功能均为 TODO 状态。

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
| 数据库 | MySQL | - | 关系型数据库，通过 SQLAlchemy ORM |
| AI 模型 | DeepSeek API | - | 大语言模型推理 |
| 知识库 | JSON + Prompt 模板 | - | 后续扩展为 RAG 向量检索 |

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
├── knowledge/                # AI 岗位知识库
│   ├── jobs.json             # 岗位数据
│   ├── skills.json           # 技能数据
│   └── prompts/              # AI Prompt 模板
│       ├── profile_prompt.txt
│       ├── job_prompt.txt
│       └── resume_prompt.txt
│
├── docs/                     # 项目文档
│   └── architecture.md       # 架构设计文档
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
venv\Scripts\activate
# macOS/Linux 激活
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务（默认端口 8000）
python main.py
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

| 文档 | 位置 | 说明 |
|------|------|------|
| 架构设计文档 | [docs/architecture.md](./docs/architecture.md) | 系统架构、技术选型、模块设计详解 |
| 项目导航（Agent用） | [docs/PROJECT_NAVIGATION.md](./docs/PROJECT_NAVIGATION.md) | AI Agent 快速了解项目的入口文档 |
| 开发规范 | [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md) | 代码规范、提交规范、分支策略 |

---

## 🛣️ 后续路线图

- [ ] **阶段一**：用户管理模块（注册/登录/信息录入）
- [ ] **阶段二**：AI 就业画像模块（技术能力评估 + 报告生成）
- [ ] **阶段三**：岗位匹配模块（知识库 + 智能匹配）
- [ ] **阶段四**：简历优化模块（上传/解析/优化/导出）
- [ ] **阶段五**：成长规划模块（学习路线 + 资源推荐）
- [ ] **阶段六**：知识库升级（从 JSON 迁移到 RAG 向量检索）

---

## 📝 当前阶段说明

> ⚠️ **重要提示**：当前项目处于**基础架构搭建阶段**。
>
> - 所有业务逻辑均未实现，仅保留代码骨架和 TODO 注释
> - 数据库未接入，ORM 模型仅为结构占位
> - DeepSeek API 未接入，客户端仅为类框架
> - 前端页面仅为空白骨架，无 UI 样式和交互
>
> 后续开发时，请在对应模块的 TODO 位置实现具体功能。

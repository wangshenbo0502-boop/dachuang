# 项目导航文档（AI Agent 专用）

> **文档目的**：帮助 AI Agent（如 Trae、Cursor、Copilot 等）在首次接触本项目时，快速理解项目全貌、定位关键文件、明确开发规范。
>
> **阅读顺序**：先读本文档 → 再根据任务需要查阅对应模块的详细文档和代码。

---

## 🎯 项目一句话总结

**AI就业竞争力分析助手** = 一个面向计算机专业大学生的 Web 应用，通过大语言模型分析学生的学习/项目/技能数据，输出**就业画像、岗位匹配、简历优化、成长规划**四大核心能力。

- 前端：Vue3 + Vite + TypeScript
- 后端：Python + FastAPI
- 数据库：MySQL
- AI：DeepSeek API（当前未接入，仅预留框架）
- 当前阶段：**基础架构搭建完成，业务逻辑待开发**

---

## 📂 顶层目录速览

项目根目录：`d:\大创项目\`

| 目录/文件 | 一句话说明 | 重要程度 |
|----------|-----------|---------|
| `frontend/` | Vue3 前端项目 | ⭐⭐⭐⭐⭐ |
| `backend/` | FastAPI 后端项目 | ⭐⭐⭐⭐⭐ |
| `knowledge/` | AI 岗位知识库（JSON + Prompt） | ⭐⭐⭐ |
| `docs/` | 项目文档（架构、规范等） | ⭐⭐⭐⭐ |
| `README.md` | 项目总览 + 快速开始 | ⭐⭐⭐⭐⭐ |
| `.gitignore` | Git 忽略规则 | ⭐ |

---

## 🗺️ 前端项目结构导航（`frontend/`）

### 关键入口文件

| 文件路径 | 作用 | 何时需要看它 |
|---------|------|------------|
| `package.json` | 依赖清单 + npm 脚本 | 安装依赖、加新包、运行命令 |
| `vite.config.ts` | Vite 构建配置 | 改端口、配置代理、改构建配置 |
| `tsconfig.json` | TypeScript 配置 | 加路径别名、调编译选项 |
| `src/main.ts` | 应用入口 | 注册新插件、全局初始化逻辑 |
| `src/App.vue` | 根组件 | 全局布局、路由出口位置 |

### 核心目录说明

```
frontend/src/
├── api/          # 📡 后端接口请求封装（按模块分文件）
├── views/        # 🖼️ 页面级组件（一个路由对应一个页面）
├── components/   # 🧩 公共可复用组件
│   └── common/   # 通用组件（导航栏、底部、Loading 等）
├── layouts/      # 📐 页面布局组件（DefaultLayout / AuthLayout）
├── router/       # 🛣️ 路由配置
├── store/        # 📦 Pinia 状态管理（按领域分文件）
├── utils/        # 🔧 工具方法（请求封装、认证工具等）
└── assets/       # 🎨 静态资源（图片、字体、全局样式）
```

### 五大功能模块前端位置

| 功能 | 页面文件 | API 文件 | 状态文件 |
|------|---------|---------|---------|
| 首页 | `views/Home.vue` | - | - |
| 就业画像 | `views/Profile.vue` | `api/analysis.ts` | `store/analysis.ts` |
| 岗位匹配 | `views/JobMatch.vue` | `api/jobMatch.ts` | - |
| 简历优化 | `views/Resume.vue` | `api/resume.ts` | - |
| 成长规划 | `views/Growth.vue` | `api/growth.ts` | - |
| 用户管理 | - | `api/user.ts` | `store/user.ts` |

### 前端开发快速上手

```bash
cd frontend
npm install      # 安装依赖（首次必做）
npm run dev      # 启动开发服务器（端口 5173）
```

---

## 🗺️ 后端项目结构导航（`backend/`）

### 关键入口文件

| 文件路径 | 作用 | 何时需要看它 |
|---------|------|------------|
| `main.py` | FastAPI 应用启动入口 | 注册新路由、加中间件、启动服务 |
| `requirements.txt` | Python 依赖清单 | 加新的 Python 包 |

### 分层架构说明

后端采用经典的**分层架构**，从外到内依次是：

```
API 层（路由） → Service 层（业务逻辑） → Model/Database 层（数据存取）
              ↑
              └── Schema 层（数据校验）
```

```
backend/app/
├── api/          # 🌐 API 接口层（路由定义 + 参数接收 + 返回响应）
├── services/     # ⚙️ 业务服务层（核心业务逻辑，供 API 层调用）
├── models/       # 📊 数据模型层（SQLAlchemy ORM，映射数据库表）
├── schemas/      # ✅ 数据结构层（Pydantic，请求/响应校验）
├── database/     # 🗄️ 数据库层（连接配置、会话管理）
├── ai/           # 🤖 AI 模块（DeepSeek 客户端、Prompt 管理）
├── knowledge/    # 📚 知识库模块（岗位/技能数据加载与检索）
└── utils/        # 🔧 工具类（统一响应格式、自定义异常）
```

### 五大功能模块后端位置

| 功能 | API 文件 | Service 文件 | Model 文件 | Schema 文件 |
|------|---------|-------------|-----------|------------|
| 用户管理 | `api/user.py` | `services/user_service.py` | `models/user.py` | `schemas/user.py` |
| 就业画像 | `api/analysis.py` | `services/analysis_service.py` | `models/analysis.py` | `schemas/analysis.py` |
| 岗位匹配 | `api/job_match.py` | `services/job_match_service.py` | `models/job.py` | `schemas/job.py` |
| 简历优化 | `api/resume.py` | `services/resume_service.py` | `models/resume.py` | `schemas/resume.py` |
| 成长规划 | `api/growth.py` | `services/growth_service.py` | `models/growth.py` | `schemas/growth.py` |

### 后端开发快速上手

```bash
cd backend
pip install -r requirements.txt   # 安装依赖
python main.py                    # 启动服务（端口 8000）
```

启动后访问：
- Swagger UI（交互式 API 文档）：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

---

## 📚 知识库导航（`knowledge/`）

| 文件 | 作用 |
|------|------|
| `jobs.json` | 岗位数据（岗位名、分类、技能要求、薪资范围等）|
| `skills.json` | 技能数据（技能名、分类、熟练度等级等）|
| `prompts/profile_prompt.txt` | 就业画像分析 Prompt 模板 |
| `prompts/job_prompt.txt` | 岗位匹配 Prompt 模板 |
| `prompts/resume_prompt.txt` | 简历优化 Prompt 模板 |

> 注意：当前知识库为 JSON 静态数据，后续将升级为 RAG 向量检索。

---

## 📋 开发规范速查

### 前端规范

1. **组件写法**：全部使用 `<script setup lang="ts">` 组合式 API
2. **路径别名**：用 `@/` 代替 `src/`（已在 vite 和 tsconfig 中配置）
3. **文件命名**：
   - 组件：PascalCase（`NavBar.vue`）
   - 工具/配置：camelCase（`request.ts`）
4. **API 请求**：统一在 `src/api/` 目录封装，不直接在组件里写 axios
5. **状态管理**：全局共享状态放 Pinia Store，组件内部状态用 ref/reactive

### 后端规范

1. **分层调用**：API 层 → Service 层 → Model 层，禁止跨层直接操作
2. **类型注解**：所有函数必须有完整的 Python Type Hints
3. **数据校验**：入参用 Pydantic Schema 校验，不要在业务代码里手动校验
4. **响应格式**：统一用 `utils/response.py` 中的标准响应格式
5. **异常处理**：抛出自定义异常（`utils/exceptions.py`），不直接抛 Exception
6. **路由注册**：新增模块路由后，必须在 `main.py` 中注册

---

## ⚠️ 当前项目状态提醒

**非常重要**：当前项目处于 **v0.1.0 基础架构阶段**，意味着：

- ✅ 目录结构已搭建完成
- ✅ 所有模块的代码骨架已创建
- ❌ **没有任何实际业务逻辑**
- ❌ **数据库未接入**（models 里只有注释占位）
- ❌ **DeepSeek API 未接入**（ai 模块只有类框架）
- ❌ **前端页面只有空白骨架**（没有 UI 和交互）
- ❌ **所有 API 接口都是空路由**（只有 TODO 注释）

**开发任何功能时，都需要从骨架开始填内容**。每个文件顶部都有中文说明注释，代码中有 `# TODO:` 或 `// TODO:` 标记指明待实现的位置。

---

## 🔍 查找代码的快速方式

| 你想找什么 | 去哪里找 |
|-----------|---------|
| 某个页面的代码 | `frontend/src/views/` 下对应的 .vue 文件 |
| 某个接口的定义 | `backend/app/api/` 下对应的模块文件 |
| 某个业务逻辑 | `backend/app/services/` 下对应的服务文件 |
| 数据库表结构 | `backend/app/models/` 下的 ORM 模型 |
| 请求/响应的数据结构 | `backend/app/schemas/` 下的 Pydantic 模型 |
| AI 模型调用 | `backend/app/ai/deepseek_client.py` |
| 知识库数据 | `knowledge/` 目录下的 JSON 文件 |
| Prompt 模板 | `knowledge/prompts/` 目录 |

---

## 📖 更多文档

| 文档 | 位置 | 适合场景 |
|------|------|---------|
| 项目总览（README） | `README.md` | 第一次了解项目、快速开始 |
| 架构设计文档 | `docs/architecture.md` | 需要深入理解架构设计和技术选型时 |
| 本文档（Agent导航） | `docs/PROJECT_NAVIGATION.md` | AI Agent 快速定位文件和模块 |

---

## 💡 给 AI Agent 的工作建议

1. **先读本文档**，再根据任务目标定位到具体目录和文件
2. **修改代码前**，先看一下同目录下其他文件的写法，保持风格一致
3. **新增功能模块时**，确保前后端 5 个层次（API/Service/Model/Schema/前端页面）都同步添加
4. **每个新建文件顶部必须加中文注释**，说明文件名称和作用
5. **未实现的功能用 TODO 注释标记**，不要留空文件

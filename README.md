# 大学生就业竞争力评估与提升系统

> AI 驱动的大学生就业能力分析与成长服务平台

这是一个面向高校学生的就业能力服务系统。系统以学生就业档案为基础，结合 AI 画像、岗位知识库、岗位匹配、简历优化和成长规划，帮助学生完成：

```text
完善档案 -> AI画像 -> 岗位匹配 -> 发现技能缺口 -> 简历优化 -> 成长规划 -> 再评估
```

## 当前版本

- 前端：Vue 3 + TypeScript + Vite
- 后端：FastAPI + SQLAlchemy
- AI：DeepSeek 兼容接口，未配置 Key 时支持后端 Mock 模式
- 知识库：PostgreSQL + pgvector + Hybrid Retrieval + RRF + Reranker
- 图表：ECharts
- UI：Element Plus

当前正式前端已经移除旧 React、Three.js、React Three Fiber、WebGL 和 3D 作品集页面。产品定位是高校就业服务工作台，而不是展示型网站。

## 功能模块

| 模块 | 内容 |
|---|---|
| 首页 | 综合竞争力、档案完整度、能力画像、推荐方向和业务入口 |
| 就业档案 | 基本信息、技能、项目、竞赛、实习经历维护 |
| AI 就业画像 | 真实调用后端 AI/SSE，展示能力雷达、优势和短板 |
| 岗位匹配 | 知识库岗位列表、搜索、技能匹配和岗位详情 |
| 简历优化 | 根据档案和目标岗位生成优化建议 |
| 成长规划 | 生成阶段目标、能力缺口、学习路线和资源建议 |
| 就业资源 | 通过正式 RAG API 检索岗位、技能、简历和面试知识 |
| 分析记录 | 查看画像、简历和成长历史 |
| 系统设置 | 当前学生信息、服务状态和退出登录 |

## 项目结构

```text
├── frontend/                 # Vue 3 前端
│   ├── src/api/              # Axios API 适配层
│   ├── src/components/       # 布局、通用组件和图表
│   ├── src/layouts/          # 主工作台布局
│   ├── src/router/           # 路由与访问守卫
│   ├── src/stores/           # Pinia 状态
│   ├── src/utils/            # SSE、格式化工具
│   ├── src/views/            # 业务页面
│   └── src/styles/           # SCSS 设计基础
├── backend/                  # FastAPI 业务后端
├── knowledge/                # PostgreSQL + pgvector RAG 模块
├── scripts/                  # Seed、索引检查和评测脚本
├── docs/                     # 架构、接口、部署和验收文档
├── docker-compose.yml        # pgvector 知识库数据库
└── .env.example              # 知识库环境变量样例
```

## 环境要求

- Node.js 18+
- npm 9+
- Python 3.10+
- Docker Desktop（岗位匹配和 RAG 资源检索需要）
- DeepSeek API Key（可选，不配置时后端使用 Mock 模式）

## 快速启动

### 1. 初始化知识库数据库

在项目根目录执行：

```powershell
Copy-Item .env.example .env
docker compose up -d knowledge-db
python scripts/seed_knowledge.py
python scripts/check_rag_indexes.py
```

知识库的详细说明见 [knowledge/README.md](knowledge/README.md)。

### 2. 启动后端

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端地址：

- Swagger：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/api/health`

### 3. 启动前端

另开终端：

```powershell
cd frontend
npm install
npm run dev
```

访问 `http://127.0.0.1:5173`。

生产构建：

```powershell
npm run type-check
npm run build
npm run preview
```

## 登录说明

当前后端没有账号密码或 JWT 登录接口，因此前端使用真实的学生档案编号验证身份：

1. 在登录页输入已存在的学生档案编号，例如 `1`。
2. 前端调用 `GET /api/users/{id}`。
3. 后端返回成功后进入系统。
4. 记住登录状态时保存到 `localStorage`，否则保存到 `sessionStorage`。

这不是前端伪造账号体系。后端以后增加正式认证接口时，只需替换登录适配层。

## 知识库说明

正式知识库只使用 PostgreSQL + pgvector，不使用浏览器直读 Markdown，也不在前端实现向量检索。完整链路为：

```text
查询重写 -> PostgreSQL FTS + pgvector HNSW -> RRF 融合 -> 元数据过滤 -> 可选 Reranker -> Context
```

当 PostgreSQL + pgvector 未启动时：

- 岗位列表可能返回知识库服务不可用；
- 就业资源检索会显示知识库服务不可用；
- 前端不会伪造岗位、技能或检索结果；
- AI 业务可以根据后端配置继续使用 Mock 模式。

## 测试与验收

前端：

```powershell
cd frontend
npm run type-check
npm run build
npm audit
```

后端：

```powershell
cd backend
python -m unittest discover -s tests -p "test_*.py" -v
```

知识库：

```powershell
python -m pytest backend/tests/knowledge -q
python scripts/audit_knowledge_content.py
python scripts/check_rag_indexes.py
```

前端重构审计与完成报告：

- [docs/FRONTEND_REBUILD_AUDIT.md](docs/FRONTEND_REBUILD_AUDIT.md)
- [docs/FRONTEND_REBUILD_REPORT.md](docs/FRONTEND_REBUILD_REPORT.md)

## 评审演示路径

1. 启动知识库、后端和前端。
2. 用已有学生档案编号登录。
3. 补充技能和项目经历。
4. 生成 AI 就业画像。
5. 查看岗位匹配与技能缺口。
6. 进行简历优化和成长规划。
7. 返回就业档案更新信息，再次分析。

这条路径直接体现系统的核心价值：从学生真实经历出发，给出可解释、可行动、可持续更新的就业提升建议。

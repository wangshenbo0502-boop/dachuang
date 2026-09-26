# 大学生就业竞争力评估与提升系统

这是一个面向高校学生的就业成长工作台。系统以真实就业档案为基础，提供 AI 求职咨询、档案完善、就业画像、岗位匹配、简历优化、成长规划和就业知识检索。

当前说明更新于 **2026-09-26**。

## 核心流程

```text
AI求职助手 -> 完善并确认档案 -> AI就业画像 -> 岗位匹配 -> 简历优化 -> 成长规划
```

## AI 求职助手

前端只有一个正式入口：`/coach`，统一名称为“AI求职助手”。页面内可切换两种模式：

| 模式 | 能力 |
|---|---|
| 求职咨询 | 开放讨论简历、面试、岗位选择、学习方向和求职困惑，支持流式回答、停止生成、失败重试、复制回答和下一步建议 |
| 完善档案 | 通过不限轮数的自然对话整理个人信息、技能、项目、竞赛和实习；识别结果先进入草稿，用户确认后才写回正式档案 |

会话按当前档案编号保存在当前浏览器中，刷新或重新进入后会恢复上次对话。两种模式分别保存历史；清空对话前会二次确认。旧地址 `/profile/assistant` 会自动跳转到 `/coach?mode=profile`。

档案写回遵循以下原则：

- 同名技能、项目和竞赛会更新原记录，相同公司与岗位的实习会更新原记录。
- 不确定的信息保持为空，不自动补写“掌握”“项目成员”“校级”“参与奖”等事实。
- 整份草稿在一个事务中提交，任一步失败都会整体回滚。
- 新记录缺少数据库必要字段时不会强行保存，页面会提示需要补充的内容。

## 功能模块

| 模块 | 内容 |
|---|---|
| 首页 | 竞争力、档案完整度、能力画像、推荐方向和常用入口 |
| 我的就业档案 | 基本信息、技能、项目、竞赛和实习维护 |
| AI求职助手 | 开放式求职咨询与结构化档案访谈 |
| AI就业画像 | 能力总结、优势短板、推荐方向和能力雷达 |
| 岗位匹配 | 岗位检索、技能匹配、缺口分析和岗位详情 |
| 我的简历 | 简历版本管理、内容优化和预览 |
| 成长规划 | 能力差距、学习路线、项目建议和面试准备 |
| 就业资源 | 基于 PostgreSQL + pgvector 的就业知识检索 |

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Pinia、Element Plus、ECharts
- 后端：FastAPI、SQLAlchemy、Pydantic
- AI：DeepSeek 兼容接口；未配置密钥时使用 Mock 模式
- 知识库：PostgreSQL、pgvector、全文检索、RRF 与可选 Reranker

## 项目结构

```text
frontend/          Vue 前端
backend/           FastAPI 后端、业务服务和测试
knowledge/         RAG 文档、检索、重排和评测模块
scripts/           知识库初始化、索引检查和评测脚本
docs/              当前仍有效的 RAG 架构与评测文档
docker-compose.yml PostgreSQL + pgvector 服务
```

## 环境要求

- Node.js 18+
- npm 9+
- Python 3.10+
- Docker Desktop：岗位知识库和就业资源检索需要
- DeepSeek API Key：可选

## 启动后端

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- API 健康检查：`http://127.0.0.1:8000/api/health`
- Swagger 接口文档：`http://127.0.0.1:8000/docs`

Swagger/OpenAPI 是当前接口契约的唯一来源，不再维护容易过期的手工接口文档。

## 启动前端

```powershell
cd frontend
npm install
npm run dev
```

访问 `http://127.0.0.1:5173`。

## 初始化知识库

在项目根目录执行：

```powershell
Copy-Item .env.example .env
docker compose up -d knowledge-db
python scripts/seed_knowledge.py
python scripts/check_rag_indexes.py
```

详细说明见 `knowledge/README.md`。知识库未启动时，岗位与资源检索可能不可用，但其他配置为 Mock 的 AI 功能仍可运行。

## 测试

前端：

```powershell
cd frontend
npm run type-check
npm run build
```

后端业务测试：

```powershell
cd backend
python -m pytest tests -q
python -m compileall app
```

只运行知识库测试：

```powershell
python -m pytest backend/tests/knowledge -q
```

## 登录与上线说明

当前版本使用已有学生档案编号进入系统，适合本地演示和受控环境。浏览器中的会话记忆也按档案编号隔离。

这不等同于正式身份认证。生产上线前必须增加账号密码、短信验证或校园统一身份认证，并由服务端把登录身份、档案访问权和 AI 用量绑定起来；在完成正式认证前，不应将当前版本直接暴露到公网。

# 大学生就业竞争力评估与提升系统

这是一个面向高校学生的就业成长工作台。系统以真实就业档案为基础，提供 AI 求职咨询、档案完善、就业画像、岗位匹配、简历优化、成长规划和就业知识检索。

当前说明更新于 **2026-10-05**。

## 学生与招聘者角色

登录页同时显示“求职者登录”和“招聘者登录”，选择身份后使用已验证的 QQ 邮箱和密码进入对应工作台。可直接访问 `/login?role=student` 或 `/login?role=recruiter`；刷新保留所选身份，注册及忘记密码也会保留当前身份。账号与所选身份不符时，页面提示切换到正确入口，不建立新的登录会话。

注册页可选择“求职者”或“招聘者”，从登录页进入注册时自动选中对应身份。两种角色沿用 QQ 邮箱验证码注册、密码登录和 JWT 会话。已有学生账号继续作为求职者使用，内部角色值仍为 `student`；未提交身份的旧登录请求保持兼容。

| 角色 | 新增入口 | 功能 |
|---|---|---|
| 招聘者 | `/recruiter` | 企业资料、岗位草稿、发布/下架、岗位编辑、查看收到的简历、处理状态与站内反馈 |
| 学生 | `/recruitment` | 按关键词、城市、方向检索正在招聘的岗位，查看企业资料，选择本人的简历版本进行投递 |
| 学生 | `/recruitment/applications` | 查看投递时的简历快照、招聘反馈与进度，撤回未结束的投递 |

招聘者使用流程：**注册时选择招聘者 → 完善企业名称、联系人、联系邮箱 → 创建并发布岗位 → 在“收到的投递”查看简历并处理**。企业资料由招聘者填写，不代表平台已认证。

学生使用流程：**在“我的简历”保存版本 → 浏览“招聘岗位” → 预览并确认分享简历 → 在“站内投递”查看反馈**。投递只分享选中版本的内容与基本联系方式，保存当时的快照；已采纳的项目表达会一并保留。同一岗位仅可投递一次，撤回后也不能重复投递。

在线岗位需先下架才能编辑；有投递记录的岗位保留历史，只能下架，不能删除。下架后停止展示和接收新投递，已有记录仍可查看。招聘者只能管理自己的岗位和收到的投递，不能访问学生的私有档案、AI对话或分析历史。

本轮新增的站内招聘与原有知识库岗位方向匹配、BOSS 外部投递助手分别保留。站内反馈不会自动发送邮件，也不代表已经安排实际面试。

后端启动时自动新增招聘业务表，并为旧账号补充默认学生角色，迁移不清空原有数据。正常重启后端并重启前端即可使用。设计和实施记录见 [设计书](docs/superpowers/specs/2026-09-30-recruiter-design.md)、[实施计划](docs/superpowers/plans/2026-09-30-recruiter-role.md) 和 [验证报告](docs/招聘者功能验证报告.md)。

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

当前版本已使用 QQ 邮箱验证码注册、Argon2 密码哈希和 JWT 登录，不再通过填写档案编号进入。服务端根据数据库里的账号角色和数据归属校验访问权；退出登录或重置密码会使旧凭证失效。

验证码发送需要配置 `SMTP_HOST`、`SMTP_PORT`、`SMTP_USERNAME`、`SMTP_PASSWORD` 和 `SMTP_FROM`；JWT 需要配置 `JWT_SECRET`。本地开发可使用已有 `DEV_EMAIL_CODE_MODE`，生产环境不启用该模式。招聘者身份通过注册时选择建立，本轮未增加企业资质审核或校园统一身份认证。

独立浏览器验收可在项目根目录运行 `python scripts/verify_recruitment_browser.py`。脚本使用现有 Microsoft Edge、临时端口和临时 SQLite 数据，不修改默认后端代理，也不会写入现有业务数据库；验证码使用验证夹具，不发送真实邮件。

登录身份入口的针对性验收可运行 `python scripts/verify_login_browser.py`，覆盖身份切换、注册预选、密码恢复返回、真实登录与跳转、错选提示和手机布局。结果及截图保存在 `docs/verification/login/`。

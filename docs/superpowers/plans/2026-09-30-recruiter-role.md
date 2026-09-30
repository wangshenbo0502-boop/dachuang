# 招聘者角色与站内招聘 Implementation Plan

> 执行方式：依用户授权，由当前智能体使用 executing-plans 在本会话直接执行，禁止子智能体。先完成本计划与设计自审，再修改业务代码。

**Goal:** 增加完整招聘者角色、企业资料、岗位发布管理与学生站内简历投递闭环。

**Architecture:** Account 角色负责入口与权限，RecruiterProfile 保存企业资料，RecruitmentJob 管理岗位生命周期，RecruitmentApplication 保存投递快照与招聘反馈。新增业务独立于原知识库岗位和 BOSS 投递；前端复用原布局和样式。

**Tech Stack:** Vue 3 / TypeScript / Vite / Pinia / Element Plus；FastAPI / SQLAlchemy / Pydantic；原数据库与 pgvector 保持不变。

## 全局约束

- 以 `docs/superpowers/specs/2026-09-30-recruiter-design.md` 为功能与权限契约。
- 不新增生产依赖、不更换技术栈、不修改全局视觉风格、不调用子智能体。
- 不覆盖用户代码、不清空业务数据库、不修改真实密钥；测试设置 `DATABASE_URL=sqlite://`，浏览器验证使用独立临时数据库。
- 留存可编辑源代码、计划和验证报告；不推送、不部署。当前工作区初始干净，在当前目录建立 `codex/recruiter-role` 分支实施。

## Task 1：身份、角色与兼容迁移

文件：修改 `backend/app/models/account.py`、`backend/app/schemas/auth.py`、`backend/app/api/auth.py`、`backend/app/auth/dependencies.py`、`backend/app/database/bootstrap.py`；新增 `backend/tests/test_recruitment_api.py`。

接口：注册增加 `role: Literal['student','recruiter']='student'`；身份返回 `role`、`name`、现有 `profile_id` 和邮箱；`get_current_recruiter` 返回 Account；`get_current_user` 只允许 student。

- [x] 先编写默认角色、招聘者注册、禁止角色篡改和跨角色访问的真实 API 测试，观察新功能缺失的失败。
- [x] Account 增加 `role VARCHAR(20) NOT NULL DEFAULT 'student'`；兼容迁移同定义，反复执行无重复修改。
- [x] 注册保留验证码与密码流程，根据角色使用默认身份名；登录/me 统一返回真实角色。
- [x] 增加学生与招聘者角色依赖，保留原归属校验。
- [x] 编写旧 accounts 表保留原行与角色默认值的迁移测试。

## Task 2：岗位管理、企业资料与投递接口

文件：新增 `backend/app/models/recruitment.py`、`backend/app/schemas/recruitment.py`、`backend/app/services/recruitment_service.py`、`backend/app/api/recruitment.py`；修改 `backend/app/models/__init__.py`、`backend/main.py`。

接口（沿用 `{code,message,data}`）：

| 方法 | 路径 | 输入与结果 |
|---|---|---|
| GET/PUT | `/api/recruiter/profile` | 当前企业资料 / 保存企业资料 |
| GET/POST | `/api/recruiter/jobs` | 本人岗位分页列表 / 新建草稿 |
| GET/PUT/DELETE | `/api/recruiter/jobs/{id}` | 本人详情 / 编辑非在线岗位 / 删除无投递的非在线岗位 |
| POST | `/api/recruiter/jobs/{id}/status` | `{status:'published'\|'closed'}` |
| GET | `/api/recruiter/applications` | 本人岗位收到的投递，支持岗位、状态分页 |
| PATCH | `/api/recruiter/applications/{id}` | `{status,feedback}`，状态遵循状态机 |
| GET | `/api/recruitment/jobs` | 招聘中岗位，keyword/category/city/page/page_size |
| GET | `/api/recruitment/jobs/{id}` | 招聘中岗位与企业资料 |
| POST | `/api/recruitment/jobs/{id}/apply` | `{resume_id,note}`，返回已保存投递 |
| GET | `/api/recruitment/applications` | 学生本人投递分页列表 |
| POST | `/api/recruitment/applications/{id}/withdraw` | 撤回本人未结束投递 |

数据：岗位 `recruiter_id` 来自登录账号；投递 `student_id` 来自账号，简历必须同时归属于学生 profile；`UNIQUE(job_id,student_id)`；快照保存用户实际选中的内容。分页统一 `{items,total,page,page_size}`。投递状态更新使用当前状态条件更新，冲突返回 409。

- [x] 添加岗位发布校验、生命周期、重复投递、简历归属、快照稳定和跨招聘者拒绝的测试。
- [x] 实现三张表、严格 Pydantic 输入（拒绝额外字段）、服务层验证与状态流转。
- [x] 注册新路由；发布/投递按事务保存，捕获唯一约束冲突。
- [x] 新建岗位默认草稿，在线编辑或有投递删除返回 409；下架后学生详情 404；已保存投递保留快照。

## Task 3：前端账号和导航

文件：修改 `frontend/src/stores/auth.ts`、`frontend/src/utils/authSession.ts`、`frontend/src/router/index.ts`、`frontend/src/components/layout/AppSidebar.vue`、`AppHeader.vue`、`frontend/src/views/login/{RegisterView,LoginView}.vue`、`frontend/src/views/settings/SettingsView.vue`。

- [x] AccountIdentity 增加 role/name；招聘者建立会话时不请求学生档案。hydrate 返回身份，学生 user 保持原有 StudentProfile 契约。
- [x] 注册提供学生/招聘者选择；登录和刷新根据 role 默认进入 `/dashboard` 或 `/recruiter`；禁止错误角色重定向。
- [x] 新增招聘者路由 `/recruiter`、`/recruiter/jobs/new`、`/recruiter/jobs/:id/edit`；学生路由 `/recruitment`、`/recruitment/jobs/:id`、`/recruitment/applications`。
- [x] 根据角色生成侧栏和顶部文案；招聘者不显示学生 AI 会话历史，系统设置显示角色和账号。

## Task 4：招聘者与学生业务页面

文件：新增 `frontend/src/api/recruitment.ts`、`frontend/src/types/recruitment.ts`、`frontend/src/utils/recruitment.ts`、`frontend/src/views/recruiter/{RecruiterView,JobEditorView}.vue`、`frontend/src/views/recruitment/{RecruitmentView,RecruitmentDetailView,MyApplicationsView}.vue`、`frontend/src/components/recruitment/ResumeSnapshot.vue`。

- [x] 类型与 API 路径逐项匹配 Task 2；状态中文文案和可流转状态共用工具函数。
- [x] 招聘工作台有岗位管理、收到的投递、企业资料三个页签；真实数量、筛选、分页和独立错误态。
- [x] 岗位编辑器区分新建/编辑，保存草稿后可发布；离开未保存页面提示，失败保留表单。
- [x] 学生招聘列表支持搜索与分页；详情显示完整职责要求和企业信息，使用本人简历选择框明确确认分享。
- [x] 招聘者简历详情显示快照，允许合法状态与反馈保存；学生查看投递反馈与撤回。对不可操作状态禁用按钮。
- [x] 复用当前绿色变量、页面标题、卡片、表格、空态和按钮样式，只新增局部 responsive CSS。

## Task 5：验证与交付

文件：更新 `README.md`，新增 `docs/招聘者功能验证报告.md` 和 `scripts/verify_recruitment_browser.py`。

- [x] 在独立库运行 `python -m pytest tests/test_recruitment_api.py tests/test_sqlite_user_migration.py -q`，预期新功能和迁移全部通过。
- [x] 运行 `python -m pytest tests -q`（既有知识库测试本身使用测试隔离），输出真实计数；如有既有失败，记录并判断是否相关。
- [x] 前端按锁文件 `npm.cmd ci`，执行 `npm.cmd run build`（包含完整类型检查），不改变 manifest/lockfile。
- [x] 使用独立本地端口和临时数据库启动本轮后端与前端，通过 Playwright 实际完成企业填写、发布、学生投递、招聘者反馈、学生撤回/查看以及角色直达拦截，保存桌面与移动端截图。浏览器数据为验证专用，不写入用户真实业务库。
- [x] 核对 `git diff --check` 与变更清单，逐项对照设计验收，计划标记完成；报告功能使用方法、测试数量、实际限制和未执行的外部服务检查。

## 执行完成记录

2026-09-30：计划逐项完成，后端最终 56 项通过、1 项跳过、17 个子测试通过，前端完整构建通过，浏览器 9 组检查通过，桌面与移动截图已核对。详细结果见 `docs/招聘者功能验证报告.md`。未连接真实 SMTP、AI、BOSS 或 pgvector 服务；未提交、推送或部署。

# 登录身份入口 Implementation Plan

> **For agentic workers:** 使用 executing-plans 在当前会话直接执行；本次不使用子智能体。

**Goal:** 在登录页明确呈现求职者和招聘者入口，并让认证及相关导航遵循所选身份。

**Architecture:** 同一登录页共享表单，URL query 保存身份，既有账号角色决定权限。后端登录接口接受可选角色，在签发 token 前检查身份一致性。

**Tech Stack:** 现有 Vue 3、TypeScript、Pinia、Element Plus、FastAPI、Pydantic、pytest、Playwright。

## Global Constraints

- 保留现有技术栈、登录页视觉语言和 QQ 邮箱认证。
- 内部角色继续使用 `student` 与 `recruiter`；不迁移数据库。
- 保持 `safeInternalRedirect` 的角色与内部地址校验。
- 直接完成当前授权任务，不使用子智能体。登录功能验收后，用户已于 2026-10-05 授权清理旧文件并上传 GitHub。
- 所有验证使用隔离数据及本次启动的进程。

## Task 1: 登录请求的身份校验

**Files:** `backend/app/schemas/auth.py`、`backend/app/api/auth.py`、`backend/tests/test_auth_api.py`。

**Interfaces:** `LoginRequest.role: Literal["student", "recruiter"] | None = None`；保持原登录响应结构。

- [x] 为正确身份、错选身份、错误密码优先、非法角色及未传角色的招聘者登录增加回归测试。
- [x] 执行 `python -m pytest tests/test_auth_api.py -q -k 'selected_role or legacy_recruiter or invalid_role'`，确认新身份约束测试失败。
- [x] 在密码及账号状态验证之后、`last_login_at` 写入之前加入：

```python
if body.role is not None and body.role != account.role:
    label = "招聘者" if account.role == "recruiter" else "求职者"
    raise AppException(f"该账号是{label}账号，请选择“{label}登录”", code=5211, status_code=403)
```

- [x] 执行 `python -m pytest tests/test_auth_api.py tests/test_recruitment_api.py -q`，确认认证和现有招聘权限通过。

## Task 2: 登录入口及身份导航

**Files:** `frontend/src/views/login/LoginView.vue`、`RegisterView.vue`、`ForgotPasswordView.vue`、`frontend/src/utils/authSession.ts`、`frontend/src/router/index.ts`、`frontend/src/api/index.ts`、`frontend/src/stores/auth.ts`。

**Interfaces:** `AccountRole = "student" | "recruiter"`；`resolveAuthRole(value: unknown, redirect?: unknown): AccountRole`；`auth.login(email: string, password: string, role?: AccountRole)`。

- [x] 登录请求传递角色：`api.authLogin({ email, password, role })`。
- [x] 用同页原生 button 卡片展示两个入口，使用 `aria-pressed` 表达选中状态；选中身份改变 URL query，登录时禁用切换。
- [x] 根据身份展示品牌区、表单标题、工作台登录按钮及注册文案。
- [x] 注册初值与返回地址使用所选角色；忘记密码页面保留 query；招聘者受保护地址自动打开招聘者入口。
- [x] 移除密码框的额外 Enter 提交处理，统一使用表单 submit，提交函数防止重复调用。
- [x] 执行 `npm.cmd run build`，确认类型校验和生产构建成功。

## Task 3: 浏览器验收与使用说明

**Files:** `scripts/verify_login_browser.py`、`scripts/verify_recruitment_browser.py`、`README.md`、`docs/verification/login/`。

- [x] 更新既有招聘验收中的登录入口定位器。
- [x] 使用现有验收辅助函数，新增针对登录的真实浏览器脚本，临时创建求职者及招聘者验证账号。
- [x] 检查默认入口、切换与刷新、注册预选与返回、密码恢复导航、错选身份无 token、两类登录与安全跳转、单次 Enter 提交、手机可见性和无横向溢出。
- [x] 执行 `python scripts/verify_login_browser.py`；查看截图和结果 JSON，修复实际发现的问题。
- [x] 更新 README，记录两个入口、错选提示和兼容方式；执行 `git diff --check` 并审阅最终改动。

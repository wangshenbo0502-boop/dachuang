# 开发规范

> **文件名称**：DEVELOPMENT.md
> **适用范围**：本项目所有前端和后端开发人员、AI Agent
> **版本**：v0.1.0

---

## 1. 通用规范

### 1.1 文件顶部注释

**所有代码文件（.py / .ts / .vue / .js）顶部必须添加中文注释**，格式如下：

**Python 文件：**
```python
"""
文件名称：xxx.py
文件作用：一句话说明文件是做什么的。
当前阶段仅搭建结构，具体业务逻辑后续实现。
"""
```

**Vue 文件：**
```vue
<!--
  文件名称：Xxx.vue
  文件作用：一句话说明组件/页面是做什么的。
  当前阶段仅建立结构，具体UI和业务逻辑后续开发。
-->
```

**TypeScript / JavaScript 文件：**
```typescript
/**
 * 文件名称：xxx.ts
 * 文件作用：一句话说明文件是做什么的。
 */
```

### 1.2 TODO 注释

未实现的功能必须用 `TODO:` 注释标记：

```python
# TODO: 实现用户注册逻辑
def register():
    pass
```

```typescript
// TODO: 实现登录接口调用
export function login() {}
```

---

## 2. 前端开发规范

### 2.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 (.vue) | PascalCase | `NavBar.vue`, `UserProfile.vue` |
| 工具/配置/API 文件 | camelCase | `request.ts`, `user.ts` |
| 组件名 | PascalCase | `<UserProfile />` |
| 变量/函数 | camelCase | `userName`, `getUserInfo()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| CSS 类名 | kebab-case | `.nav-bar`, `.user-profile` |

### 2.2 组件写法

**必须使用 `<script setup lang="ts">` 组合式 API：**

```vue
<script setup lang="ts">
import { ref, computed } from "vue";

const props = defineProps<{
  title: string;
}>(); 

const count = ref(0);
const doubled = computed(() => count.value * 2);

function increment() {
  count.value++;
}
</script>
```

### 2.3 路径别名

使用 `@/` 代替 `src/`（已在 vite.config.ts 和 tsconfig.json 中配置）：

```typescript
// 正确
import NavBar from "@/components/common/NavBar.vue";
import { useUserStore } from "@/store/user";

// 错误（不推荐相对路径出层级）
import NavBar from "../../components/common/NavBar.vue";
```

### 2.4 API 请求规范

1. 所有后端接口请求统一放在 `src/api/` 目录下
2. 按业务模块分文件（user.ts / analysis.ts / jobMatch.ts 等）
3. 不允许在组件中直接写 axios 请求

```typescript
// src/api/user.ts
import http from "./index";

export function login(data: { username: string; password: string }) {
  return http.post("/user/login", data);
}
```

### 2.5 状态管理规范

1. 全局共享状态放在 `src/store/` 下的 Pinia Store
2. 按领域分文件（user.ts / analysis.ts 等）
3. 组件内部状态用 `ref` / `reactive`，不要什么都放 Store

```typescript
// src/store/user.ts
import { defineStore } from "pinia";
import { ref } from "vue";

export const useUserStore = defineStore("user", () => {
  const userInfo = ref<object | null>(null);
  const isLoggedIn = ref(false);

  // ... actions

  return { userInfo, isLoggedIn };
});
```

### 2.6 样式规范

1. 组件样式默认使用 `<style scoped>`，避免全局污染
2. 全局样式放在 `assets/styles/` 下（后续创建）
3. 优先使用 CSS 变量管理主题色

---

## 3. 后端开发规范

### 3.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/文件 | snake_case | `user_service.py`, `job_match.py` |
| 类名 | PascalCase | `UserService`, `AnalysisModel` |
| 函数/方法 | snake_case | `get_user_info()`, `create_report()` |
| 变量 | snake_case | `user_name`, `match_score` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |

### 3.2 分层架构规范

严格遵守分层架构，禁止跨层调用：

```
API 层 → Service 层 → Model 层
```

- **API 层**（app/api/）：只做参数接收、调用 Service、返回响应
- **Service 层**（app/services/）：核心业务逻辑，可以调用多个 Model 或外部服务
- **Model 层**（app/models/）：只做数据存取，不包含业务逻辑

### 3.3 类型提示

所有函数必须添加完整的类型注解（Type Hints）：

```python
# 正确
def get_user_by_id(user_id: int) -> User | None:
    """根据ID获取用户"""
    pass

# 错误
def get_user_by_id(user_id):
    pass
```

### 3.4 数据校验

- 请求参数校验使用 Pydantic Schema（app/schemas/）
- 不要在业务代码中手动做参数校验
- 响应数据也使用 Schema 序列化

### 3.5 路由注册

新增模块路由后，必须在 `main.py` 中注册：

```python
from app.api import user, analysis

app.include_router(user.router, prefix="/api/user", tags=["用户管理"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["AI分析"])
```

### 3.6 错误处理

1. 使用 `app/utils/exceptions.py` 中的自定义异常
2. 不直接 `raise Exception("xxx")`
3. API 层不捕获异常，统一由全局异常处理器处理

### 3.7 导入顺序

Python 文件导入按以下顺序排列（空行分隔）：

```python
# 1. 标准库
import os
from datetime import datetime

# 2. 第三方库
from fastapi import APIRouter
from sqlalchemy.orm import Session

# 3. 项目内部模块
from app.services.user_service import UserService
from app.schemas.user import UserRegisterRequest
from app.utils.response import success
```

---

## 4. Git 规范（建议）

### 4.1 分支策略

- `main` / `master`：主分支，生产环境代码
- `dev`：开发分支，所有功能合并到这里
- `feature/xxx`：功能分支，从 dev 切出，开发完成后合并回 dev
- `fix/xxx`：修复分支，修复 bug 用

### 4.2 Commit 信息

格式：`<类型>: <简要描述>`

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 文档更新 |
| `style` | 代码格式调整（不影响功能） |
| `refactor` | 重构（不新增功能，不修 bug） |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建/工具/依赖调整 |

示例：
```
feat: 实现用户注册接口
fix: 修复登录页面样式错位
docs: 更新架构文档
```

---

## 5. 项目结构扩展规范

### 5.1 新增功能模块

新增一个功能模块时，需要同步更新以下位置：

**前端：**
- `src/api/xxx.ts` — API 请求封装
- `src/views/Xxx.vue` — 页面组件（如需要）
- `src/router/index.ts` — 路由配置（如需要）
- `src/store/xxx.ts` — 状态管理（如需要）

**后端：**
- `app/api/xxx.py` — API 路由
- `app/services/xxx_service.py` — 业务服务
- `app/models/xxx.py` — ORM 模型（如需要）
- `app/schemas/xxx.py` — Pydantic Schema
- `main.py` — 注册路由

---

## 6. 环境变量规范

- 敏感信息（数据库密码、API Key 等）**绝对不能硬编码**
- 使用 `.env` 文件管理环境变量
- `.env` 文件必须加入 `.gitignore`
- 提供 `.env.example` 示例文件（后续创建）

---

## 7. 给 AI Agent 的工作守则

1. **先读文档再动手**：先读 `docs/PROJECT_NAVIGATION.md` 了解项目全貌
2. **保持代码风格一致**：参考同目录下已有文件的写法
3. **不要实现业务逻辑**（除非明确要求）：只搭建结构，留 TODO 注释
4. **每个文件顶部必须有中文注释**
5. **修改代码前先 Read 再 Edit**：确保用最新内容做替换

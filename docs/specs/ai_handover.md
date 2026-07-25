# AI 模块交接：学生上下文契约

> **提供方：** 后端基础数据模块
> **使用方：** AI、知识库与 Prompt 开发成员
> **版本：** v1.0
> **更新日期：** 2026-07-23

## 1. 目的与边界

学生资料模块已经提供稳定的学生上下文，供就业画像、岗位匹配、简历优化和成长规划服务使用。当前技术路线为 FastAPI 直接调用 DeepSeek，本地 `knowledge/` JSON 文件是首版岗位知识库；本阶段不使用 FastGPT。

AI 模块不得直接查询 `User`、`UserSkill` 或 `UserProject` ORM 模型，也不得修改 `app/models/user.py`、`app/schemas/user.py`、`app/services/user_service.py`。学生资料字段有新增需求时，先与基础数据模块确认并更新本契约。

## 2. 获取方式

### 2.1 同一 FastAPI 进程内

AI Service 通过依赖注入取得 `Session` 后，直接调用：

```python
context = UserService(database_session).get_user_context(user_id)
```

该方法返回 `StudentContextResponse`，其字段和下方 HTTP 响应的 `data` 完全一致。

### 2.2 独立联调或调试

```text
GET /api/users/{user_id}/context
```

成功时返回 HTTP `200`：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": 1,
    "name": "张同学",
    "school": "示例大学",
    "major": "软件工程",
    "grade": "2024级",
    "bio": "希望从事后端或 AI 应用开发。",
    "skills": [
      {
        "id": 1,
        "user_id": 1,
        "name": "Python",
        "proficiency": "掌握",
        "description": "可使用 FastAPI 编写 REST API。"
      },
      {
        "id": 2,
        "user_id": 1,
        "name": "MySQL",
        "proficiency": "熟悉",
        "description": "可完成基础表设计和查询。"
      }
    ],
    "projects": [
      {
        "id": 1,
        "user_id": 1,
        "name": "就业竞争力分析助手",
        "role": "后端开发",
        "description": "负责学生资料接口、数据库模型和数据持久化。",
        "tech_stack": ["FastAPI", "SQLAlchemy", "MySQL"],
        "start_date": "2026-07-01",
        "end_date": null
      }
    ]
  }
}
```

## 3. 字段说明

| 字段 | 类型 | 含义 | AI 使用建议 |
|:---|:---|:---|:---|
| `user_id` | integer | 学生唯一标识 | 保存 AI 分析结果时的关联键 |
| `name` | string | 学生姓名 | 不应作为能力评分依据 |
| `school` | string | 学校 | 仅在报告背景中使用，不以学校直接推断能力 |
| `major` | string | 专业 | 用于选择岗位分析语境 |
| `grade` | string | 年级 | 用于评估当前成长阶段 |
| `bio` | string | 自我描述或目标方向 | 可提取目标岗位偏好，但应允许用户后续覆盖 |
| `skills` | array | 技能列表 | 使用 `name`、`proficiency`、`description` 分析能力 |
| `projects` | array | 项目经历列表 | 使用 `role`、`description`、`tech_stack` 分析工程经验 |
| `tech_stack` | string array | 项目技术栈 | 用于和岗位技能要求进行匹配 |

技能等级由弱到强依次为：`了解`、`熟悉`、`掌握`、`精通`。空数组表示用户尚未录入对应信息，不表示用户不具备该能力。

## 4. 错误契约

| 场景 | HTTP 状态 | `code` | 处理方式 |
|:---|:---:|:---:|:---|
| 用户不存在 | 404 | 3001 | 停止 AI 调用，提示先完善学生资料 |
| `user_id` 非法 | 422 | 1001 | 不调用模型，返回参数校验错误 |
| 数据库或服务内部错误 | 500 | 1 | 不重试写操作；可记录日志后提示稍后重试 |

所有错误响应均遵循：

```json
{"code": 3001, "message": "学生资料不存在", "data": null}
```

## 5. AI 成员工作清单

1. 在 `app/ai/deepseek_client.py` 实现 DeepSeek 客户端，API Key 仅从 `.env` 读取。
2. 在 `app/knowledge/` 加载 `knowledge/jobs.json` 和 `knowledge/skills.json`，实现岗位与技能检索。
3. 维护 `knowledge/prompts/` 中的就业画像、岗位匹配、简历优化和成长规划 Prompt。
4. AI Service 接收 `user_id`，通过本契约读取学生上下文，再调用知识库和 DeepSeek。
5. Prompt 中需要的 `target_job`、`preference`、`resume_content` 等字段由对应 AI API 请求额外提供，不能写入或臆造学生上下文字段。
6. AI 输出的结构、数据库结果表和 AI API 路由在 AI 模块内设计；在实现前与基础数据模块确认 `user_id` 的关联方式。

## 6. 联调检查清单

- `GET /api/users/{user_id}/context` 返回 `code=0`。
- 资料、技能和项目的字段名称与本文件示例一致。
- 空技能或空项目数组能被 AI 服务正常处理。
- 用户不存在时 AI 服务不发起 DeepSeek 请求。
- AI 输出保存时使用同一 `user_id`，不以姓名作为关联键。

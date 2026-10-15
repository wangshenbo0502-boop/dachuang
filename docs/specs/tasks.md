# Bugfix 任务清单

> **关联规范：** `docs/specs/bugfix.md` · `docs/specs/design.md`
> **状态：** 已完成
> **进度：** 3 / 3 已完成

- [x] **B-001:** 实现 SQLite 用户聚合表缺失列的幂等兼容迁移。
  - 涉及文件：`backend/app/database/`、`backend/main.py`、`backend/init_db.py`
  - 验证标准：旧版 SQLite 表补齐四个用户字段，重复执行不报错。
  - 预估工程量：30 分钟
  - 依赖：无

- [x] **B-002:** 为旧版 SQLite Schema 增加迁移和档案创建回归测试。
  - 涉及文件：`backend/tests/`
  - 验证标准：迁移后 `POST /api/users` 返回 201/code 0。
  - 预估工程量：20 分钟
  - 依赖：B-001

- [x] **B-003:** 验证运行中本地服务的档案创建接口。
  - 涉及文件：`backend/tests/`
  - 验证标准：当前 `backend/ai_job_analysis.db` 保留且可创建档案。
  - 预估工程量：10 分钟
  - 依赖：B-002

## 完成记录

| 任务 | 完成时间 | 结果 |
|:---|:---|:---|
| B-001 | 2026-09-11 | 自动补齐 `users` 的四个资料字段及 `user_competitions.competition_date` |
| B-002 | 2026-09-11 | 旧版 SQLite 迁移与用户 API 回归测试通过 |
| B-003 | 2026-09-11 | 运行中服务创建档案返回 HTTP 201/code 0，验证档案 ID 为 3 |

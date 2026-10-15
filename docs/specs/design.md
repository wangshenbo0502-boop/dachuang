# Bugfix 设计

> **关联缺陷：** `docs/specs/bugfix.md`
> **状态：** 已完成
> **最后更新：** 2026-09-11

## 根因

`init_db.py` 仅调用 SQLAlchemy `Base.metadata.create_all()`。该 API 只创建不存在的表，无法向已有 SQLite `users` 表添加后续模型增加的字段。因此应用代码与本地数据库 Schema 不一致。

## 最小修复策略

1. 在数据库初始化模块增加 SQLite 专用、幂等的兼容迁移函数。
2. 使用 `PRAGMA table_info(users)` 获取现有列。
3. 对 `users` 缺失的 `email`、`phone`、`target_city`、`target_salary` 逐列执行固定的 `ALTER TABLE users ADD COLUMN ... NOT NULL DEFAULT ''`；对 `user_competitions` 缺失的 `competition_date` 执行 `ALTER TABLE ... ADD COLUMN ... DATE`。
4. 在 FastAPI 启动阶段、模型注册完成后执行 `create_all()` 与兼容迁移；`init_db.py` 也复用同一函数。
5. 增加真实临时 SQLite 文件的回归测试：先创建旧版 `users` 表，再启动迁移并验证可创建用户。

## 明确不修改

- 不删除或复制数据库文件。
- 不自动迁移 MySQL。
- 不改变 API 路径、请求字段或响应契约。

## 验证策略

1. 临时 SQLite 文件从旧版 `users` 表开始，迁移后断言四列存在。
2. 对当前运行实例调用 `POST /api/users`，断言 HTTP 201/code 0。
3. 运行既有用户 API 契约测试，确保无回归。

## 审批记录

| 日期 | 审批人 | 决定 | 备注 |
|:---|:---|:---|:---|
| 2026-09-11 | 用户 | 批准 | 用户回复“开始” |

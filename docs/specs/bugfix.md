# Bugfix 规范

> **缺陷名称：** 就业档案创建因 SQLite 用户表版本落后而失败
> **状态：** 已完成
> **最后更新：** 2026-09-11

## 缺陷摘要

创建就业档案时，`POST /api/users` 返回 HTTP 500。运行日志确认 SQLite 报错：`table users has no column named email`。

## 当前行为

- 应用模型会写入 `email`、`phone`、`target_city`、`target_salary`。
- 已存在的 `backend/ai_job_analysis.db` 中 `users` 表缺少至少 `email` 列；实际聚合查询还确认 `user_competitions` 表缺少 `competition_date`。
- `Base.metadata.create_all()` 不会为已存在表补列，导致创建用户失败。

## 期望行为

- 对现有 SQLite 开发数据库的用户聚合表进行幂等的最小补列迁移。
- 迁移后创建档案返回 HTTP 201 和 `code=0`。
- 已有用户记录和其他数据表保留。

## 不变行为

- 不删除、重建或重命名任意已有表。
- 不修改 MySQL Schema，不引入第三方迁移框架。
- 新建数据库仍通过 `create_all()` 正常初始化。

## 影响范围与风险

- 影响范围：仅开发环境的 SQLite `users` 表。
- 风险：Schema 变更。必须限定为 `ADD COLUMN`，并以列存在检查保证可重复执行。

## 审批记录

| 日期 | 审批人 | 决定 | 备注 |
|:---|:---|:---|:---|
| 2026-09-11 | 用户 | 批准 | 用户回复“开始” |

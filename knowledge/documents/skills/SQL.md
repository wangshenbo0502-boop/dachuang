---
title: SQL
category: skills
tags: [数据库, 查询语言, 通用]
source: skill_improvement.json
date: 2026-07-28
---

# SQL

> 结构化查询语言，所有涉及数据存储的岗位都需要的通用技能。MySQL 是最流行的关系型数据库。

- **就业影响**: 高
- **前置技能**: 无
- **关联系能**: Java, Python, Node.js

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- SELECT/WHERE/ORDER BY/LIMIT
- INSERT/UPDATE/DELETE
- 聚合函数(COUNT/SUM/AVG)
- GROUP BY/HAVING
- 多表联查(INNER JOIN/LEFT JOIN)
- 子查询

**学习资源：**
- [SQLZoo（交互式练习）](https://sqlzoo.net/wiki/SQL_Tutorial) — 实战项目 · 免费 · 入门 · 英文
- [牛客网 SQL 实战](https://www.nowcoder.com/exam/oj) — 实战项目 · 免费 · 入门 · 中文

**练习项目：**
- 在 SQLZoo 上完成 0-7 章的练习

**评估方式：** 在线刷题 — 能在不看答案的情况下写出 3 表 JOIN + GROUP BY 的查询

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- 索引原理与优化(EXPLAIN)
- 数据库范式(1NF/2NF/3NF)
- 事务(ACID)与隔离级别
- 存储过程与触发器
- 视图
- 慢查询分析与优化

**学习资源：**
- [《高性能 MySQL（第4版）》](https://book.douban.com/subject/35921778/) — 书籍 · 付费 · 进阶 · 中文
- [MySQL 官方文档](https://dev.mysql.com/doc/refman/8.0/en/) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 为自己之前写的项目设计 ER 图，分析索引使用情况
- 用 EXPLAIN 优化 3 条慢查询

**评估方式：** 实操+面试 — 能解释索引类型(B+Tree/Hash)，说出至少 3 种慢查询优化方法

---

## 阶段 3 — 目标：掌握（预估 2 周）

**学习主题：**
- 分库分表方案
- 主从复制与读写分离
- MySQL 架构(连接池/查询缓存/存储引擎)
- 备份与恢复策略

**学习资源：**
- [《MySQL 技术内幕：InnoDB 存储引擎》](https://book.douban.com/subject/24708143/) — 书籍 · 付费 · 高级 · 中文

**练习项目：**
- 搭建一个 MySQL 主从复制环境（可用 Docker）

**评估方式：** 环境搭建 — 主从复制正常运行，延迟 < 1s

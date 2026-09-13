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

# 进阶要点与面试高频

SQL 的进阶分水岭是**窗口函数与 CTE**。窗口函数（ROW_NUMBER/RANK/DENSE_RANK、LAG/LEAD、SUM() OVER）在不折叠行的情况下做组内计算——"每组取前 N""连续登录天数""环比同比"这类经典题都是窗口函数的标准应用场景；CTE（WITH 子句）让复杂查询可读可维护，递归 CTE 可处理树形数据（组织架构、分类树）。

**逻辑执行顺序**是理解 SQL 的钥匙：FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT，理解"WHERE 里不能用 SELECT 别名""HAVING 与 WHERE 的区别"都源于此。性能层面需要掌握执行计划（EXPLAIN）的阅读：type 列（ALL 全表扫是反模式，至少到 range）、key 与 rows 的意义、索引失效的常见姿势（对索引列做函数运算、隐式类型转换、前导模糊 like '%x'、OR 混合非索引列）。

方言差异在实际工作高频出现：MySQL 与 PostgreSQL 的 JSON 支持、分页写法（LIMIT/OFFSET vs 游标分页——深分页优化的标准答案是游标/延迟关联）、时间函数差异。手写 SQL 是数据岗与后端岗的共同必考题，重点练习：多表 JOIN 的去重计数、留存率计算、Top N per group、累计指标——四类题型覆盖了绝大多数面试 SQL。

# Reference

1. Oracle. MySQL 8.x Reference Manual（SQL 语法与执行计划）. dev.mysql.com/doc. 访问时间: 2026-09-13.
2. The PostgreSQL Global Development Group. PostgreSQL 官方文档（窗口函数/CTE）. postgresql.org/docs. 访问时间: 2026-09-13.
3. SQLBolt. Interactive SQL Tutorial（交互式入门）. sqlbolt.com. 访问时间: 2026-09-13.

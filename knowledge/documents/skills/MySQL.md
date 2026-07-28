---
title: MySQL
category: skills
tags: [数据库, 关系型, 后端]
source: skill_improvement.json
date: 2026-07-28
---

# MySQL

> 最流行的开源关系型数据库，几乎所有后端岗位都要求掌握。

- **就业影响**: 高
- **前置技能**: SQL
- **关联系能**: Java, Spring Boot, Redis

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- MySQL 安装与连接
- 数据库/表创建
- 基本 SQL（同 SQL 技能的 stage 1）
- GUI 工具使用(Navicat/DBeaver)

**学习资源：**
- [MySQL 8.0 官方文档中文版](https://dev.mysql.com/doc/refman/8.0/en/) — 官方文档 · 免费 · 入门 · 英文

**练习项目：**
- 为自己之前的项目设计数据库表并手动创建

**评估方式：** 实操 — 能独立完成建库、建表、插入测试数据

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- 索引原理与优化（B+树、聚簇索引、二级索引、覆盖索引、最左前缀原则）
- 事务与 ACID 特性
- 隔离级别（读未提交/读已提交/可重复读/串行化）
- 锁机制（行锁/表锁/间隙锁/意向锁）
- 存储引擎（InnoDB/MyISAM 对比）
- 主从复制原理与配置
- SQL 优化（Explain 执行计划分析）
- 慢查询分析与优化

**学习资源：**
- [《高性能 MySQL（第4版）》](https://book.douban.com/subject/35668953/) — 书籍 · 付费 · 进阶 · 中文
- [MySQL 8.0 官方文档 - 优化篇](https://dev.mysql.com/doc/refman/8.0/en/optimization.html) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 为电商系统设计索引并优化慢查询

**评估方式：** 性能验证 — 对100万数据表，优化后查询速度提升10倍以上，Explain分析合理

---

## 阶段 3 — 目标：掌握（预估 4 周）

**学习主题：**
- 分库分表（垂直/水平拆分、ShardingSphere）
- 读写分离架构与实现
- 高可用架构（MHA/MMM/组复制）
- 性能调优（参数调优、配置优化）
- 备份恢复策略（全量/增量/二进制日志）
- 参数优化（连接池、缓存、InnoDB参数）
- MySQL 8.0 新特性（CTE/窗口函数/原子DDL）
- 数据库设计规范与最佳实践

**学习资源：**
- [《MySQL技术内幕：InnoDB存储引擎》](https://book.douban.com/subject/24708143/) — 书籍 · 付费 · 高级 · 中文
- [ShardingSphere 官方文档](https://shardingsphere.apache.org/document/current/cn/overview/) — 官方文档 · 免费 · 高级 · 中文

**练习项目：**
- 设计高可用 MySQL 集群方案

**评估方式：** 架构设计 — 提交完整的高可用集群设计方案，包含主从切换、故障转移、备份恢复策略

---
title: MongoDB
category: skills
tags: [数据库, NoSQL, 全栈]
source: skill_improvement.json
date: 2026-07-28
---

# MongoDB

> 流行的 NoSQL 文档数据库，适合灵活 Schema 的场景。Node.js 全栈项目的常见选择。

- **就业影响**: 中
- **前置技能**: JavaScript
- **关联系能**: Node.js, Docker

---

## 阶段 1 — 目标：了解（预估 1 周）

**学习主题：**
- MongoDB 安装
- 数据库/集合/文档概念
- CRUD 操作(find/insertOne/updateOne/deleteOne)
- MongoDB Compass 可视化工具
- Mongoose ODM 基础

**学习资源：**
- [MongoDB 大学（免费课程）](https://learn.mongodb.com/) — 在线课程 · 免费 · 入门 · 英文
- [Mongoose 官方文档](https://mongoosejs.com/docs/) — 官方文档 · 免费 · 入门 · 英文

**练习项目：**
- 用 Mongoose + Express 写一个简单的博客 API（文章增删改查）

**评估方式：** 接口测试 — CRUD 接口完整，数据能正确存储和查询

---

## 阶段 2 — 目标：熟悉（预估 1 周）

**学习主题：**
- 聚合管道(Aggregation Pipeline)
- 索引优化
- 数据建模(嵌入 vs 引用)
- 副本集与分片概念

**学习资源：**
- [MongoDB 官方手册](https://www.mongodb.com/docs/manual/) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 为博客系统添加聚合查询（如按分类统计文章数量）

**评估方式：** 实操 — 能写出至少 1 个包含 $match/$group/$sort 的聚合查询

# 原理与面试高频

MongoDB 是文档型数据库，数据以 **BSON**（二进制 JSON）存储，支持嵌套文档与数组，天然贴合对象模型，免去了关系库的多表关联。存储引擎为 **WiredTiger**：文档级并发控制、快照隔离、压缩（snappy/zlib/zstd）。

**副本集（Replica Set）**是高可用基石：一主（Primary）多从（Secondary），主节点写、从节点异步复制 oplog 并提供读；主节点故障时自动选举（基于 Raft 类协议）新主，通常 3 节点起。**分片（Sharding）**解决水平扩展：按 shard key 将集合数据分布到多个分片，由 mongos 路由、config server 管理元数据；shard key 一旦选定难以更改，需依据查询模式选择高基数、写分散的键。

索引与 MySQL 的 B+ 树不同，MongoDB 采用 **B-Tree（WiredTiger 实现）**，支持复合索引、多键索引（数组字段）、TTL 索引（自动过期）、文本索引与地理空间索引。 explain 命令分析执行计划（COLLSCAN 全表扫是典型性能反模式）。MongoDB 4.0 起支持副本集内多文档 ACID 事务，但设计上仍鼓励以文档结构化建模减少事务。

适用场景：内容管理、用户画像、IoT 时序数据、商品目录等 schema 灵活或需要水平扩展的场景；强事务型场景（资金账务）仍首选关系库。面试高频：BSON 与 JSON 区别、副本集选举与读写分离、分片键如何选择、与 MySQL 选型对比、聚合管道（$match/$group/$lookup）。

# Reference

1. MongoDB Inc. MongoDB 官方手册. mongodb.com/docs/manual. 访问时间: 2026-09-13. https://www.mongodb.com/docs/manual/
2. MongoDB Inc. MongoDB University（官方免费课程）. learn.mongodb.com. 访问时间: 2026-09-13.
3. MongoDB Inc. pymongo 驱动官方文档. pymongo.readthedocs.io. 访问时间: 2026-09-13.

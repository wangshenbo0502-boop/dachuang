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

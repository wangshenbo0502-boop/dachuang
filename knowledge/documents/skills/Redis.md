---
title: Redis
category: skills
tags: [数据库, 缓存, 后端]
source: skill_improvement.json
date: 2026-07-28
---

# Redis

> 高性能内存键值数据库，用于缓存、会话存储、消息队列、排行榜等场景。后端开发中大型项目的标配。

- **就业影响**: 中
- **前置技能**: 无
- **关联系能**: Java, Spring Boot, Node.js, Python

---

## 阶段 1 — 目标：了解（预估 1 周）

**学习主题：**
- Redis 安装与启动
- String/Hash/List/Set/ZSet 五种数据类型
- 基本命令(SET/GET/HSET/LPUSH等)
- 过期时间设置
- redis-cli 使用

**学习资源：**
- [Redis 官方文档](https://redis.io/docs/latest/) — 官方文档 · 免费 · 入门 · 英文
- [Redis 命令参考（中文）](https://redis.com.cn/commands.html) — 在线课程 · 免费 · 入门 · 中文

**练习项目：**
- 用 Redis 实现一个简单的访问计数器
- 用 Redis List 实现消息队列

**评估方式：** 独立完成 — 正确使用至少 4 种数据类型

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- 持久化(RDB/AOF)
- 主从复制
- 哨兵模式(Sentinel)
- 缓存策略(旁路/读写穿透)
- 缓存穿透/雪崩/击穿解决方案
- Spring Boot + Redis 集成

**学习资源：**
- [《Redis 设计与实现》](https://book.douban.com/subject/25900156/) — 书籍 · 付费 · 进阶 · 中文

**练习项目：**
- 为博客系统添加 Redis 缓存层（缓存热门文章）

**评估方式：** 代码审查+面试 — 能说明缓存更新策略，解释缓存雪崩的解决方案

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

# 原理与面试高频

Redis 是内存键值数据库，单线程命令执行（网络 I/O 自 6.0 起多线程）消除了锁竞争，配合 epoll 实现十万级 QPS。底层数据结构是面试重点：String 的 **SDS**（预分配与惰性释放，O(1) 取长度）；Hash 的 ziplist（7.0 起为 **listpack**）与 hashtable 的编码转换；ZSet 的**跳表（skiplist）+ dict** 双结构，跳表支持 O(logN) 范围查询——"为什么用跳表不用红黑树"是经典题（实现简单、范围查询友好、按概率维持平衡）。

**持久化**两条路线：RDB（定时 fork 子进程全量快照，恢复快、可能丢数据）与 AOF（追加写命令日志，appendfsync everysec 兼顾性能与安全，4.0 起 AOF 重写用 RDB 头+增量命令混合格式）。**高可用**：主从复制（异步，存在数据不一致窗口）、哨兵（Sentinel 自动故障转移）、Cluster 集群（16384 槽位哈希分片，客户端直连路由）。

**缓存三大问题**必须能完整作答：穿透（查不存在数据——布隆过滤器/空值缓存）、击穿（热点 key 过期瞬间——互斥锁/逻辑过期）、雪崩（大量 key 同时过期——随机 TTL/多级缓存）。**缓存一致性**主流方案是 Cache Aside（先更新库再删缓存）配合延迟双删；分布式锁用 SET NX PX + 唯一值 + Lua 释放，Redlock 算法在业界存在争议（ Martin Kleppmann 与作者的论战），面试中能说出争议点即加分。

# Reference

1. Redis Ltd. Redis 官方文档（数据类型与持久化）. redis.io/docs. 访问时间: 2026-09-13. https://redis.io/docs/latest/
2. Redis Ltd. Redis Replication 与 Sentinel 官方指南. redis.io/docs/latest/operate. 访问时间: 2026-09-13.
3. antirez. Redis 作者博客（设计原理一手资料）. antirez.com. 访问时间: 2026-09-13.

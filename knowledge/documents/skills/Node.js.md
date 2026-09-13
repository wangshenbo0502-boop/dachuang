---
title: Node.js
category: skills
tags: [后端, JavaScript, 全栈]
source: skill_improvement.json
date: 2026-07-28
---

# Node.js

> 让 JavaScript 运行在服务端的能力。全栈工程师必备，也是前端工程师理解后端的基础。

- **就业影响**: 高
- **前置技能**: JavaScript
- **关联系能**: TypeScript, MongoDB, Docker

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- Node.js 运行时
- 模块系统(CommonJS/ESM)
- fs/path/http 核心模块
- npm 包管理
- Express.js 基础路由
- 中间件概念

**学习资源：**
- [Node.js 官方文档](https://nodejs.org/zh-cn/docs) — 官方文档 · 免费 · 入门 · 中文
- [Express.js 官方文档](https://expressjs.com/zh-cn/) — 官方文档 · 免费 · 入门 · 中文

**练习项目：**
- 写一个 RESTful API 服务（图书管理系统：增删改查接口）

**评估方式：** 接口测试 — 4 个接口返回正确的 JSON 数据，有基本的错误处理

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- 身份认证(JWT/Session)
- 文件上传
- 数据校验
- 日志系统
- 环境变量管理
- MongoDB 连接(Mongoose)

**学习资源：**
- [《Node.js 实战》](https://book.douban.com/subject/30418478/) — 书籍 · 付费 · 进阶 · 中文

**练习项目：**
- 为图书管理系统添加用户注册/登录（JWT认证）+ MongoDB 数据库

**评估方式：** 安全审查 — 密码加密存储，敏感路由有认证中间件保护

# 原理与面试高频

Node.js 的核心是 **V8 引擎 + libuv**：V8 执行 JavaScript，libuv 提供事件循环与异步 I/O。事件循环按阶段轮转：timers（setTimeout/setInterval 回调）→ pending callbacks → poll（I/O 事件）→ check（setImmediate）→ close callbacks，两个阶段间执行微任务（Promise.then、process.nextTick，其中 nextTick 优先级最高）。

Node 的 JavaScript 执行是单线程的，因此**CPU 密集任务会阻塞事件循环**——这是它与 Java/Go 后端最本质的差异。解决方案：worker_threads 模块（多线程执行 CPU 任务）、子进程 cluster（多进程利用多核）或把重计算下沉到独立服务。I/O 密集场景（BFF 中间层、API 网关、实时推送）则是 Node 的主场，配合 stream 流式处理可高效处理大文件与网络传输。

模块体系上，CommonJS（require/exports）是历史主流，ESM（import/export）已成标准方向（Node 20+ 稳定支持），npm 生态是全世界最大的软件包仓库。Web 框架从 Express（经典）到 Koa（中间件洋葱模型）再到 NestJS（企业级、依赖注入、TypeScript 优先）。

面试高频：事件循环六个阶段与微任务时机、nextTick 与 Promise 区别、单线程模型与多核利用（cluster/worker_threads）、stream 四种类型与 backpressure、CommonJS 与 ESM 差异、中间件洋葱模型原理。

# Reference

1. OpenJS Foundation. Node.js 官方文档（含事件循环机制）. nodejs.org/docs. 访问时间: 2026-09-13. https://nodejs.org/docs/latest/api/
2. OpenJS Foundation. npm 官方文档. docs.npmjs.com. 访问时间: 2026-09-13.
3. Node.js. Node.js Best Practices（社区高质量实践库）. github.com/goldbergyoni/nodebestpractices. 访问时间: 2026-09-13.

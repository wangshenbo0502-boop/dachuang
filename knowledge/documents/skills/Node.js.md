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

---
title: TypeScript
category: skills
tags: [编程语言, 前端, 类型系统]
source: skill_improvement.json
date: 2026-07-28
---

# TypeScript

> JavaScript 的超集，增加静态类型系统。大中型项目标配，前端/全栈岗位几乎必会。

- **就业影响**: 高
- **前置技能**: JavaScript
- **关联系能**: Vue.js, React, Node.js

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- 基础类型注解
- 接口(interface)与类型别名(type)
- 函数类型
- 泛型基础
- 联合类型与交叉类型
- 类型推断
- tsconfig.json 配置

**学习资源：**
- [TypeScript 官方手册](https://www.typescriptlang.org/zh/docs/handbook/intro.html) — 官方文档 · 免费 · 入门 · 中文
- [TypeScript 入门教程（阮一峰）](https://ts.xcatliu.com/) — 在线课程 · 免费 · 入门 · 中文

**练习项目：**
- 把之前写的 JavaScript Todo List 逐行加上 TypeScript 类型

**评估方式：** 类型检查 — tsc --noEmit 命令无错误输出

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- 高级泛型(extends/keyof/infer)
- 工具类型(Partial/Required/Pick/Omit)
- 条件类型
- 声明文件(.d.ts)
- 枚举与常量断言

**学习资源：**
- [TypeScript Deep Dive](https://jkchao.github.io/typescript-book-chinese/) — 在线课程 · 免费 · 进阶 · 中文

**练习项目：**
- 给一个开源 JS 项目写 .d.ts 声明文件
- 实现一个简化版的 axios 类型系统

**评估方式：** 类型挑战 — 能完成 type-challenges 中等难度的 5 道题

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

# 进阶要点与面试高频

TypeScript 的类型系统是**结构化类型（structural typing）**：只要形状匹配即兼容（duck typing 的编译期版本），这与 Java/C# 的名义类型系统本质不同——理解这一点是回答"interface 和 type 区别"（语义上几乎等价，差异在扩展语法与联合类型表达力）与"为什么 TS 是 JS 的超集而非 Java 的类型系统"的基础。

进阶工具类型要能信手拈来：Partial/Required/Readonly（映射类型 + 修饰符）、Pick/Omit/Record（索引与筛选）、ReturnType/Parameters（用 infer 从函数类型中提取），以及手写实现的套路——映射类型的 key remapping（as 子句）、条件类型的分布式行为（联合类型在裸类型参数上自动分发）、infer 的位置推断。**类型体操**的本质是"在类型层面做函数式编程"，面试常考手写 DeepPartial、UnionToIntersection、GetRequiredKeys。

工程实践决定了 TS 的真实价值：strict 模式全开（noImplicitAny/strictNullChecks 是底线）、any 与 unknown 的区别（unknown 类型安全、使用前必须收窄）、类型收窄手段（typeof/in/可辨识联合/discriminated union）、泛型的默认值与约束（extends）。编译层面：tsc 只做类型检查与类型擦除（不优化运行时），构建性能靠 Vite/esbuild/swc 转译 + tsc 仅做类型检查的组合方案；tsconfig 的 module/moduleResolution/target 与 paths 别名配置是工程化基本功。

# Reference

1. Microsoft. TypeScript 官方文档（The TypeScript Handbook）. typescriptlang.org/docs/handbook. 访问时间: 2026-09-13. https://www.typescriptlang.org/docs/handbook/intro.html
2. Microsoft. TypeScript tsconfig Reference. typescriptlang.org/tsconfig. 访问时间: 2026-09-13.
3. Microsoft. TypeScript GitHub 仓库与 Release Notes. github.com/microsoft/TypeScript. 访问时间: 2026-09-13.

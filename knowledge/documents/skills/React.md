---
title: React
category: skills
tags: [框架, 前端, JavaScript]
source: skill_improvement.json
date: 2026-07-28
---

# React

> 全球使用最广泛的前端 UI 库，大厂主流选择。配合 TypeScript 和 Next.js 是全栈岗位的核心技术。

- **就业影响**: 高
- **前置技能**: HTML, CSS, JavaScript, TypeScript
- **关联系能**: Node.js, Next.js, Vue.js

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- JSX 语法
- 组件与 Props
- useState / useEffect
- 条件渲染与列表渲染
- 事件处理
- 受控组件与表单

**学习资源：**
- [React 官方教程（井字棋）](https://zh-hans.react.dev/learn/tutorial-tic-tac-toe) — 官方文档 · 免费 · 入门 · 中文
- [React 全新官方文档](https://zh-hans.react.dev/) — 官方文档 · 免费 · 入门 · 中文

**练习项目：**
- 用 React 重写天气预报查询页面

**评估方式：** 独立完成 — 组件拆分合理，useEffect 依赖数组正确

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- useReducer / useContext
- React Router
- useMemo / useCallback
- 自定义 Hook
- TanStack Query(React Query)
- Tailwind CSS + shadcn/ui

**学习资源：**
- [React Router 官方文档](https://reactrouter.com/) — 官方文档 · 免费 · 进阶 · 英文
- [TanStack Query 文档](https://tanstack.com/query/latest) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 写一个在线商城页面（商品列表/购物车/搜索筛选）+ 用 JSON Server 模拟后端

**评估方式：** 代码审查 — 自定义 Hook 合理抽象复用逻辑，React Query 管理服务端状态

---

## 阶段 3 — 目标：掌握（预估 3 周）

**学习主题：**
- Next.js(App Router/SSR/SSG)
- 状态管理(Zustand)
- React 性能优化(React.memo/Suspense)
- Storybook 组件文档
- React Testing Library

**学习资源：**
- [Next.js 官方教程](https://nextjs.org/learn) — 官方文档 · 免费 · 高级 · 英文

**练习项目：**
- 用 Next.js 重构商城项目，实现 SSR + ISR

**评估方式：** 性能测试 — Lighthouse 评分 > 85，首屏加载 < 2s

# 原理与面试高频

React 的现代核心是 **Fiber 架构**：把渲染工作拆分为可中断的小单元（Fiber 节点），通过调度器（Scheduler，基于优先级与 MessageChannel 时间切片）协调渲染与用户交互，实现"并发渲染"。两棵 Fiber 树（current 与 workInProgress）配合双缓冲实现增量更新与中断恢复。

**Hooks 原理**是面试必考：Hooks 依托 Fiber 节点上的链表按调用顺序索引（因此有"不能放在条件语句里"的规则）；useState 的更新触发重渲染，useEffect 的依赖数组与 cleanup 机制对应副作用的挂载/更新/卸载时机；useMemo/useCallback 的记忆化本质是依赖数组的浅比较。React 18 的并发特性（useTransition/useDeferredValue 区分紧急与非紧急更新）与 React 19 的 Server Components/Actions 是新的加分考点。

工程层面：状态管理从 Redux（单一 store、action 不可变流）演进到轻量方案（Zustand/Jotai 原子化状态）与服务端状态专用库（TanStack Query 解决缓存/重试/失效）；Next.js 提供 SSR/SSG/RSC 全栈能力，是 React 生态事实上的全栈标准。diff 算法三假设（同类型元素复用、key 标识跨层级移动、同级多节点 O(n) 比较）决定了"为什么列表要稳定唯一的 key"这类高频题的标准答案。

# Reference

1. Meta Open Source. React 官方文档（react.dev）. react.dev. 访问时间: 2026-09-13. https://react.dev/
2. Meta Open Source. React 19 Release Notes（Server Components / Actions）. react.dev/blog. 访问时间: 2026-09-13.
3. Vercel. Next.js 官方文档（React 全栈框架）. nextjs.org/docs. 访问时间: 2026-09-13.

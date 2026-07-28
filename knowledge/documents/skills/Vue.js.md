---
title: Vue.js
category: skills
tags: [框架, 前端, JavaScript]
source: skill_improvement.json
date: 2026-07-28
---

# Vue.js

> 国内使用最广泛的前端框架之一，上手友好但生态完整。初级前端岗位高频要求项。

- **就业影响**: 高
- **前置技能**: HTML, CSS, JavaScript
- **关联系能**: TypeScript, React, Node.js

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- 创建 Vue 项目(Vite)
- 模板语法与指令(v-bind/v-if/v-for/v-model)
- 响应式基础(ref/reactive)
- 计算属性(computed)与侦听器(watch)
- 组件基础(props/emits)
- 生命周期钩子

**学习资源：**
- [Vue.js 官方教程](https://cn.vuejs.org/tutorial/) — 官方文档 · 免费 · 入门 · 中文
- [Vue3 入门指南](https://cn.vuejs.org/guide/introduction.html) — 官方文档 · 免费 · 入门 · 中文

**练习项目：**
- 写一个天气预报查询页面（组件拆分+API调用+列表渲染）

**评估方式：** 独立完成 — 组件拆分合理（至少3个子组件），数据流使用 props/emits

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- Vue Router（路由/导航守卫/懒加载）
- Pinia 状态管理
- 组合式函数(Composables)
- 插槽(slots)
- Teleport/Suspense
- Axios 封装
- 环境变量配置

**学习资源：**
- [Vue Router 官方文档](https://router.vuejs.org/zh/) — 官方文档 · 免费 · 进阶 · 中文
- [Pinia 官方文档](https://pinia.vuejs.org/zh/) — 官方文档 · 免费 · 进阶 · 中文

**练习项目：**
- 写一个带登录态的个人博客系统（Vue3+Vue Router+Pinia）

**评估方式：** 代码审查 — 路由守卫保护登录页，Pinia 管理用户状态，Axios 有统一拦截器

---

## 阶段 3 — 目标：掌握（预估 3 周）

**学习主题：**
- TypeScript + Vue3
- 组件库封装
- 自定义指令
- 虚拟列表实现
- SSR(Nuxt.js)
- 性能优化(KeepAlive/异步组件)
- 自动化测试(Vitest)

**学习资源：**
- [Nuxt.js 官方文档](https://nuxt.com/docs) — 官方文档 · 免费 · 高级 · 英文
- [Vitest 官方文档](https://cn.vitest.dev/) — 官方文档 · 免费 · 进阶 · 中文

**练习项目：**
- 封装一个通用表格组件发布到 npm
- 用 Nuxt.js 重写个人博客实现 SSR

**评估方式：** 代码审查+性能测试 — 组件的 props 类型完整，有使用文档，Lighthouse 评分 > 80

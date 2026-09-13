---
title: CSS
category: skills
tags: [前端, 样式, Web开发]
source: skill_improvement.json
date: 2026-07-28
---

# CSS

> 网页样式和布局语言，从简单的颜色字体到复杂的响应式布局和动画效果。前端岗位必会技能。

- **就业影响**: 高
- **前置技能**: HTML
- **关联系能**: JavaScript, Vue.js, React

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- 选择器与优先级
- 盒模型
- 颜色/字体/背景
- Flexbox 布局
- Grid 布局
- 响应式设计基础(媒体查询)

**学习资源：**
- [MDN CSS 教程](https://developer.mozilla.org/zh-CN/docs/Learn/CSS) — 官方文档 · 免费 · 入门 · 中文
- [Flexbox Froggy（游戏化学习）](https://flexboxfroggy.com/) — 实战项目 · 免费 · 入门 · 中文
- [CSS Grid Garden（游戏化学习）](https://cssgridgarden.com/) — 实战项目 · 免费 · 入门 · 中文

**练习项目：**
- 用 Flexbox + Grid 还原一个常见的网站首页布局（导航+内容+侧边栏+底部）

**评估方式：** 独立完成 — 页面在手机/平板/桌面三种宽度下布局正常不崩溃

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- CSS变量
- 过渡与动画(transition/animation)
- BEM命名规范
- 伪类与伪元素深入
- CSS预处理器(SCSS)
- 移动端适配(rem/vw)

**学习资源：**
- [CSS Secrets（CSS揭秘）](https://book.douban.com/subject/26745943/) — 书籍 · 付费 · 进阶 · 中文
- [SCSS 官方文档](https://sass-lang.com/documentation/) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 为一个网站添加 hover 动画、页面切换过渡动画、骨架屏加载动画

**评估方式：** 代码审查 — CSS 文件中有变量复用，动画流畅 60fps，命名遵循 BEM 规范

---

## 阶段 3 — 目标：掌握（预估 2 周）

**学习主题：**
- CSS-in-JS
- Tailwind CSS
- PostCSS
- 浏览器渲染性能优化
- 复杂动画(GSAP)

**学习资源：**
- [Tailwind CSS 官方文档](https://tailwindcss.com/docs) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 用 Tailwind CSS 重写之前的页面，并添加 GSAP 动画

**评估方式：** 工具检测 — Lighthouse Performance 评分 > 90，动画使用 GPU 加速

# 进阶要点与面试高频

超越基础语法后，CSS 的三个进阶主线值得系统掌握。**布局体系**：Flex 一维布局（主轴/交叉轴、flex:1 的完整含义 flex-grow/shrink/basis）、Grid 二维布局（模板区域、minmax/fr 单位）、以及现代响应式单位（rem/em/vw/vh、clamp() 流体排版）；**容器查询（Container Queries）**已获主流浏览器支持，组件可依据父容器而非视口自适应，是组件化时代的重要演进。

**层叠与继承机制**是面试深水区：选择器优先级（inline > id > class > tag）、层叠上下文（stacking context）如何决定元素绘制顺序、z-index 为何"失效"（未创建层叠上下文或父级受限）。**渲染性能**：重排（layout）与重绘（paint）的触发条件与代价排序（重排 > 重绘 > 合成），transform/opacity 走合成层不触发重排——动画优化（用 transform 替代 top/left、will-change 提示）是高频考题。

现代工程实践：CSS 变量（custom properties）实现主题切换、@media 与 dark mode 适配、BEM 命名或 CSS Modules/CSS-in-JS 的工程选型。面试高频：水平垂直居中的 N 种写法、BFC 的触发条件与应用（清除浮动/防止 margin 合并）、flex:1 细节、sticky 定位原理、重排重绘优化、移动端 1px 问题。

# Reference

1. MDN Web Docs. CSS 参考文档. developer.mozilla.org/zh-CN/docs/Web/CSS. 访问时间: 2026-09-13.
2. Google Chrome Team. web.dev Learn CSS（官方交互教程）. web.dev/learn/css. 访问时间: 2026-09-13.
3. Can I use. 浏览器兼容性数据查询. caniuse.com. 访问时间: 2026-09-13.

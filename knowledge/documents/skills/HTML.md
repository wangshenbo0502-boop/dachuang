---
title: HTML
category: skills
tags: [前端, 基础, Web开发]
source: skill_improvement.json
date: 2026-07-28
---

# HTML

> 网页结构和内容标记语言，所有 Web 开发的基础，门槛低但精通需要深入理解语义化和可访问性。

- **就业影响**: 高
- **前置技能**: 无
- **关联系能**: CSS, JavaScript

---

## 阶段 1 — 目标：了解（预估 1 周）

**学习主题：**
- HTML文档结构
- 常用标签(h1-h6/p/a/img/div/span)
- 列表与表格
- 表单元素
- 语义化标签(header/nav/main/section/article/footer)

**学习资源：**
- [MDN HTML 教程](https://developer.mozilla.org/zh-CN/docs/Learn/HTML) — 官方文档 · 免费 · 入门 · 中文
- [freeCodeCamp HTML](https://www.freecodecamp.org/chinese/learn/responsive-web-design) — 在线课程 · 免费 · 入门 · 中文

**练习项目：**
- 写一个个人介绍页面，包含标题/段落/图片/链接/列表

**评估方式：** 独立完成 — 页面不含任何 CSS 仍能清晰表达信息结构

---

## 阶段 2 — 目标：熟悉（预估 1 周）

**学习主题：**
- 表单高级用法(验证/文件上传)
- 多媒体标签(audio/video/canvas)
- SEO Meta标签
- 无障碍ARIA属性
- HTML5新特性

**学习资源：**
- [MDN HTML 进阶](https://developer.mozilla.org/zh-CN/docs/Web/HTML) — 官方文档 · 免费 · 进阶 · 中文

**练习项目：**
- 做一个包含多种输入类型的注册表单页面

**评估方式：** 代码审查 — 表单元素全部使用语义化标签，包含基本的客户端验证属性

---

## 阶段 3 — 目标：掌握（预估 1 周）

**学习主题：**
- Web Components基础
- HTML模板(Handlebars/EJS)
- 邮件HTML写法
- 浏览器兼容性处理

**学习资源：**
- [HTML5 Boilerplate](https://html5boilerplate.com/) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 将之前写的页面改造成语义化+无障碍友好的版本

**评估方式：** 工具检测 — 通过 W3C 验证器检测，Lighthouse Accessibility 评分 > 90

# 进阶要点与面试高频

HTML 的进阶价值在于**语义化、可访问性与平台能力**三个方向。语义化是用对标签而非堆 div：header/nav/main/article/section/aside/footer 表达文档结构，figure/figcaption、time、details/summary 各司其职。语义化的收益是实打实的：屏幕阅读器可正确导航（可访问性 a11y）、搜索引擎更好理解页面（SEO）、代码可维护性更高。可访问性还包括 alt 文本、label 关联表单控件、ARIA 属性的规范使用、键盘可达性（tabindex 与焦点管理）。

**meta 与文档头**是实际业务高频点：viewport（移动端适配的根基）、charset、SEO 相关（description、Open Graph 社交分享卡片）、CSP（内容安全策略防御 XSS）。**HTML5 平台 API**扩展了纯标记的边界：表单原生校验（required/pattern）、拖放、history 路由（SPA 基础）、Web Components（自定义元素，框架无关组件方案的底层）、localStorage/sessionStorage/IndexedDB 存储。

加载行为是性能话题的入口：script 的 defer 与 async 区别（defer 保序延后执行、async 下载完即执行）、预加载提示（preload/prefetch/preconnect）、图片的 srcset/lazy loading。面试高频：语义化标签的意义、defer 与 async 区别、localStorage 与 Cookie 区别、浏览器渲染流程中 HTML 的解析与 DOM 构建、跨标签页通信（BroadcastChannel/storage 事件）。

# Reference

1. WHATWG. HTML Living Standard（唯一现行标准）. html.spec.whatwg.org. 访问时间: 2026-09-13.
2. MDN Web Docs. HTML：超文本标记语言. developer.mozilla.org/zh-CN/docs/Web/HTML. 访问时间: 2026-09-13.
3. web.dev. Learn HTML（Google 官方课程）. web.dev/learn/html. 访问时间: 2026-09-13.

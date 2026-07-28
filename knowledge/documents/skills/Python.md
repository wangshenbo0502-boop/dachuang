---
title: Python
category: skills
tags: [编程语言, 通用, 后端, 数据科学]
source: skill_improvement.json
date: 2026-07-28
---

# Python

> 简洁优雅的通用编程语言。就业方向极广：后端开发、数据分析、AI/机器学习、自动化运维。学生最容易上手的第一门语言。

- **就业影响**: 高
- **前置技能**: 无
- **关联系能**: MySQL, Pandas, NumPy, PyTorch, Docker

---

## 阶段 1 — 目标：了解（预估 3 周）

**学习主题：**
- 变量与数据类型
- 条件与循环
- 函数定义
- 列表/元组/字典/集合
- 文件读写
- 异常处理
- 包管理与虚拟环境(pip/venv)

**学习资源：**
- [Python 官方教程](https://docs.python.org/zh-cn/3/tutorial/) — 官方文档 · 免费 · 入门 · 中文
- [廖雪峰 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400) — 在线课程 · 免费 · 入门 · 中文

**练习项目：**
- 写一个命令行学生管理系统（增删改查+文件持久化）

**评估方式：** 独立完成 — 程序功能完整，数据保存到 JSON/TXT 文件，有异常处理

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- 面向对象编程(类/继承/多态)
- 装饰器
- 生成器与迭代器
- 正则表达式
- 常用标准库(os/datetime/json/re/collections)
- 数据库操作(SQLAlchemy/pymysql)
- HTTP请求(requests/httpx)

**学习资源：**
- [《流畅的 Python》](https://book.douban.com/subject/27028517/) — 书籍 · 付费 · 进阶 · 中文
- [Real Python 教程](https://realpython.com/) — 在线课程 · 部分免费 · 进阶 · 英文

**练习项目：**
- 写一个豆瓣图书爬虫（requests+BeautifulSoup，存到 SQLite）
- 用 SQLAlchemy 重写学生管理系统为 Web API 版本

**评估方式：** 代码审查 — 类设计合理，数据持久化，能处理网络异常

---

## 阶段 3 — 目标：掌握（预估 3 周）

**学习主题：**
- 异步编程(async/await/aiohttp)
- FastAPI 框架
- 单元测试(pytest)
- 类型注解与mypy
- 性能分析(cProfile)

**学习资源：**
- [FastAPI 官方教程](https://fastapi.tiangolo.com/zh/tutorial/) — 官方文档 · 免费 · 进阶 · 中文
- [Pytest 官方文档](https://docs.pytest.org/) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 用 FastAPI 搭建一个带接口文档的博客 API 服务
- 为关键接口写 pytest 测试

**评估方式：** 测试覆盖率 — 核心业务代码测试覆盖率 > 80%，接口文档完整可交互

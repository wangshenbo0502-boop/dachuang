---
title: Pandas
category: skills
tags: [Python, 数据分析, 数据处理]
source: skill_improvement.json
date: 2026-07-28
---

# Pandas

> Python 数据分析的核心库，提供高性能的数据结构(DataFrame)和数据处理工具。数据分析师入门必备。

- **就业影响**: 中
- **前置技能**: Python, NumPy
- **关联系能**: NumPy, 机器学习

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- DataFrame 与 Series
- 读取 CSV/Excel/JSON
- 数据筛选与切片(loc/iloc)
- 数据清洗(缺失值/重复值/类型转换)
- 分组聚合(groupby)
- 基本绘图(plot)

**学习资源：**
- [Pandas 官方文档 10分钟入门](https://pandas.pydata.org/docs/user_guide/10min.html) — 官方文档 · 免费 · 入门 · 英文
- [《利用 Python 进行数据分析（第3版）》](https://book.douban.com/subject/36130267/) — 书籍 · 付费 · 入门 · 中文

**练习项目：**
- 找一份公开数据集（如 Kaggle Titanic），完成数据清洗和探索性分析

**评估方式：** 独立完成 — 能读入数据并完成缺失值处理、按某列分组统计、输出基本图表

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- 数据清洗进阶（缺失值/重复值/异常值处理）
- 分组聚合（groupby 高级用法、agg/transform/apply）
- 表合并（merge/join/concat 及各种连接方式）
- 时间序列处理（日期索引、重采样、滚动窗口）
- 数据透视表（pivot_table/crosstab）
- 字符串处理（str 访问器、正则提取）

**学习资源：**
- [Pandas 官方用户指南](https://pandas.pydata.org/docs/user_guide/index.html) — 官方文档 · 免费 · 进阶 · 英文
- [《Pandas Cookbook（第2版）》](https://book.douban.com/subject/35417203/) — 书籍 · 付费 · 进阶 · 中文

**练习项目：**
- 分析一份真实电商销售数据并生成报表

**评估方式：** 报告评审 — 提交完整的分析报告，包含数据清洗、多维度分析、可视化图表和业务洞察

---

## 阶段 3 — 目标：掌握（预估 3 周）

**学习主题：**
- 性能优化（eval/query/categorical 类型优化）
- 高级分组变换（自定义变换函数、分组排名）
- 多层索引操作（MultiIndex 索引/切片/堆叠）
- 自定义聚合函数（agg 自定义、numba 加速）
- 大数据量处理技巧（chunk 分块读取、内存优化、Dask）
- 与数据库/Excel 交互（SQL 读写、大型 Excel 处理）
- Pandas 2.0 新特性（PyArrow 后端、Copy-on-Write）

**学习资源：**
- [《Python数据科学手册（第2版）》](https://book.douban.com/subject/36502280/) — 书籍 · 付费 · 高级 · 中文
- [Pandas 2.0 官方文档](https://pandas.pydata.org/docs/whatsnew/v2.0.0.html) — 官方文档 · 免费 · 高级 · 英文

**练习项目：**
- 处理百万级数据文件并优化内存占用

**评估方式：** 性能验证 — 百万级数据处理内存占用降低50%以上，处理时间在可接受范围内，有优化前后对比报告

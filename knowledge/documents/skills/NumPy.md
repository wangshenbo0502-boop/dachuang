---
title: NumPy
category: skills
tags: [Python, 科学计算, 数据处理]
source: skill_improvement.json
date: 2026-07-28
---

# NumPy

> Python 科学计算基础库，提供了高效的多维数组运算。是 Pandas、机器学习等几乎所有数据相关库的底层依赖。

- **就业影响**: 中
- **前置技能**: Python
- **关联系能**: Pandas, PyTorch, 机器学习

---

## 阶段 1 — 目标：了解（预估 1 周）

**学习主题：**
- ndarray 创建与属性
- 数组索引与切片
- 数组运算(广播机制)
- 通用函数(ufunc)
- 线性代数运算
- 随机数生成

**学习资源：**
- [NumPy 官方快速入门](https://numpy.org/doc/stable/user/quickstart.html) — 官方文档 · 免费 · 入门 · 英文

**练习项目：**
- 用 NumPy 实现矩阵乘法、均值归一化、简单的线性回归

**评估方式：** 独立完成 — 能用 NumPy 完成矩阵运算，理解广播机制

---

## 阶段 2 — 目标：熟悉（预估 1 周）

**学习主题：**
- 高级索引（布尔索引/花式索引）
- 数组变形与重塑（reshape/transpose/swapaxes）
- 广播机制深入理解
- 统计函数（mean/std/median/corrcoef）
- 矩阵运算（点积/逆矩阵/行列式/特征值）
- 线性代数（numpy.linalg 模块）
- 随机数与抽样（随机分布、随机种子、采样方法）

**学习资源：**
- [NumPy 官方用户指南](https://numpy.org/doc/stable/user/index.html) — 官方文档 · 免费 · 进阶 · 英文
- [《利用 Python 进行数据分析（第3版）》](https://book.douban.com/subject/36130267/) — 书籍 · 付费 · 进阶 · 中文

**练习项目：**
- 用 NumPy 实现 KNN 分类算法

**评估方式：** 代码验证 — KNN算法在测试集上准确率达到预期，向量化实现无显式循环

---

## 阶段 3 — 目标：掌握（预估 1.5 周）

**学习主题：**
- 性能优化（向量化/内存布局/C/Fortran顺序）
- Numba 加速 NumPy 运算
- 与 Pandas/TensorFlow 数据交互
- 高级多项式与拟合（polyfit/polyval/最小二乘）
- 大数组处理技巧（内存映射、分块处理）
- C 扩展原理（ctypes/cffi/NumPy C API）

**学习资源：**
- [Numba 官方文档](https://numba.readthedocs.io/) — 官方文档 · 免费 · 高级 · 英文
- [《Python高性能编程（第2版）》](https://book.douban.com/subject/35820591/) — 书籍 · 付费 · 高级 · 中文

**练习项目：**
- 优化大规模矩阵运算性能

**评估方式：** 性能对比 — 优化后的矩阵运算相比纯Python版本提速100倍以上，有基准测试报告

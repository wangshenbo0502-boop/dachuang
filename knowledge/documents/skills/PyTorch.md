---
title: PyTorch
category: skills
tags: [AI, 深度学习, Python, 框架]
source: skill_improvement.json
date: 2026-07-28
---

# PyTorch

> 当前学术界和工业界最主流的深度学习框架，API 设计直观 Pythonic，动态计算图灵活方便。AI 岗位必会框架。

- **就业影响**: 高
- **前置技能**: Python, NumPy
- **关联系能**: TensorFlow, 机器学习, 深度学习

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- Tensor 张量操作
- 自动求导(autograd)
- Dataset 与 DataLoader
- nn.Module 搭建网络
- 损失函数与优化器
- 训练循环编写

**学习资源：**
- [PyTorch 官方教程（60分钟入门）](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html) — 官方文档 · 免费 · 入门 · 英文
- [d2l.ai PyTorch 版](https://zh.d2l.ai/) — 在线课程 · 免费 · 入门 · 中文

**练习项目：**
- 用 PyTorch 从零写一个 2 层 MLP 训练 MNIST

**评估方式：** 独立完成 — 训练循环完整（forward→loss→backward→optimizer.step），模型收敛验证集准确率 > 90%

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- GPU 训练(.to(device))
- 自定义 Dataset/DataLoader
- 学习率调度器
- TensorBoard 可视化
- 模型保存与加载(checkpoint)
- 混合精度训练(AMP)

**学习资源：**
- [PyTorch 中级教程](https://pytorch.org/tutorials/#intermediate) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 把 MNIST 训练改为 GPU + 混合精度 + TensorBoard 记录

**评估方式：** 代码审查 — GPU 利用率 > 70%，训练日志能在 TensorBoard 中查看

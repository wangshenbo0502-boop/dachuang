---
title: AI 图像分类应用
category: AI
difficulty: 进阶
tech_stack: [Python, PyTorch, Flask/FastAPI, Docker]
estimated_hours: 60
source: projects.json
date: 2026-07-28
---

# AI 图像分类应用

## 项目概述

训练一个图像分类模型并用 Web API 部署，让用户可以通过上传图片获取分类结果。完整的端到端 AI 项目经验。

## 核心功能

- 使用预训练 ResNet 做迁移学习
- 数据增强（翻转/旋转/色彩变换）
- 模型保存为 ONNX 格式
- FastAPI 提供推理接口
- 返回 Top-3 分类结果及置信度
- Docker 部署

## 技术收获

- 迁移学习的实践应用
- GPU 训练流程
- 模型格式转换和优化
- AI 模型的 API 化部署
- 处理大文件上传

## 适合人群

有深度学习基础、想找AI岗位的同学

## 前置技能

- Python
- PyTorch基础
- CNN基础

# 技术难点与面试展开点

**数据与训练侧**的三个关键难点：① 数据不足与不均衡——讲解迁移学习（ImageNet 预训练 + 微调）为何是小数据场景的标准解法，以及类别不均衡时的加权采样/加权损失（focal loss）；② 过拟合控制——数据增强（随机裁剪/翻转/色彩抖动，MixUp/CutMix 进阶）、Dropout、早停的组合使用，能说出验证集指标与训练集指标的差距分析过程；③ 训练工程——混合精度（AMP）加速、学习率调度（warmup+cosine）、断点续训（checkpoint）。

**工程部署侧**是区别于课程作业的加分项：训练好的模型如何服务化——Flask/FastAPI 封装推理接口、模型导出（ONNX/TorchScript）脱离 Python 依赖、前端上传图片的预处理与服务端保持一致（resize/normalize 参数对齐）、推理耗时优化（batch、量化）。端侧方向可讲 TF Lite/NCNN 的量化部署。

**面试高频问题**：卷积的运算过程与参数量计算、ResNet 为什么能训得深、迁移学习何时该冻结底层、softmax 与交叉熵的配合、如何定位"训练 loss 下降但验证准确率不升"的问题。简历写法建议突出量化结果：数据集规模、准确率提升幅度（如"迁移学习+数据增强将 Top-1 准确率从 78% 提升至 94%"）、推理耗时。

# 项目演进路线与推荐资源

**演进路线**：基础版（PyTorch + 预训练 ResNet 微调 + FastAPI 接口）→ 进阶版（数据增强与不均衡处理、准确率对比实验、ONNX 导出）→ 完整版（前端上传页面 + Docker 部署 + 推理耗时压测报告）。三个阶段的层层递进本身就是面试叙事的好素材。

**推荐资源**：PyTorch 官方 Tutorials（Image 分类标准流程）；动手学深度学习（d2l.ai）图像分类章节；HuggingFace Transformers（直接使用 timm 预训练模型库）；Paper With Code（SOTA 模型与复现入口）。

# Reference

1. GitHub. 相关开源项目与技术文档. github.com. 访问时间: 2026-09-13.
2. LeetCode. 力扣题库（项目相关算法题）. leetcode.cn. 访问时间: 2026-09-13.

---
title: TensorFlow
category: skills
tags: [AI, 深度学习, Python, 框架]
source: skill_improvement.json
date: 2026-07-28
---

# TensorFlow

> Google 开源的深度学习框架，工业界部署广泛（TF Serving、TF Lite）。与 PyTorch 二选一掌握即可，工业界岗位有时特别要求。

- **就业影响**: 中
- **前置技能**: Python, NumPy
- **关联系能**: PyTorch, 深度学习

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- TensorFlow 2.x 与 Keras API
- Sequential/Functional API 搭建模型
- model.compile/fit/evaluate
- 回调函数(EarlyStopping/ModelCheckpoint)
- TensorBoard

**学习资源：**
- [TensorFlow 官方教程](https://www.tensorflow.org/tutorials?hl=zh-cn) — 官方文档 · 免费 · 入门 · 中文

**练习项目：**
- 用 Keras 训练 CIFAR-10 图像分类模型

**评估方式：** 独立完成 — 训练曲线正常收敛，验证集准确率 > 70%

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- Keras 高阶 API（Model 子类化、自定义层）
- 模型训练与评估（自定义损失函数、自定义指标）
- 回调函数（LearningRateScheduler、ReduceLROnPlateau 等）
- 数据增强（tf.image、ImageDataGenerator、tf.data）
- 迁移学习（冻结层、微调特征提取）
- 预训练模型使用（MobileNet/ResNet/EfficientNet）
- 模型保存与加载（SavedModel/HDF5/Checkpoint）

**学习资源：**
- [TensorFlow 官方进阶教程](https://www.tensorflow.org/guide?hl=zh-cn) — 官方文档 · 免费 · 进阶 · 中文
- [《动手学深度学习（TensorFlow版）》](https://zh.d2l.ai/) — 在线教程 · 免费 · 进阶 · 中文

**练习项目：**
- 用迁移学习实现图像分类

**评估方式：** 性能验证 — 使用预训练模型微调后，在自定义数据集上验证集准确率 > 90%，训练过程可视化

---

## 阶段 3 — 目标：掌握（预估 4 周）

**学习主题：**
- 自定义模型与训练循环（tf.GradientTape、自定义训练步骤）
- 分布式训练（MirroredStrategy、MultiWorkerMirroredStrategy）
- TensorFlow Lite 移动端部署（模型转换、量化、移动端集成）
- TensorRT 加速推理（TensorRT 集成、FP16/INT8 优化）
- 模型量化与剪枝（训练后量化、感知量化、结构化剪枝）
- TF Serving 生产部署（模型服务化、REST/gRPC 接口、版本管理）
- TFLearn / Estimator API（高级封装、预制 Estimator）

**学习资源：**
- [TensorFlow Lite 官方文档](https://www.tensorflow.org/lite/guide?hl=zh-cn) — 官方文档 · 免费 · 高级 · 中文
- [《TensorFlow实战（第2版）》](https://book.douban.com/subject/35722911/) — 书籍 · 付费 · 高级 · 中文

**练习项目：**
- 部署模型到移动端并优化推理速度

**评估方式：** 部署验证 — 模型成功部署到移动端，推理速度提升3倍以上，精度损失控制在可接受范围内

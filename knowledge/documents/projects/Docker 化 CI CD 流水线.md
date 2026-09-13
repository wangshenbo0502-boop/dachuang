---
title: Docker 化 CI/CD 流水线
category: 工程
difficulty: 挑战
tech_stack: [Docker, Docker Compose, GitHub Actions, Nginx]
estimated_hours: 40
source: projects.json
date: 2026-07-28
---

# Docker 化 CI/CD 流水线

## 项目概述

为一个已有的前后端项目搭建完整的 Docker 化 CI/CD 流水线。DevOps 方向的核心实践，所有岗位都加分。

## 核心功能

- 前端 Dockerfile（多阶段构建）
- 后端 Dockerfile
- Nginx 反向代理配置
- docker-compose 编排全服务
- GitHub Actions 自动构建+部署

## 技术收获

- Docker 多阶段构建减小镜像体积
- docker-compose 编排多服务
- CI/CD 流水线原理
- GitHub Actions 实战
- 环境变量管理

## 适合人群

已有项目、想学习部署的同学

## 前置技能

- Docker基础
- Git
- 有任一可部署的项目

# 技术难点与面试展开点

**流水线的阶段设计**是主线：代码提交（Webhook 触发）→ 静态检查（lint/单测，失败快速反馈）→ 构建（Docker 多阶段构建产物镜像）→ 镜像推送（打 tag 规范：commit sha + 语义化版本）→ 部署（开发环境自动、生产环境审批后手动触发）→ 回滚预案（按 tag 回退上一版本）。"为什么每个阶段都要 Docker 化"——环境一致性：构建、测试、运行使用同一基础镜像，消灭"我本地是好的"。

**构建优化的真实工程价值**最能打动面试官：Dockerfile 层缓存策略（依赖清单先于源码 COPY）、多阶段构建减小镜像、CI 中缓存 Maven/npm 依赖目录、并行执行无依赖的阶段。能给出量化对比（如"构建时间从 8 分钟优化到 2 分钟"）即是简历亮点。

**安全与治理**：镜像漏洞扫描（Trivy）纳入流水线门禁、密钥管理（不硬编码在 YAML，用 CI 的 secrets 机制）、制品库权限（私有 registry）、部署凭据最小化。面试高频：CI 与 CD 的区别、蓝绿部署与滚动部署/金丝雀发布的取舍、Docker 层缓存原理、如何在 K8s 中实现金丝雀、回滚策略设计。

# 项目演进路线与推荐资源

**演进路线**：基础版（GitHub Actions 构建 + 推送镜像到 registry）→ 进阶版（多环境部署、Trivy 镜像扫描门禁、构建缓存优化）→ 完整版（K8s 金丝雀发布或 Docker Compose 蓝绿切换、失败自动回滚、构建时长对比报告）。

**推荐资源**：GitHub Actions 官方文档（workflow 语法与缓存机制）；Docker 官方文档（多阶段构建与 BuildKit）；Trivy 官方文档（漏洞扫描）；《Continuous Delivery》（Jez Humble，CI/CD 理论经典）。

# 简历定位

适合后端/运维/DevOps 方向。定位示例："基于 GitHub Actions 与 Docker 多阶段构建搭建全自动 CI/CD，接入镜像漏洞扫描门禁，构建时长由 8 分钟优化至 2 分钟"。体现工程效率意识，是校招生相对稀缺的 DevOps 实战背书。

# Reference

1. GitHub. 相关开源项目与技术文档. github.com. 访问时间: 2026-09-13.
2. LeetCode. 力扣题库（项目相关算法题）. leetcode.cn. 访问时间: 2026-09-13.

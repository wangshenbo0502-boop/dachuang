---
title: Docker
category: skills
tags: [工具, 容器化, DevOps]
source: skill_improvement.json
date: 2026-07-28
---

# Docker

> 容器化部署的标准方案。解决了"在我电脑上能跑"的经典痛点。全栈和运维岗位的加分项。

- **就业影响**: 中
- **前置技能**: Linux 基础操作
- **关联系能**: Git, Node.js, Java

---

## 阶段 1 — 目标：了解（预估 1 周）

**学习主题：**
- Docker 安装
- 镜像与容器概念
- docker run / ps / stop / rm
- 端口映射
- 数据卷挂载
- Dockerfile 编写基础

**学习资源：**
- [Docker 从入门到实践（中文）](https://yeasy.gitbook.io/docker_practice/) — 在线课程 · 免费 · 入门 · 中文
- [Docker 官方文档](https://docs.docker.com/) — 官方文档 · 免费 · 入门 · 英文

**练习项目：**
- 把你之前的任何一个项目用 Dockerfile 打包成镜像并运行

**评估方式：** 实操 — docker run 后项目能正常访问，端口映射正确

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- docker-compose 多容器编排
- 多阶段构建(Multi-stage Build)
- 镜像优化(体积/Tag)
- 网络模式(bridge/host)
- Docker Hub 发布

**学习资源：**
- [Docker Compose 官方文档](https://docs.docker.com/compose/) — 官方文档 · 免费 · 进阶 · 英文

**练习项目：**
- 用 docker-compose 编排前端+Nginx+后端+MySQL+Redis 一键启动

**评估方式：** 实操 — docker-compose up 一键启动整个项目栈，5 个服务均能正常通信

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

# 原理与面试高频

Docker 的核心是操作系统级虚拟化：通过 Linux 的 **namespace**（隔离进程视图：PID、网络、挂载点等）与 **cgroup**（限制 CPU/内存等资源配额）实现进程级隔离，再借助 **overlay2** 联合文件系统实现镜像的分层存储。容器与虚拟机的本质区别在于：虚拟机虚拟的是完整硬件并运行独立内核，容器共享宿主机内核、以进程形态存在，因此启动以秒计、开销极小。

镜像采用分层只读结构，容器运行时在顶部叠加一个可写层。分层带来两大工程价值：**构建缓存**（Dockerfile 指令顺序影响缓存命中率，应把不常变动的步骤放在前面）与 **层复用**（多个镜像共享基础层，节省磁盘与传输）。生产构建的标准实践是**多阶段构建**——第一阶段用完整 SDK 编译，第二阶段仅复制产物到精简运行时镜像（如 eclipse-temurin→alpine/distroless），可将 Java 前端等镜像体积缩减一个数量级。

安全方面需关注：避免以 root 运行（USER 指令/rootless 模式）、不把密钥写进镜像与层、用 trivy/grype 等工具做镜像漏洞扫描、启用内容信任。数据持久化用 volume（由 Docker 管理）而非 bind mount（依赖宿主路径）。

面试高频：容器与虚拟机区别（namespace/cgroup）、镜像分层原理、Dockerfile 优化、volume 与 bind mount 区别、容器网络模式（bridge/host/overlay）、如何排查容器内网络问题（exec 进容器、nslookup、curl 检查连通性）。

# Reference

1. Docker Inc. Docker 官方文档（含 Compose）. docs.docker.com. 访问时间: 2026-09-13. https://docs.docker.com/
2. Docker Inc. Dockerfile Reference（指令规范）. docs.docker.com/reference/dockerfile. 访问时间: 2026-09-13.
3. Kubernetes. Kubernetes 官方文档（容器编排进阶）. kubernetes.io/zh-cn/docs. 访问时间: 2026-09-13.

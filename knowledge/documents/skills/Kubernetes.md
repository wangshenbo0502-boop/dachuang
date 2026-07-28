---
title: Kubernetes
category: skills
tags: [云原生, 容器编排, DevOps, 运维]
source: skill_improvement.json
date: 2026-07-28
---

# Kubernetes

> 容器编排的事实标准，云原生时代的"操作系统"，DevOps/SRE 必备技能。

- **就业影响**: 高
- **前置技能**: Docker, Linux
- **关联系能**: DevOps, 云原生, Helm, Prometheus

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- 核心概念（Pod/Service/Deployment/ConfigMap/Secret）
- kubectl 命令行工具使用
- YAML 资源定义与编写
- Namespace 命名空间管理
- 基本网络（ClusterIP/NodePort/LoadBalancer）
- 卷与持久化基础（emptyDir/hostPath）

**学习资源：**
- [Kubernetes 官方文档](https://kubernetes.io/zh-cn/docs/home/) — 官方文档 · 免费 · 入门 · 中文
- [《Kubernetes in Action（第2版）》](https://book.douban.com/subject/35722911/) — 书籍 · 付费 · 入门 · 中文

**练习项目：**
- 用 Minikube 部署一个简单的 Web 应用（前端+后端+数据库）

**评估方式：** 实操 — 能独立创建 Deployment、Service，通过 kubectl 管理应用生命周期，应用可正常访问

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- Ingress 与流量管理（Ingress Controller、路由规则、TLS）
- 存储（PV/PVC/StorageClass、动态供应）
- RBAC 权限控制（Role/ClusterRole、ServiceAccount）
- Helm 包管理（Chart 编写、仓库管理、常用 Chart 使用）
- HPA 自动扩缩容（CPU/内存/自定义指标）
- 调度策略（节点选择、亲和性、污点与容忍）

**学习资源：**
- [Helm 官方文档](https://helm.sh/zh/docs/) — 官方文档 · 免费 · 进阶 · 中文
- [《Kubernetes权威指南（第6版）》](https://book.douban.com/subject/36502280/) — 书籍 · 付费 · 进阶 · 中文

**练习项目：**
- 用 Helm 部署完整的微服务应用，配置 Ingress 和持久化存储

**评估方式：** 实操 — 微服务完整部署，Ingress 路由正确，数据持久化有效，RBAC 权限配置合理

---

## 阶段 3 — 目标：掌握（预估 4 周）

**学习主题：**
- 生产级集群搭建（kubeadm/二进制、多 Master 高可用）
- 高可用架构（etcd 集群、控制平面高可用）
- 性能调优（参数调优、资源限制、QoS 等级）
- 网络插件（Cilium/Calico 原理与选型）
- 服务网格（Istio 架构、流量管理、可观测性）
- K8s 安全（Pod 安全策略、网络策略、镜像安全）
- Operator 开发（CRD、Controller、Operator SDK）
- CKA/CKS 认证备考

**学习资源：**
- [Istio 官方文档](https://istio.io/latest/zh/docs/) — 官方文档 · 免费 · 高级 · 中文
- [《云原生模式》](https://book.douban.com/subject/35273714/) — 书籍 · 付费 · 高级 · 中文

**练习项目：**
- 搭建生产级高可用 K8s 集群，集成 Istio 服务网格，设计完整的 CI/CD 流水线

**评估方式：** 架构评审 — 集群高可用、安全合规、可观测性完善，具备故障自愈能力，有完整的架构设计文档

---

**来源：** CNCF 2025 云原生报告、Kubernetes 官方文档、掘金云原生专栏、猎聘运维岗位 JD（访问时间：2026-07-28）

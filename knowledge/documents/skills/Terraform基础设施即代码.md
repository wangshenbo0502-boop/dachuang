---
title: Terraform基础设施即代码
category: skills
tags: [IaC, 云原生, DevOps, 自动化]
source: skill_improvement.json
date: 2026-07-28
---

# Terraform基础设施即代码

> 基础设施即代码（IaC）的事实标准，通过代码定义和管理云资源，实现自动化部署。

- **就业影响**: 中高
- **前置技能**: 云计算基础, Linux
- **关联系能**: Kubernetes, DevOps, 云原生, Ansible

---

## 阶段 1 — 目标：了解（预估 1.5 周）

**学习主题：**
- IaC 概念与 Terraform 核心原理
- Terraform 安装与基本命令
- HCL 语法基础（变量、输出、资源、数据源）
- 基本资源定义（VPC/ECS/OSS 等云资源）
- State 管理（本地 state、state 命令）
- plan/apply/destroy 工作流

**学习资源：**
- [Terraform 官方入门教程](https://developer.hashicorp.com/terraform/tutorials/aws-get-started) — 官方教程 · 免费 · 入门 · 英文
- [阿里云 Terraform 最佳实践](https://help.aliyun.com/product/95817.html) — 官方文档 · 免费 · 入门 · 中文

**练习项目：**
- 用 Terraform 在阿里云/AWS 上创建 VPC + ECS + 安全组的基础网络环境

**评估方式：** 实操 — 能独立编写 Terraform 配置，成功创建云资源，理解 state 文件作用，能正确销毁资源

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- 模块化设计（Module 编写与引用、模块版本管理）
- 变量与输出（复杂类型、变量验证、敏感数据）
- 多环境管理（Workspace 工作区、目录结构设计）
- Provider 使用（阿里云/AWS Provider、Provider 版本锁定）
- Remote State（远程状态存储、状态锁、团队协作）
- 常用模块编写（VPC 模块、ECS 模块、RDS 模块）

**学习资源：**
- [Terraform 官方文档](https://developer.hashicorp.com/terraform/docs) — 官方文档 · 免费 · 进阶 · 英文
- [《Terraform: Up & Running（第3版）》](https://book.douban.com/subject/36130267/) — 书籍 · 付费 · 进阶 · 中文

**练习项目：**
- 设计多环境（开发/测试/生产）基础设施架构，用模块化方式管理所有云资源

**评估方式：** 代码评审 — 模块划分合理，代码可复用，多环境配置清晰，remote state 配置正确，有版本控制

---

## 阶段 3 — 目标：掌握（预估 3 周）

**学习主题：**
- 企业级架构设计（多账号管理、组织架构、 Landing Zone）
- Terraform Cloud/Enterprise（远程运行、团队协作、策略即代码）
- CI/CD 集成（GitOps、Atlantis、自动化流水线）
- 安全与合规（Sentinel 策略、OPA/Rego、安全扫描）
- 大型项目最佳实践（目录结构、依赖管理、变更管理）
- 与 K8s/Ansible 协同（基础设施编排 + 配置管理 + 容器编排）
- Terraform 性能优化（并行度、target 应用、import 迁移）

**学习资源：**
- [Sentinel 官方文档](https://developer.hashicorp.com/sentinel/docs) — 官方文档 · 免费 · 高级 · 英文
- [HashiCorp 官方最佳实践](https://developer.hashicorp.com/terraform/language/best-practices) — 官方文档 · 免费 · 高级 · 英文

**练习项目：**
- 为企业设计完整的 IaC 平台，集成 CI/CD 流水线、策略检查、多环境管理，实现基础设施自助服务

**评估方式：** 架构评审 — IaC 平台设计完整，安全合规可控，支持自助服务和审计追溯，有完整的设计文档

---

**来源：** HashiCorp 官方文档、CSDN 云原生专栏、猎聘云架构师 JD、阿里云最佳实践（访问时间：2026-07-28）

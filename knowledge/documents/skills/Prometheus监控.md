---
title: Prometheus监控
category: skills
tags: [监控, 云原生, DevOps, 可观测性]
source: skill_improvement.json
date: 2026-07-28
---

# Prometheus监控

> 云原生时代的监控标准，CNCF 毕业项目，与 Grafana 组成可观测性核心。

- **就业影响**: 中高
- **前置技能**: Linux, 基础运维
- **关联系能**: Kubernetes, Grafana, Loki, DevOps

---

## 阶段 1 — 目标：了解（预估 1.5 周）

**学习主题：**
- Prometheus 架构与安装部署
- PromQL 基础语法（查询函数、运算符）
- 指标类型（Counter/Gauge/Histogram/Summary）
- Grafana 可视化仪表盘搭建
- 基础告警配置（Alertmanager 入门）
- Node Exporter 主机监控

**学习资源：**
- [Prometheus 官方文档](https://prometheus.io/docs/introduction/overview/) — 官方文档 · 免费 · 入门 · 英文
- [Grafana 官方文档](https://grafana.com/docs/grafana/latest/) — 官方文档 · 免费 · 入门 · 英文

**练习项目：**
- 搭建 Prometheus + Grafana 监控系统，监控主机 CPU/内存/磁盘并配置告警

**评估方式：** 实操 — 能独立部署 Prometheus 和 Grafana，创建仪表盘，配置邮件/钉钉告警，告警能正常触发

---

## 阶段 2 — 目标：熟悉（预估 2 周）

**学习主题：**
- PromQL 进阶（聚合函数、区间向量、rate/irate/increase）
- 服务发现（静态配置、文件发现、Consul/K8s 服务发现）
- Exporter 使用（MySQL Exporter/Redis Exporter/Nginx Exporter 等）
- 告警规则设计（阈值设定、告警分级、抑制与静默）
- Alertmanager 高级配置（路由树、分组、通知模板）
- 记录规则（Recording Rules 优化查询性能）

**学习资源：**
- [《Prometheus监控实战》](https://book.douban.com/subject/35031588/) — 书籍 · 付费 · 进阶 · 中文
- [Prometheus 中文文档](https://www.prometheus.wang/) — 社区文档 · 免费 · 进阶 · 中文

**练习项目：**
- 为一套完整的应用栈（主机+数据库+中间件+应用）设计监控方案，配置分级告警

**评估方式：** 方案评审 — 监控覆盖全面，告警规则合理，有告警分级和升级策略，仪表盘信息清晰

---

## 阶段 3 — 目标：掌握（预估 3 周）

**学习主题：**
- 高可用部署（Prometheus 联邦集群、Alertmanager 集群）
- 联邦集群（Federation、跨集群监控）
- 长期存储（Thanos/Mimir 架构与部署）
- 性能调优（指标基数控制、内存优化、查询优化）
- 自定义 Exporter 开发（Prometheus Client 库、Collector 编写）
- 与 K8s 深度集成（kube-state-metrics、metrics-server、Prometheus Operator）
- 可观测性体系建设（监控+日志+链路追踪三位一体）

**学习资源：**
- [Thanos 官方文档](https://thanos.io/tip/thanos/getting-started.md/) — 官方文档 · 免费 · 高级 · 英文
- [《云原生可观测性》](https://book.douban.com/subject/36092226/) — 书籍 · 付费 · 高级 · 中文

**练习项目：**
- 设计并实现企业级可观测性平台，集成 Prometheus + Loki + Jaeger，支持多集群监控

**评估方式：** 架构评审 — 平台高可用、可扩展、监控告警日志链路一体化，有完整的设计文档和运维手册

---

**来源：** Prometheus 官方文档、CNCF 可观测性报告、腾讯云监控、阿里云 Prometheus（访问时间：2026-07-28）

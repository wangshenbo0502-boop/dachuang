---
title: Java
category: skills
tags: [编程语言, 后端, 企业级]
source: skill_improvement.json
date: 2026-07-28
---

# Java

> 企业级开发首选语言，银行/电商/政务系统大量使用。就业市场最大、最稳定的后端语言，岗位需求常年第一。

- **就业影响**: 高
- **前置技能**: 无
- **关联系能**: Spring Boot, MySQL, Redis

---

## 阶段 1 — 目标：了解（预估 3 周）

**学习主题：**
- JDK安装与环境配置
- 基本语法(变量/循环/条件)
- 面向对象(类/对象/封装/继承/多态)
- 接口与抽象类
- 异常处理
- 集合框架(List/Set/Map)
- IO流

**学习资源：**
- [廖雪峰 Java 教程](https://www.liaoxuefeng.com/wiki/1252599548343744) — 在线课程 · 免费 · 入门 · 中文
- [《Java 核心技术 卷I》](https://book.douban.com/subject/34898994/) — 书籍 · 付费 · 入门 · 中文

**练习项目：**
- 用集合+IO写一个带搜索功能的联系人管理系统

**评估方式：** 独立完成 — 面向对象设计（至少3个类），数据可持久化到文件

---

## 阶段 2 — 目标：熟悉（预估 4 周）

**学习主题：**
- Maven/Gradle 构建工具
- 泛型
- Lambda 表达式与 Stream API
- JDBC 数据库连接
- Servlet 基础
- Spring Boot 入门（DI/IOC/自动配置）
- RESTful API开发
- JUnit 单元测试

**学习资源：**
- [Spring Boot 官方文档](https://spring.io/projects/spring-boot) — 官方文档 · 免费 · 进阶 · 英文
- [《Spring 实战（第6版）》](https://book.douban.com/subject/36092226/) — 书籍 · 付费 · 进阶 · 中文

**练习项目：**
- 用 Spring Boot + MySQL 写一个带用户认证的博客系统后端 API

**评估方式：** 代码审查 — 三层架构(Controller/Service/Repository)清晰，有基本的异常处理和参数校验

---

## 阶段 3 — 目标：掌握（预估 4 周）

**学习主题：**
- Spring Security 认证授权
- MyBatis / MyBatis-Plus
- Redis 缓存集成
- 消息队列(RabbitMQ)
- 微服务基础(Spring Cloud)
- Docker 容器化部署

**学习资源：**
- [《Spring 微服务实战》](https://book.douban.com/subject/30306593/) — 书籍 · 付费 · 高级 · 中文

**练习项目：**
- 为博客系统加入 Spring Security + Redis + Docker 部署

**评估方式：** 部署验证 — 系统可通过 docker-compose 一键启动，JWT 认证完整

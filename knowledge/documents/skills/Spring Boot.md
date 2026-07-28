---
title: Spring Boot
category: skills
tags: [框架, Java, 后端, 微服务]
source: skill_improvement.json
date: 2026-07-28
---

# Spring Boot

> Java 生态最主流的微服务框架，大幅简化了 Spring 应用的搭建和开发。Java 后端岗位的几乎标配要求。

- **就业影响**: 高
- **前置技能**: Java, MySQL
- **关联系能**: Redis, Docker

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- Spring Boot 项目创建(Spring Initializr)
- 自动配置原理
- application.yml 配置
- Controller/RestController
- Service/Repository 分层
- 参数校验(@Validated)

**学习资源：**
- [Spring Boot 官方文档](https://docs.spring.io/spring-boot/documentation.html) — 官方文档 · 免费 · 入门 · 英文
- [Baeldung Spring Boot 教程](https://www.baeldung.com/spring-boot) — 在线课程 · 免费 · 入门 · 英文

**练习项目：**
- 搭建一个学生成绩管理系统 API（CRUD + 分页查询）

**评估方式：** 接口测试 — 使用 Postman 测试所有接口正常，分页返回正确

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- Spring Data JPA / MyBatis-Plus
- 全局异常处理(@ControllerAdvice)
- AOP 日志
- 定时任务(@Scheduled)
- 文件上传下载
- Swagger/OpenAPI 文档

**学习资源：**
- [MyBatis-Plus 官方文档](https://baomidou.com/) — 官方文档 · 免费 · 进阶 · 中文

**练习项目：**
- 给成绩管理系统加全局异常处理+Swagger文档+操作日志（AOP）

**评估方式：** 代码审查 — Swagger 接口文档完整可交互，异常信息对用户友好

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

# 原理与面试高频

Spring Boot 的核心价值是**约定优于配置 + 自动装配**。自动装配原理是面试第一高频：@SpringBootApplication 复合 @EnableAutoConfiguration，后者通过 spring.factories / AutoConfiguration.imports（Boot 3 机制）加载候选配置类，再由 @Conditional 系列注解（@ConditionalOnClass、@ConditionalOnMissingBean 等）按条件筛选生效——"为什么引入 starter 依赖功能就自动配置好了"的标准答案链。起步依赖（starter）通过 Maven 传递依赖解决版本对齐；内嵌 Tomcat 让应用以 java -jar 自包含运行，为容器化铺路。

Actuator 提供健康检查、指标暴露（/actuator/prometheus 对接 Prometheus），是生产可观测性的入口。**Spring Boot 3 的两个重点**：基于 Spring Framework 6 要求 Java 17+；引入 **AOT（提前编译）**支持 GraalVM Native Image，启动时间从秒级降到毫秒级、内存减半，契合 Serverless 场景。

与微服务的关系要能分清：Spring Boot 解决单体应用快速搭建，Spring Cloud（及其 Alibaba 实现：Nacos 注册配置中心、Sentinel 限流熔断、OpenFeign 声明调用、Gateway 网关）解决服务治理。事务传播行为（REQUIRED/REQUIRES_NEW/NESTED）、@Transactional 失效场景（自调用、非 public、异常被吞）是 Spring 面试的常驻考点，配合 AOP 动态代理原理（JDK 动态代理与 CGLIB）构成完整答案链。

# Reference

1. VMware Tanzu. Spring Boot 官方文档. docs.spring.io/spring-boot. 访问时间: 2026-09-13. https://docs.spring.io/spring-boot/index.html
2. VMware Tanzu. Spring Framework 官方文档（IoC/AOP 原理）. docs.spring.io/spring-framework. 访问时间: 2026-09-13.
3. Alibaba. Spring Cloud Alibaba 官方文档（Nacos/Sentinel）. sca.aliyun.com. 访问时间: 2026-09-13.

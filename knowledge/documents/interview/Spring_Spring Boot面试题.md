---
title: "Spring/Spring Boot面试题（20题）"
category: "面试题"
type: "Java后端"
difficulty: "中等"
tags: ["Spring", "Spring Boot", "IOC", "AOP", "自动装配"]
source: ["Spring官方文档", "Spring Boot实战", "美团技术团队博客"]
last_update: "2026-07-28"
---

# Spring/Spring Boot面试题（20题）

> 本文档涵盖Spring和Spring Boot的核心知识点，包括IOC、AOP、Bean生命周期、事务、自动装配、Spring MVC等重点内容，是Java后端面试的必考内容。

---

## Q1: Spring的IOC和DI是什么

**考察点**: IOC和DI的概念、区别、IOC容器的作用

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. IOC（Inversion of Control，控制反转）

**概念**：IOC 是一种设计思想，指的是将对象的创建、对象之间的依赖关系的管理权，从代码中转移到外部容器（Spring 容器）中。

简单说：**以前是自己 new 对象，现在是 Spring 帮我们创建和管理对象。**

**"反转"了什么**：
- 传统方式：应用程序主动创建依赖对象（正控）
- IOC 方式：容器创建对象，应用被动接受（反转）

**IOC 容器**：
- Spring 提供的 IOC 容器是实现 IOC 的载体
- 负责创建、管理、装配对象
- 常见的容器实现：
  - BeanFactory：最基础的容器
  - ApplicationContext：更高级的容器，功能更丰富（推荐）

**IOC 的好处**：
1. **解耦**：对象之间的依赖关系由容器管理，降低耦合度
2. **便于管理**：统一管理对象的创建和生命周期
3. **提高可测试性**：可以方便地替换实现
4. **提高可维护性**：修改依赖不需要改代码，改配置就行

### 2. DI（Dependency Injection，依赖注入）

**概念**：DI 是 IOC 的一种实现方式，指的是容器在创建对象时，将对象依赖的其他对象注入进去。

简单说：**对象的依赖由容器注入，不用自己去找。**

**三种注入方式**：

**（1）构造器注入**
```java
public class UserService {
    private UserDao userDao;
    
    // 构造器注入
    public UserService(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

**（2）Setter 方法注入**
```java
public class UserService {
    private UserDao userDao;
    
    // Setter方法注入
    public void setUserDao(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

**（3）字段注入（@Autowired）**
```java
@Service
public class UserService {
    @Autowired // 字段注入
    private UserDao userDao;
}
```

### 3. IOC 和 DI 的关系

- **IOC 是目的**：控制反转，把对象管理权交给容器
- **DI 是手段**：依赖注入，是实现 IOC 的一种方式

IOC 可以通过多种方式实现，DI 是最常用的一种。Spring 就是通过 DI 来实现 IOC 的。

还有一种 IOC 的实现方式叫依赖查找（Dependency Lookup），比如 JNDI 就是这种方式，但比较少用。

### 4. Spring IOC 的实现原理

Spring IOC 容器的核心：
1. **配置解析**：读取 XML、注解、Java 配置类等配置信息
2. **BeanDefinition**：将配置信息解析成 BeanDefinition 对象，包含 Bean 的定义信息
3. **Bean 工厂**：根据 BeanDefinition 创建和管理 Bean
4. **依赖注入**：解析 Bean 之间的依赖关系，完成注入

**核心组件**：
- BeanFactory：Bean 工厂，最基础的 IOC 容器
- ApplicationContext：应用上下文，更高级的容器
- BeanDefinition：Bean 的定义信息
- BeanPostProcessor：Bean 后置处理器

**答案解析**:

IOC 和 DI 是 Spring 最基础的概念，也是面试必考题。

IOC 是一种思想，核心是把对象的创建和管理权交给容器。DI 是实现 IOC 的方式，通过注入依赖来实现控制反转。

IOC 的好处是解耦，让对象之间的依赖关系由容器管理，代码更灵活，更易测试。

三种注入方式各有优缺点：
- 构造器注入：保证依赖不可变，保证依赖不为空，推荐使用
- Setter 注入：灵活，可以后期修改
- 字段注入：最简单，但不利于测试，不推荐

Spring 推荐使用构造器注入，因为它能保证依赖的不可变性和完整性。

**扩展问题**:
- 什么是 IOC？什么是 DI？
- IOC 和 DI 的关系？
- IOC 有什么好处？
- 依赖注入有哪几种方式？
- BeanFactory 和 ApplicationContext 的区别？

---

## Q2: Spring Bean的生命周期

**考察点**: Bean从创建到销毁的完整过程、各种扩展点

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. Bean 的生命周期概述

Spring Bean 的生命周期是指 Bean 从创建到销毁的整个过程。

完整的生命周期分为以下几个阶段：
1. 实例化（Instantiation）
2. 属性赋值（Populate）
3. 初始化（Initialization）
4. 使用（In Use）
5. 销毁（Destruction）

### 2. 详细生命周期流程

#### 阶段1：实例化 Bean

- 调用构造方法创建 Bean 实例
- 对应 BeanPostProcessor 的 postProcessBeforeInstantiation（实例化前）
- 和 postProcessAfterInstantiation（实例化后）

#### 阶段2：属性赋值（依赖注入）

- 为 Bean 的属性赋值，注入依赖
- 处理 @Autowired、@Value 等注解
- 对应 InstantiationAwareBeanPostProcessor 的 postProcessProperties

#### 阶段3：初始化 Bean

初始化阶段有很多扩展点：

**（1）Aware 接口回调**
- BeanNameAware：设置 Bean 的名称
- BeanClassLoaderAware：设置类加载器
- BeanFactoryAware：设置 BeanFactory
- ApplicationContextAware：设置 ApplicationContext
- 等等

**（2）BeanPostProcessor 前置处理**
- 执行所有 BeanPostProcessor 的 postProcessBeforeInitialization 方法
- 在初始化方法执行前调用

**（3）初始化方法**
- 如果 Bean 实现了 InitializingBean 接口，执行 afterPropertiesSet 方法
- 如果配置了 init-method（或 @PostConstruct），执行自定义初始化方法

**（4）BeanPostProcessor 后置处理**
- 执行所有 BeanPostProcessor 的 postProcessAfterInitialization 方法
- 在初始化方法执行后调用
- **AOP 就是在这里完成代理的**

#### 阶段4：使用 Bean

- Bean 创建完成，可以使用了
- 从容器中获取 Bean，执行业务逻辑

#### 阶段5：销毁 Bean

容器关闭时，销毁 Bean：

- 如果 Bean 实现了 DisposableBean 接口，执行 destroy 方法
- 如果配置了 destroy-method（或 @PreDestroy），执行自定义销毁方法

### 3. 生命周期流程图

```
实例化 Bean
    ↓
属性赋值（依赖注入）
    ↓
Aware 接口回调（BeanNameAware、BeanFactoryAware等）
    ↓
BeanPostProcessor.postProcessBeforeInitialization
    ↓
InitializingBean.afterPropertiesSet
    ↓
init-method（@PostConstruct）
    ↓
BeanPostProcessor.postProcessAfterInitialization  ← AOP代理在这里
    ↓
Bean 就绪，可以使用
    ↓
容器关闭
    ↓
DisposableBean.destroy
    ↓
destroy-method（@PreDestroy）
    ↓
Bean 销毁
```

### 4. 重要的扩展点

**BeanPostProcessor**：
- Bean 后置处理器
- 在 Bean 初始化前后执行
- 非常重要，AOP、依赖注入等都是通过它实现的

**InitializingBean / DisposableBean**：
- 初始化回调和销毁回调
- 但建议用 @PostConstruct / @PreDestroy 注解，侵入性小

**Aware 接口**：
- 让 Bean 获取 Spring 容器的一些资源
- 如 BeanName、BeanFactory、ApplicationContext 等

### 5. BeanPostProcessor 的作用

BeanPostProcessor 是 Spring 扩展的核心，很多功能都是基于它实现的：

- **依赖注入**：@Autowired 注解的处理
- **AOP**：创建代理对象
- **注解处理**：@Value、@Resource 等
- **属性填充**：属性赋值

**答案解析**:

Spring Bean 的生命周期是面试高频考点，也是难点。

核心流程：实例化 → 属性赋值 → 初始化 → 使用 → 销毁。

初始化阶段最复杂，有很多扩展点：
1. Aware 回调
2. BeanPostProcessor 前置处理
3. InitializingBean.afterPropertiesSet
4. init-method
5. BeanPostProcessor 后置处理

BeanPostProcessor 是 Spring 最重要的扩展点之一，AOP 就是在 postProcessAfterInitialization 中完成的。

@PostConstruct 和 @PreDestroy 是 JSR-250 规范的注解，优先级比 InitializingBean 和 DisposableBean 高吗？不，@PostConstruct 是在 postProcessBeforeInitialization 阶段（CommonAnnotationBeanPostProcessor）执行的，在 InitializingBean 之前。

**扩展问题**:
- Bean 的生命周期是什么？
- BeanPostProcessor 有什么用？
- AOP 在哪个阶段完成？
- InitializingBean 和 init-method 的区别？
- Aware 接口有哪些？

---

## Q3: Spring Bean的作用域

**考察点**: 6种作用域的区别、singleton和prototype的区别

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. Bean 的 6 种作用域

Spring 有 6 种 Bean 作用域：

| 作用域 | 说明 | 适用场景 |
|--------|------|---------|
| singleton | 单例，整个容器中只有一个实例 | 默认，大部分 Bean 用这个 |
| prototype | 原型，每次获取都创建新实例 | 有状态的 Bean |
| request | 每次 HTTP 请求一个实例 | Web 应用 |
| session | 每个 Session 一个实例 | Web 应用 |
| application | 每个 ServletContext 一个实例 | Web 应用 |
| websocket | 每个 WebSocket 一个实例 | WebSocket 应用 |

前两种是通用的，后四种是 Web 环境下的。

### 2. singleton（单例）

- 默认作用域
- 整个 Spring 容器中只有一个 Bean 实例
- 容器启动时创建（默认），容器销毁时销毁
- 通过 `@Scope("singleton")` 或默认指定

```java
@Service
// 默认就是singleton
public class UserService {
    // ...
}
```

**注意**：单例 Bean 是线程不安全的，如果 Bean 中有成员变量，多线程下可能有问题。

### 3. prototype（原型）

- 每次获取 Bean 时创建一个新的实例
- 容器只负责创建，不负责完整的生命周期管理
- 销毁方法不会被调用（容器不跟踪 prototype Bean 的生命周期）

```java
@Service
@Scope("prototype")
public class UserService {
    // ...
}
```

**prototype Bean 的销毁**：
- Spring 容器不负责销毁 prototype Bean
- 如果需要清理资源，需要自己处理
- 因为容器创建后就不再跟踪了

### 4. Web 相关的作用域

**request**：
- 每次 HTTP 请求创建一个新的 Bean
- 请求结束，Bean 销毁

**session**：
- 每个 HTTP Session 创建一个 Bean
- Session 过期，Bean 销毁

**application**：
- 整个应用生命周期内只有一个 Bean
- 和 singleton 类似，但范围是 ServletContext，singleton 是 ApplicationContext

**websocket**：
- 每个 WebSocket 连接一个 Bean

### 5. singleton 和 prototype 的对比

| 特性 | singleton | prototype |
|------|-----------|-----------|
| 实例数量 | 一个 | 多个 |
| 创建时机 | 容器启动时（默认） | 每次获取时 |
| 线程安全 | 不安全（有成员变量时） | 相对安全 |
| 生命周期管理 | 完整管理 | 只管理创建，不管理销毁 |
| 销毁方法 | 会调用 | 不会调用 |
| 默认 | 是默认作用域 | 需要手动指定 |

### 6. 单例 Bean 的线程安全问题

单例 Bean 是线程不安全的，因为所有线程共享同一个实例。

**情况1：无状态 Bean（推荐）**
```java
@Service
public class UserService {
    // 没有成员变量，或成员变量也是无状态的
    // 方法中的局部变量是线程安全的
    public void doSomething() {
        int a = 10; // 局部变量，安全
    }
}
```
无状态 Bean 是线程安全的，因为没有共享的可变状态。

**情况2：有状态 Bean（不推荐）**
```java
@Service
public class CounterService {
    private int count; // 成员变量，线程不安全
    // ...
}
```
有状态 Bean 在线程不安全，需要加锁或使用 ThreadLocal，或者改成 prototype。

**答案解析**:

Bean 的作用域是 Spring 的基础知识点，必须掌握。

最常用的是 singleton（默认）和 prototype。

singleton 是默认的，整个容器只有一个实例。大部分 Bean 都是无状态的，用单例没问题。

prototype 每次获取都创建新实例，适合有状态的 Bean。但要注意 prototype Bean 的销毁方法不会被调用，需要自己清理资源。

Web 相关的作用域了解即可。

单例 Bean 的线程安全问题也是常考点：无状态的单例 Bean 是安全的，有状态的不安全。

**扩展问题**:
- Bean 有哪些作用域？
- singleton 和 prototype 的区别？
- 单例 Bean 是线程安全的吗？
- prototype Bean 的销毁方法会执行吗？
- request 和 session 作用域的区别？

---

## Q4: Spring AOP的实现原理

**考察点**: AOP的概念、JDK动态代理、CGLIB代理、织入时机

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 AOP

**AOP（Aspect-Oriented Programming，面向切面编程）**：

- 是对 OOP（面向对象编程）的补充
- 将横切关注点（如日志、事务、权限、监控等）从业务逻辑中分离出来
- 减少重复代码，降低耦合，提高可维护性

**核心概念**：
- **Aspect（切面）**：横切关注点的模块化，一个切面类
- **Join Point（连接点）**：程序执行过程中的某个点，如方法调用
- **Pointcut（切入点）**：匹配连接点的表达式，定义哪些方法被拦截
- **Advice（通知）**：在切入点执行的动作，如前置通知、后置通知等
- **Weaving（织入）**：将切面应用到目标对象的过程
- **Target（目标对象）**：被代理的对象

### 2. AOP 的两种代理方式

Spring AOP 是基于动态代理实现的，有两种代理方式：

#### （1）JDK 动态代理

**原理**：
- 基于 Java 的反射机制
- 目标类必须实现接口
- 运行时动态生成接口的实现类作为代理类

```java
// JDK动态代理示例
public class JdkProxy implements InvocationHandler {
    private Object target;
    
    public Object getProxy(Object target) {
        this.target = target;
        return Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            this
        );
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 前置通知
        Object result = method.invoke(target, args);
        // 后置通知
        return result;
    }
}
```

**特点**：
- 目标类必须实现接口
- 只能代理接口方法
- JDK 自带，不需要额外依赖
- 性能比 CGLIB 略好（创建快，调用快）

#### （2）CGLIB 动态代理

**原理**：
- 基于 ASM 字节码框架
- 生成目标类的子类作为代理类
- 目标类不需要实现接口

```java
// CGLIB动态代理示例
public class CglibProxy implements MethodInterceptor {
    private Object target;
    
    public Object getProxy(Object target) {
        this.target = target;
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(target.getClass());
        enhancer.setCallback(this);
        return enhancer.create();
    }
    
    @Override
    public Object intercept(Object obj, Method method, Object[] args, MethodProxy proxy) throws Throwable {
        // 前置通知
        Object result = proxy.invokeSuper(obj, args);
        // 后置通知
        return result;
    }
}
```

**特点**：
- 目标类不需要实现接口
- 通过继承目标类实现
- 不能代理 final 类和 final 方法
- 需要 CGLIB 库依赖

### 3. Spring 如何选择代理方式

Spring AOP 默认的策略：
- **如果目标类实现了接口，默认用 JDK 动态代理**
- **如果目标类没有实现接口，用 CGLIB 代理**

可以通过配置强制使用 CGLIB：
```java
@Configuration
@EnableAspectJAutoProxy(proxyTargetClass = true) // 强制使用CGLIB
public class AppConfig {
}
```

Spring Boot 2.x 开始，默认使用 CGLIB 代理（`spring.aop.proxy-target-class=true`）。

### 4. 织入时机

织入是将切面应用到目标对象的过程，有三种织入时机：

**（1）编译期织入**
- 在编译时把切面代码织入到 class 文件中
- 需要特殊的编译器，如 AspectJ 的 ajc 编译器
- 性能最好，但需要特殊编译

**（2）类加载期织入**
- 在类加载时织入
- 需要特殊的 ClassLoader
- 如 AspectJ 的 load-time weaving

**（3）运行期织入**
- 在运行时生成代理对象
- Spring AOP 就是运行期织入
- 最灵活，性能略差

Spring AOP 是**运行期织入**，通过动态代理在运行时生成代理对象。

### 5. AOP 的五种通知类型

1. **前置通知（@Before）**：目标方法执行前执行
2. **后置通知（@After）**：目标方法执行后执行（正常返回或异常都执行）
3. **返回通知（@AfterReturning）**：目标方法正常返回后执行
4. **异常通知（@AfterThrowing）**：目标方法抛出异常后执行
5. **环绕通知（@Around）**：包裹目标方法，最强大，可以控制方法是否执行

**答案解析**:

Spring AOP 的实现原理是面试高频考点，也是难点。

Spring AOP 基于动态代理实现，有 JDK 动态代理和 CGLIB 动态代理两种方式。

JDK 动态代理：基于接口，目标类必须实现接口。
CGLIB 动态代理：基于继承，目标类不需要接口，但不能代理 final 类。

Spring 默认的策略是：有接口用 JDK 代理，没接口用 CGLIB。Spring Boot 默认用 CGLIB。

AOP 的核心概念也要掌握：切面、切入点、通知、连接点、织入。

五种通知类型：前置、后置、返回、异常、环绕。环绕最强大。

AOP 的实现原理和 BeanPostProcessor 有关：AOP 代理是在 BeanPostProcessor 的 postProcessAfterInitialization 方法中创建的。

**扩展问题**:
- 什么是 AOP？有什么用？
- Spring AOP 的实现原理？
- JDK 动态代理和 CGLIB 的区别？
- Spring 默认用哪种代理？
- AOP 有哪些通知类型？

---

## Q5: Spring事务的传播行为

**考察点**: 7种传播行为、各传播行为的含义和适用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是事务传播行为

**事务传播行为**：当一个事务方法被另一个事务方法调用时，事务如何传播。

简单说：方法 A 有事务，方法 B 也有事务，A 调用 B 时，B 是加入 A 的事务，还是自己开一个新事务？

Spring 定义了 7 种事务传播行为，定义在 Propagation 枚举中。

### 2. 7 种传播行为

#### （1）REQUIRED（默认）

- **如果当前有事务，加入当前事务**
- **如果当前没有事务，创建一个新事务**
- 最常用，默认值

```
方法A（有事务）调用方法B → B加入A的事务
方法A（无事务）调用方法B → B创建新事务
```

适用场景：大多数场景。

#### （2）REQUIRES_NEW

- **总是创建一个新事务**
- 如果当前有事务，挂起当前事务
- 新事务和原事务相互独立

```
方法A（有事务）调用方法B → 挂起A的事务，B创建新事务
方法A（无事务）调用方法B → B创建新事务
```

适用场景：需要独立事务的操作，如日志记录、发消息等。即使主事务回滚，这些操作也要提交。

#### （3）SUPPORTS

- **如果当前有事务，加入当前事务**
- **如果当前没有事务，以非事务方式执行**

```
方法A（有事务）调用方法B → B加入A的事务
方法A（无事务）调用方法B → B非事务执行
```

适用场景：查询方法，有没有事务都行。

#### （4）NOT_SUPPORTED

- **以非事务方式执行**
- 如果当前有事务，挂起当前事务

```
方法A（有事务）调用方法B → 挂起A的事务，B非事务执行
方法A（无事务）调用方法B → B非事务执行
```

适用场景：不需要事务的方法，且不想影响外层事务。

#### （5）MANDATORY（强制的）

- **必须在一个事务中执行**
- 如果当前有事务，加入当前事务
- 如果当前没有事务，抛出异常

```
方法A（有事务）调用方法B → B加入A的事务
方法A（无事务）调用方法B → 抛出异常
```

适用场景：必须在事务中执行的方法，防止被非事务调用。

#### （6）NEVER

- **必须以非事务方式执行**
- 如果当前有事务，抛出异常

```
方法A（有事务）调用方法B → 抛出异常
方法A（无事务）调用方法B → B非事务执行
```

适用场景：不能在事务中执行的方法。

#### （7）NESTED（嵌套事务）

- 如果当前有事务，创建一个**嵌套事务**（保存点）
- 如果当前没有事务，和 REQUIRED 一样，创建新事务
- 嵌套事务是外层事务的一部分，外层提交它才提交
- 嵌套事务回滚不影响外层事务（只回滚到保存点）
- 外层事务回滚，嵌套事务也会回滚

```
方法A（有事务）调用方法B → B创建嵌套事务（保存点）
  B回滚 → 回滚到保存点，不影响A
  A回滚 → B也回滚
```

适用场景：需要部分回滚的场景。

注意：NESTED 需要底层数据库支持保存点（Savepoint），且事务管理器需要支持。

### 3. 对比总结

| 传播行为 | 有事务时 | 无事务时 | 常用程度 |
|---------|---------|---------|---------|
| REQUIRED | 加入当前事务 | 创建新事务 | 最常用（默认） |
| REQUIRES_NEW | 挂起当前，创建新事务 | 创建新事务 | 常用 |
| SUPPORTS | 加入当前事务 | 非事务执行 | 一般 |
| NOT_SUPPORTED | 挂起当前，非事务执行 | 非事务执行 | 少用 |
| MANDATORY | 加入当前事务 | 抛异常 | 少用 |
| NEVER | 抛异常 | 非事务执行 | 少用 |
| NESTED | 嵌套事务 | 创建新事务 | 少用 |

### 4. 重点理解：REQUIRED vs REQUIRES_NEW vs NESTED

- **REQUIRED**：加入外层事务，一起提交一起回滚
- **REQUIRES_NEW**：独立事务，互不影响
- **NESTED**：嵌套事务，外层回滚内层也回滚，内层回滚不影响外层

**答案解析**:

Spring 事务的传播行为是面试高频考点，必须掌握。

7 种传播行为，最常用的是前两种：REQUIRED（默认）和 REQUIRES_NEW。

REQUIRED 是默认的，有事务就加入，没有就创建。大部分场景用这个。

REQUIRES_NEW 总是创建新事务，和外层事务独立。适合日志、消息发送等需要独立提交的场景。

其他几种了解含义即可。

NESTED（嵌套事务）是个难点，它用保存点实现。内层回滚只回滚到保存点，不影响外层。但外层回滚会带着内层一起回滚。

注意：Spring 的事务传播行为只有在不同类之间调用才生效，同类调用不生效（因为代理的问题）。

**扩展问题**:
- 事务传播行为有哪些？
- REQUIRED 和 REQUIRES_NEW 的区别？
- NESTED 和 REQUIRES_NEW 的区别？
- 默认的传播行为是什么？
- 同类调用事务传播行为生效吗？为什么？

---

## Q6: Spring事务的隔离级别

**考察点**: 4种隔离级别、脏读不可重复读幻读、和数据库隔离级别的关系

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是事务隔离级别

事务隔离级别定义了多个并发事务之间数据的可见性。

隔离级别越高，数据一致性越好，但并发性能越差。

### 2. 事务的四个特性（ACID）

回顾一下事务的 ACID 特性：
- **原子性（Atomicity）**：事务是最小单位，要么都成功，要么都失败
- **一致性（Consistency）**：事务执行前后数据保持一致
- **隔离性（Isolation）**：并发事务之间互不干扰
- **持久性（Durability）**：事务提交后，数据永久保存

### 3. 并发事务的三个问题

#### （1）脏读（Dirty Read）

一个事务读取了另一个事务**未提交**的数据。

```
事务A：修改数据 → 还没提交
事务B：读取了A修改的数据
事务A：回滚了
结果：B读到了脏数据
```

#### （2）不可重复读（Non-Repeatable Read）

一个事务内，两次读取同一行数据，结果不一样（因为另一个事务修改并提交了）。

```
事务A：第一次读取 id=1 的数据
事务B：修改 id=1 的数据并提交
事务A：第二次读取 id=1 的数据，值变了
```

重点是**修改**（Update）。

#### （3）幻读（Phantom Read）

一个事务内，两次查询同一范围的数据，行数不一样（因为另一个事务插入或删除了数据）。

```
事务A：查询 age > 20 的用户，有5条
事务B：插入一条 age=25 的用户并提交
事务A：再次查询 age > 20 的用户，有6条
```

重点是**插入/删除**（Insert/Delete），行数变化。

### 4. Spring 的 5 种隔离级别

Spring 定义了 5 种隔离级别（Isolation 枚举）：

| 隔离级别 | 含义 | 脏读 | 不可重复读 | 幻读 |
|---------|------|------|-----------|------|
| DEFAULT | 使用数据库默认的隔离级别 | - | - | - |
| READ_UNCOMMITTED | 读未提交 | 可能 | 可能 | 可能 |
| READ_COMMITTED | 读已提交 | 不可能 | 可能 | 可能 |
| REPEATABLE_READ | 可重复读 | 不可能 | 不可能 | 可能（MySQL InnoDB 解决了） |
| SERIALIZABLE | 串行化 | 不可能 | 不可能 | 不可能 |

**DEFAULT**：使用数据库默认的隔离级别。
- MySQL InnoDB 默认：REPEATABLE_READ
- Oracle 默认：READ_COMMITTED

### 5. 隔离级别和性能的关系

隔离级别从低到高：
READ_UNCOMMITTED < READ_COMMITTED < REPEATABLE_READ < SERIALIZABLE

- 隔离级别越低：并发性能越好，数据一致性越差
- 隔离级别越高：数据一致性越好，并发性能越差

**实际开发中最常用的是 READ_COMMITTED**，大多数数据库默认也是这个（除了 MySQL）。

MySQL InnoDB 的默认隔离级别是 REPEATABLE_READ，而且通过 MVCC + Next-Key Lock 解决了幻读问题。

### 6. Spring 中设置隔离级别

```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void method() {
    // ...
}
```

### 7. 注意事项

Spring 的事务隔离级别是通过设置数据库连接的隔离级别来实现的。
如果数据库不支持某个隔离级别，Spring 也无能为力。

**答案解析**:

事务隔离级别是面试必考题，和数据库的隔离级别是一样的。

三个并发问题：脏读、不可重复读、幻读。
- 脏读：读到未提交的数据
- 不可重复读：同一行数据两次读不一样（修改）
- 幻读：同一范围查询行数不一样（增删）

四个隔离级别：
- 读未提交：最低，什么问题都有
- 读已提交：解决脏读
- 可重复读：解决脏读和不可重复读
- 串行化：解决所有问题，但性能最差

MySQL InnoDB 的默认隔离级别是可重复读，并且通过 MVCC 和 Next-Key Lock 解决了幻读问题。

Spring 的默认隔离级别是 DEFAULT，即使用数据库默认的。

**扩展问题**:
- 事务隔离级别有哪些？
- 脏读、不可重复读、幻读的区别？
- MySQL 默认的隔离级别是什么？
- MySQL 是如何解决幻读的？
- 隔离级别越高越好吗？

---

## Q7: Spring事务失效的场景

**考察点**: 事务不生效的常见原因、原理分析

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

Spring 事务是通过 AOP 代理实现的，只有通过代理对象调用事务方法，事务才会生效。

以下是常见的事务失效场景：

### 1. 方法不是 public 的

@Transactional 只能用在 public 方法上，非 public 方法事务不生效。

原因：Spring 的事务拦截器在拦截时，会检查方法是否是 public 的，非 public 不拦截。

```java
@Service
public class UserService {
    // 非public，事务不生效
    @Transactional
    private void addUser() {
        // ...
    }
}
```

### 2. 同类中方法调用（this 调用）

一个类中，方法 A 调用方法 B，B 上有 @Transactional，事务不生效。

```java
@Service
public class UserService {
    
    public void methodA() {
        this.methodB(); // this调用，走的是原对象，不是代理对象
    }
    
    @Transactional
    public void methodB() {
        // 事务不生效
    }
}
```

原因：Spring 事务是基于代理的，只有通过代理对象调用才会走事务拦截。this 调用走的是原对象，绕过了代理。

**解决方法**：
1. 把方法 B 放到另一个类中
2. 注入自己（@Autowired 自己，用注入的对象调用）
3. 用 AopContext.currentProxy() 获取代理对象（需要开启 exposeProxy）
4. 用编程式事务

### 3. 异常类型不对

默认情况下，Spring 事务只在遇到**RuntimeException** 和 **Error** 时回滚。

如果抛出的是受检异常（Exception），事务不会回滚。

```java
@Transactional
public void method() throws Exception {
    // 抛出受检异常，事务不回滚
    throw new Exception("出错了");
}
```

**解决方法**：
- 在 @Transactional 中指定 rollbackFor
```java
@Transactional(rollbackFor = Exception.class)
```

### 4. 异常被捕获了

方法中 try-catch 捕获了异常，没有抛出，事务感知不到异常，不会回滚。

```java
@Transactional
public void method() {
    try {
        // 数据库操作
        int i = 1 / 0;
    } catch (Exception e) {
        // 捕获了异常，没抛出
        e.printStackTrace();
    }
}
```

原因：事务只有在方法抛出未捕获的异常时才会回滚。

**解决方法**：
- 捕获后重新抛出
- 手动回滚：TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()

### 5. 数据库引擎不支持事务

如果使用的数据库引擎不支持事务（如 MySQL 的 MyISAM 引擎），事务不会生效。

现在 MySQL 默认用 InnoDB，支持事务。

### 6. 没有被 Spring 管理

类上没有加 @Service、@Component 等注解，没有被 Spring 管理，自然不会有事务代理。

```java
// 没有@Service，没有被Spring管理
public class UserService {
    @Transactional
    public void method() {
        // 事务不生效
    }
}
```

### 7. 多线程调用

在新线程中调用事务方法，事务不生效。

```java
@Transactional
public void method() {
    new Thread(() -> {
        // 新线程中的操作不在事务中
        userDao.insert();
    }).start();
}
```

原因：事务是和线程绑定的（ThreadLocal），新线程没有事务上下文。

### 8. 传播行为设置不正确

比如设置了 NOT_SUPPORTED 或 NEVER，事务会被挂起或抛异常。

### 9. 事务方法是 final 或 static 的

final 方法不能被重写，无法生成代理（CGLIB 基于继承）。
static 方法属于类，不属于对象，也无法代理。

### 总结

| 失效场景 | 原因 |
|---------|------|
| 方法非public | 事务拦截器只拦截public方法 |
| 同类调用 | this调用绕过了代理 |
| 异常类型不对 | 默认只回滚RuntimeException和Error |
| 异常被捕获 | 事务感知不到异常 |
| 数据库引擎不支持 | MyISAM不支持事务 |
| 没被Spring管理 | 没有生成代理对象 |
| 多线程调用 | 新线程没有事务上下文 |
| final/static方法 | 无法被代理 |

**答案解析**:

Spring 事务失效是面试高频考点，也是实际开发中经常遇到的问题。

根本原因：Spring 事务是基于 AOP 代理的，只有通过代理对象调用事务方法，事务才会生效。

最常见的失效场景：
1. 同类调用（this 调用）：最常考
2. 异常被捕获：catch 了没抛出
3. 异常类型不对：受检异常默认不回滚
4. 方法非 public

同类调用的问题可以用注入自己、AopContext、拆分到其他类等方式解决。

异常的问题可以用 rollbackFor 指定回滚的异常类型。

**扩展问题**:
- 事务失效的场景有哪些？
- 同类调用事务为什么失效？如何解决？
- 默认什么异常事务会回滚？
- 捕获了异常事务还会回滚吗？
- 如何手动回滚事务？

---

## Q8: Spring Boot的自动装配原理

**考察点**: 自动装配的原理、@EnableAutoConfiguration、SPI机制

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是自动装配

Spring Boot 的自动装配是指：**Spring Boot 会根据类路径下的依赖，自动配置 Bean，放到 Spring 容器中**。

比如引入了 spring-boot-starter-web 依赖，Spring Boot 就会自动配置 Spring MVC、Tomcat 等。

开发者只需要引入 starter，不需要做繁琐的配置。

### 2. 核心注解：@SpringBootApplication

Spring Boot 的启动类上有一个 @SpringBootApplication 注解，它是一个组合注解，包含三个核心注解：

1. **@SpringBootConfiguration**：标识这是一个配置类（底层就是 @Configuration）
2. **@EnableAutoConfiguration**：开启自动配置，核心中的核心
3. **@ComponentScan**：扫描启动类所在包及其子包下的组件

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

等价于：
```java
@Configuration
@EnableAutoConfiguration
@ComponentScan
public class Application {
    // ...
}
```

### 3. @EnableAutoConfiguration 原理

@EnableAutoConfiguration 是自动装配的核心。

它导入了 **AutoConfigurationImportSelector** 这个选择器。

```java
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {
}
```

**AutoConfigurationImportSelector 的作用**：
- 读取 `META-INF/spring.factories` 文件
- 获取所有自动配置类的全限定名
- 过滤、筛选后，返回需要加载的自动配置类

### 4. spring.factories 文件

Spring Boot 的自动配置类定义在各个 starter 的 `META-INF/spring.factories` 文件中。

这个文件是 Key-Value 格式：
```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration,\
org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,\
org.springframework.boot.autoconfigure.data.redis.RedisAutoConfiguration,\
...
```

Key 是 EnableAutoConfiguration 的全限定名，Value 是自动配置类的列表。

Spring Boot 启动时会：
1. 扫描所有 jar 包中的 `META-INF/spring.factories` 文件
2. 读取 EnableAutoConfiguration 对应的自动配置类
3. 将这些自动配置类加载到容器中

### 5. 自动配置类的条件注解

不是所有自动配置类都会生效，它们都有条件注解，满足条件才会生效。

常见的条件注解：

| 注解 | 作用 |
|------|------|
| @ConditionalOnClass | 类路径下有指定类才生效 |
| @ConditionalOnMissingBean | 容器中没有指定 Bean 才生效 |
| @ConditionalOnProperty | 配置文件中有指定属性才生效 |
| @ConditionalOnWebApplication | Web 应用才生效 |
| @ConditionalOnBean | 容器中有指定 Bean 才生效 |

以 DataSourceAutoConfiguration 为例：
```java
@Configuration
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
@ConditionalOnMissingBean(type = "io.r2dbc.spi.ConnectionFactory")
@EnableConfigurationProperties(DataSourceProperties.class)
@Import({ DataSourcePoolMetadataProvidersConfiguration.class, ... })
public class DataSourceAutoConfiguration {
    // ...
}
```

只有类路径下有 DataSource 类，且容器中没有指定类型的 Bean，这个自动配置类才会生效。

### 6. 自动装配的完整流程

1. Spring Boot 启动，运行 main 方法
2. 加载 @SpringBootApplication 注解
3. @EnableAutoConfiguration 导入 AutoConfigurationImportSelector
4. AutoConfigurationImportSelector 读取 spring.factories 文件
5. 获取所有自动配置类
6. 根据条件注解（@ConditionalOnXxx）筛选出需要加载的配置类
7. 将符合条件的配置类注册到容器中
8. 配置类中的 @Bean 方法创建 Bean，放入容器

### 7. 自定义 starter

理解了自动装配原理，就可以自定义 starter：

1. 创建一个自动配置类，加 @Configuration
2. 在 META-INF/spring.factories 中指定自动配置类
3. 用条件注解控制生效条件
4. 打成 jar 包供其他项目引用

**答案解析**:

Spring Boot 自动装配原理是面试最高频的考点之一。

核心流程：
1. @SpringBootApplication 是组合注解
2. @EnableAutoConfiguration 是核心
3. 通过 AutoConfigurationImportSelector 读取 spring.factories
4. 加载所有自动配置类
5. 通过条件注解筛选生效的配置

spring.factories 是关键文件，定义了所有自动配置类。Spring Boot 启动时会扫描所有 jar 包下的这个文件。

条件注解也很重要，它让自动配置类只在满足条件时才生效，实现了"按需装配"。

理解了自动装配原理，也就理解了 Spring Boot 的核心思想：约定大于配置，自动配置。

**扩展问题**:
- Spring Boot 自动装配的原理？
- @SpringBootApplication 包含哪些注解？
- spring.factories 文件有什么用？
- 条件注解有哪些？
- 如何自定义一个 starter？

---

## Q9: @SpringBootApplication注解包含哪些

**考察点**: @SpringBootApplication的组成、各注解的作用

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. @SpringBootApplication 是组合注解

@SpringBootApplication 是一个组合注解，它包含了三个核心注解：

1. **@SpringBootConfiguration**
2. **@EnableAutoConfiguration**
3. **@ComponentScan**

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = { 
    @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
    @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class) 
})
public @interface SpringBootApplication {
    // ...
}
```

### 2. @SpringBootConfiguration

- 标识这是一个 Spring Boot 的配置类
- 底层就是 @Configuration
- 表示这个类可以提供 Bean 定义

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Configuration
public @interface SpringBootConfiguration {
    // ...
}
```

本质上就是 @Configuration，只是名字换了一下，标识是 Spring Boot 的配置类。

### 3. @EnableAutoConfiguration

- **开启自动配置**，是 Spring Boot 自动装配的核心
- 导入了 AutoConfigurationImportSelector
- 读取 spring.factories 文件，加载所有自动配置类

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@AutoConfigurationPackage
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {
    // ...
}
```

这是三个注解中最核心的，没有它就没有自动装配。

### 4. @ComponentScan

- 组件扫描
- 默认扫描启动类所在包及其子包
- 把标注了 @Component、@Service、@Controller、@Repository 等注解的类注册到容器中

@SpringBootApplication 中的 @ComponentScan 还排除了一些过滤器，主要是排除自动配置类（因为自动配置类由 @EnableAutoConfiguration 处理）。

### 5. 其他属性

@SpringBootApplication 还提供了一些常用属性：

- **exclude**：排除指定的自动配置类
- **excludeName**：按类名排除自动配置类
- **scanBasePackages**：指定扫描的基础包
- **scanBasePackageClasses**：指定扫描的类（以类所在包为基础包）

```java
@SpringBootApplication(
    exclude = DataSourceAutoConfiguration.class,
    scanBasePackages = "com.example"
)
```

### 6. 为什么要组合成一个注解

- 简化配置：不需要写三个注解
- 约定大于配置：默认配置就能满足大部分场景
- 启动类更简洁

**答案解析**:

@SpringBootApplication 是 Spring Boot 最基础的知识点，面试必问。

它是一个组合注解，包含三个核心注解：
1. @SpringBootConfiguration：配置类
2. @EnableAutoConfiguration：自动配置（核心）
3. @ComponentScan：组件扫描

其中 @EnableAutoConfiguration 是最核心的，它实现了自动装配。

这个注解体现了 Spring Boot 的设计思想：约定大于配置。一个注解就能搞定启动配置。

**扩展问题**:
- @SpringBootApplication 包含哪些注解？
- @EnableAutoConfiguration 的作用？
- @SpringBootConfiguration 和 @Configuration 的区别？
- @ComponentScan 默认扫描哪些包？
- 如何排除某个自动配置类？

---

## Q10: Spring Boot Starter的原理

**考察点**: Starter的原理、结构、如何自定义

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 Starter

Starter 是 Spring Boot 的一种约定，它把某个功能所需的所有依赖打包在一起，开发者只需要引入一个 starter 依赖，就能使用该功能。

比如要用 Spring MVC，只需要引入 `spring-boot-starter-web`，不需要自己找一堆依赖。

**Starter 的理念**：约定大于配置，开箱即用。

### 2. Starter 的命名规范

**官方 Starter**：
- 命名格式：`spring-boot-starter-xxx`
- 如：spring-boot-starter-web、spring-boot-starter-data-redis

**第三方 Starter**：
- 命名格式：`xxx-spring-boot-starter`
- 如：mybatis-spring-boot-starter、druid-spring-boot-starter

### 3. Starter 的组成

一个 Starter 通常包含两部分：

**（1）starter 模块**
- 只有一个 pom.xml，用来引入依赖
- 没有代码
- 相当于一个"依赖集合包"

**（2）autoconfigure 模块**
- 自动配置代码
- 包含自动配置类、属性类等
- 包含 META-INF/spring.factories 文件

实际开发中，也可以把两部分合并成一个模块。

### 4. Starter 的工作原理

Starter 的核心还是自动装配：

1. 引入 starter 依赖
2. starter 传递依赖引入 autoconfigure 模块
3. autoconfigure 模块中的 META-INF/spring.factories 定义了自动配置类
4. Spring Boot 启动时扫描 spring.factories
5. 加载自动配置类
6. 自动配置类通过条件注解判断是否生效
7. 生效的自动配置类创建 Bean，放入容器

### 5. 自定义 Starter 的步骤

**第一步：创建 Maven 项目**

项目结构：
```
xxx-spring-boot-starter
├── pom.xml
└── src
    └── main
        ├── java
        │   └── com.example
        │       ├── XxxAutoConfiguration.java    // 自动配置类
        │       └── XxxProperties.java          // 属性配置类
        └── resources
            └── META-INF
                └── spring.factories             // 注册自动配置类
```

**第二步：编写属性配置类**

```java
@ConfigurationProperties(prefix = "xxx")
public class XxxProperties {
    private String name;
    private int timeout = 1000;
    // getter/setter
}
```

**第三步：编写自动配置类**

```java
@Configuration
@EnableConfigurationProperties(XxxProperties.class)
@ConditionalOnClass(XxxService.class)
@ConditionalOnProperty(prefix = "xxx", name = "enabled", havingValue = "true", matchIfMissing = true)
public class XxxAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public XxxService xxxService(XxxProperties properties) {
        return new XxxService(properties);
    }
}
```

**第四步：编写 spring.factories**

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
com.example.XxxAutoConfiguration
```

**第五步：使用自定义 Starter**

其他项目引入依赖：
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>xxx-spring-boot-starter</artifactId>
    <version>1.0.0</version>
</dependency>
```

配置文件中配置：
```yaml
xxx:
  name: test
  timeout: 2000
```

然后就可以直接注入使用：
```java
@Autowired
private XxxService xxxService;
```

### 6. Starter 的好处

1. **简化依赖管理**：不用找一堆依赖，一个 starter 搞定
2. **降低使用门槛**：不需要复杂配置，开箱即用
3. **减少版本冲突**：starter 管理好了依赖版本
4. **约定大于配置**：默认配置就能用，需要时再修改

**答案解析**:

Spring Boot Starter 是 Spring Boot 的重要特性，也是面试常考题。

Starter 的本质就是自动装配的延伸。它把自动配置类和相关依赖打包在一起，让用户只需要引入一个依赖就能使用某个功能。

Starter 本身没有代码（只有 pom.xml），真正的代码在 autoconfigure 模块里。但实际开发中经常把两者合并。

自定义 Starter 的步骤：
1. 写属性类（@ConfigurationProperties）
2. 写自动配置类（@Configuration + 条件注解）
3. 写 spring.factories 注册自动配置类
4. 打成 jar 包

理解了 Starter 的原理，也就理解了 Spring Boot 的"约定大于配置"。

**扩展问题**:
- Starter 的原理是什么？
- 如何自定义一个 Starter？
- Starter 和自动装配的关系？
- 官方 Starter 和第三方 Starter 的命名区别？
- Starter 有什么好处？

---

## Q11: Spring循环依赖及解决方案

**考察点**: 什么是循环依赖、Spring如何解决、三级缓存

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是循环依赖

循环依赖是指两个或多个 Bean 之间相互引用，形成一个环。

```java
@Service
public class A {
    @Autowired
    private B b; // A依赖B
}

@Service
public class B {
    @Autowired
    private A a; // B依赖A
}
```

A 依赖 B，B 依赖 A，这就是循环依赖。

### 2. 循环依赖的类型

**（1）构造器循环依赖**

通过构造方法注入产生的循环依赖：
```java
@Service
public class A {
    public A(B b) { ... }
}

@Service
public class B {
    public B(A a) { ... }
}
```

**Spring 无法解决构造器循环依赖**，会抛出 BeanCurrentlyInCreationException。

**（2）setter 循环依赖（字段注入）**

通过 setter 方法或字段注入产生的循环依赖：
```java
@Service
public class A {
    @Autowired
    private B b;
}

@Service
public class B {
    @Autowired
    private A a;
}
```

**Spring 可以解决单例模式下的 setter 循环依赖**。

**（3）prototype 循环依赖**

prototype 作用域的循环依赖，Spring 无法解决，会抛异常。

### 3. Spring 如何解决循环依赖：三级缓存

Spring 通过**三级缓存**来解决单例 Bean 的 setter 循环依赖。

**三级缓存**：

| 缓存 | 名称 | 存放内容 |
|------|------|---------|
| 一级缓存 | singletonObjects | 完全初始化好的 Bean（成品） |
| 二级缓存 | earlySingletonObjects | 早期 Bean（实例化了但还没初始化） |
| 三级缓存 | singletonFactories | Bean 的工厂（ObjectFactory） |

```java
// 一级缓存：单例对象缓存
private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);

// 二级缓存：早期单例对象缓存
private final Map<String, Object> earlySingletonObjects = new HashMap<>(16);

// 三级缓存：单例工厂缓存
private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);
```

### 4. 解决循环依赖的过程

以 A 和 B 互相依赖为例：

**步骤1：创建 A**
- A 实例化（调用构造方法）
- 将 A 的工厂放入三级缓存（singletonFactories）
- 开始给 A 填充属性，发现需要 B

**步骤2：创建 B**
- B 实例化（调用构造方法）
- 将 B 的工厂放入三级缓存
- 开始给 B 填充属性，发现需要 A

**步骤3：B 获取 A**
- B 要注入 A，去缓存中找 A
- 一级缓存没有，二级缓存没有，三级缓存有 A 的工厂
- 从三级缓存获取 A 的早期引用（提前暴露的对象）
- 把 A 从三级缓存移到二级缓存
- B 拿到了 A（虽然 A 还没初始化完成）
- B 初始化完成
- B 放入一级缓存

**步骤4：A 完成初始化**
- A 拿到 B（B 已经初始化好了）
- A 初始化完成
- A 放入一级缓存

最终，A 和 B 都创建完成，循环依赖解决。

### 5. 为什么需要三级缓存

**一级缓存**：存完整的 Bean，大家都用。

**为什么需要二级和三级缓存？**

- 如果只有一级缓存：Bean 还没初始化完就放进去，其他线程拿到的是不完整的 Bean，有问题。
- 二级缓存：存早期 Bean（实例化了但没初始化），解决循环依赖。
- 三级缓存：存 BeanFactory，用于创建早期 Bean。如果有 AOP 代理，三级缓存返回的是代理对象，不是原始对象。

**为什么需要三级缓存，而不是只有二级缓存？**

因为如果 Bean 有 AOP 代理，需要在三级缓存的工厂中生成代理对象。如果只有二级缓存，就需要所有 Bean 都提前生成代理对象，不管有没有循环依赖，这样效率低。

三级缓存的作用是：**只有在发生循环依赖时，才提前生成代理对象**。没有循环依赖的话，Bean 初始化完成后才生成代理。

### 6. 不能解决的循环依赖

1. **构造器循环依赖**：实例化阶段就需要依赖，还没放入缓存，解决不了
2. **prototype 循环依赖**：prototype Bean 不缓存，解决不了
3. **多例循环依赖**：每次创建新的，解决不了

**答案解析**:

Spring 循环依赖是面试高频考点，也是难点。

核心是三级缓存：
- 一级缓存（singletonObjects）：完整 Bean
- 二级缓存（earlySingletonObjects）：早期 Bean
- 三级缓存（singletonFactories）：Bean 工厂

解决循环依赖的前提：
1. 单例 Bean（只有单例才缓存）
2. setter 注入/字段注入（构造器注入解决不了）

为什么构造器注入解决不了？因为构造器注入是在实例化阶段，还没实例化完成，还没放入缓存，就需要依赖了。

三级缓存的意义：如果 Bean 需要 AOP 代理，三级缓存会返回代理对象，而不是原始对象。如果只有二级缓存，所有 Bean 都要提前生成代理，性能差。

**扩展问题**:
- 什么是循环依赖？
- Spring 如何解决循环依赖？
- 三级缓存分别是什么？
- 为什么需要三级缓存？二级不行吗？
- 构造器注入的循环依赖能解决吗？

---

## Q12: Spring中的BeanFactory和ApplicationContext的区别

**考察点**: 两种IOC容器的区别、功能差异

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 基本概念

**BeanFactory**：
- Spring 最基础的 IOC 容器
- 提供了最基本的 Bean 管理功能
- 是 Spring 的底层接口
- 懒加载：第一次获取 Bean 时才初始化

**ApplicationContext**：
- BeanFactory 的子接口
- 更高级的 IOC 容器
- 在 BeanFactory 的基础上增加了很多功能
- 预加载：容器启动时就初始化所有单例 Bean
- 开发中一般用 ApplicationContext

### 2. 功能对比

| 功能 | BeanFactory | ApplicationContext |
|------|-------------|-------------------|
| Bean 管理 | 是（基础） | 是（完整） |
| 国际化 | 否 | 是（MessageSource） |
| 事件发布 | 否 | 是（ApplicationEventPublisher） |
| 资源加载 | 否 | 是（ResourceLoader） |
| AOP 集成 | 否 | 是 |
| Web 支持 | 否 | 是（WebApplicationContext） |
| 加载方式 | 懒加载 | 预加载（单例） |
| 适用场景 | 资源受限 | 普通应用 |

### 3. 详细说明

#### （1）BeanFactory

- 最底层的接口，定义了最基本的 IOC 功能
- 主要方法：getBean、containsBean、isSingleton 等
- 默认实现：DefaultListableBeanFactory
- 特点：懒加载，启动快，占用资源少

```java
BeanFactory factory = new XmlBeanFactory(new ClassPathResource("beans.xml"));
UserService userService = (UserService) factory.getBean("userService");
```

现在基本不用 BeanFactory 了，功能太少。

#### （2）ApplicationContext

ApplicationContext 继承了 BeanFactory，还继承了其他接口：

- **MessageSource**：国际化支持
- **ApplicationEventPublisher**：事件发布/订阅
- **ResourceLoader**：资源加载
- **EnvironmentCapable**：环境配置

**常见实现类**：
- **ClassPathXmlApplicationContext**：从 classpath 加载 XML 配置
- **FileSystemXmlApplicationContext**：从文件系统加载 XML 配置
- **AnnotationConfigApplicationContext**：基于注解配置
- **Spring Boot 中的 AnnotationConfigServletWebServerApplicationContext**：Web 环境

### 4. 加载方式不同

**BeanFactory**：
- 懒加载（Lazy Loading）
- 启动时不创建 Bean，第一次 getBean 时才创建
- 启动快，内存占用少

**ApplicationContext**：
- 预加载（Eager Loading）
- 容器启动时就创建所有单例 Bean
- 启动慢一点，但运行时快
- 可以提前发现配置错误

### 5. 为什么开发中用 ApplicationContext

1. **功能更丰富**：国际化、事件、资源加载等
2. **预加载**：启动时就初始化，提前发现问题
3. **AOP 支持**：更好地集成 AOP
4. **Web 支持**：Web 应用必备
5. **自动装配**：Spring Boot 用的就是 ApplicationContext

### 6. 注意点

虽然 ApplicationContext 功能更丰富，但 BeanFactory 是基础，很多底层实现都是基于 BeanFactory 的。

ApplicationContext 内部也是持有一个 BeanFactory 实例（组合模式），在它的基础上增加功能。

**答案解析**:

BeanFactory 和 ApplicationContext 是 Spring 的两个核心容器接口。

BeanFactory 是最基础的，功能少，懒加载。
ApplicationContext 是更高级的，功能丰富，预加载。

开发中一般都用 ApplicationContext，BeanFactory 主要是底层使用。

两者最核心的区别：
1. 功能多少：ApplicationContext 功能多很多
2. 加载方式：BeanFactory 懒加载，ApplicationContext 预加载

Spring Boot 中用的就是 ApplicationContext 的实现类。

**扩展问题**:
- BeanFactory 和 ApplicationContext 的区别？
- ApplicationContext 继承了哪些接口？
- 懒加载和预加载的区别？
- 为什么 ApplicationContext 比 BeanFactory 高级？
- Spring Boot 中用的是哪个？

---

## Q13: @Autowired和@Resource的区别

**考察点**: 两个注入注解的区别、注入方式、来源

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 基本区别

| 特性 | @Autowired | @Resource |
|------|-----------|-----------|
| 来源 | Spring 提供 | JSR-250 规范（Java 自带） |
| 注入方式 | 默认按类型（byType） | 默认按名称（byName） |
| 支持的注入点 | 构造器、字段、setter、参数 | 字段、setter |
| 必须性 | 默认必须（required=true） | 默认必须 |
| 名称指定 | @Qualifier | name 属性 |

### 2. 注入方式不同

这是最核心的区别。

#### @Autowired

- **默认按类型（byType）注入**
- 如果找到多个同类型的 Bean，会报错
- 可以配合 @Qualifier 按名称注入

```java
// 按类型注入
@Autowired
private UserDao userDao;

// 按名称注入（配合@Qualifier）
@Autowired
@Qualifier("userDaoImpl")
private UserDao userDao;
```

#### @Resource

- **默认按名称（byName）注入**
- 如果找不到名称匹配的，再按类型找
- 可以通过 name 属性指定名称，通过 type 属性指定类型

```java
// 默认按名称注入（属性名就是bean名称）
@Resource
private UserDao userDao; // 找名为userDao的bean

// 指定名称
@Resource(name = "userDaoImpl")
private UserDao userDao;

// 指定类型
@Resource(type = UserDaoImpl.class)
private UserDao userDao;
```

### 3. 来源不同

- **@Autowired**：Spring 框架自己的注解（org.springframework.beans.factory.annotation.Autowired）
- **@Resource**：JSR-250 规范的注解（javax.annotation.Resource），Java 自带的

@Resource 是 Java 标准，@Autowired 是 Spring 特有的。

### 4. 支持的注入点不同

- **@Autowired**：可以用在构造器、字段、setter 方法、方法参数上
- **@Resource**：可以用在字段、setter 方法上

@Autowired 支持构造器注入，@Resource 不支持。

### 5. 必须性不同

两者都可以设置是否必须。

**@Autowired**：
```java
@Autowired(required = false) // 不是必须的，找不到就不注入
private UserDao userDao;
```

**@Resource**：
```java
// 没有required属性，找不到就抛异常
```

### 6. 多个同类型 Bean 的处理

**@Autowired**：
- 默认按类型，找到多个同类型 Bean 会抛 NoUniqueBeanDefinitionException
- 解决方案：
  1. @Primary：指定一个首选的 Bean
  2. @Qualifier：按名称指定
  3. 变量名和 Bean 名一致（会按名称匹配）

**@Resource**：
- 默认按名称，名称唯一就不会有问题
- 如果名称找不到，再按类型找，类型多个还是会报错

### 7. 推荐使用

- **Spring 推荐**：构造器注入，用 @Autowired（或省略）
- **通用性**：@Resource 是标准，换框架也能用
- **实际开发**：都可以，看习惯

Spring 4.3 之后，如果类只有一个构造方法，@Autowired 可以省略。

**答案解析**:

@Autowired 和 @Resource 是最常用的两个依赖注入注解，也是面试必考题。

核心区别：
1. @Autowired 默认按类型，@Resource 默认按名称
2. @Autowired 是 Spring 的，@Resource 是 JSR-250 标准的
3. @Autowired 支持构造器注入，@Resource 不支持

@Autowired 配合 @Qualifier 也能按名称注入。
@Resource 也支持按类型注入。

实际开发中两个都常用，@Autowired 更 Spring 风格，@Resource 更通用。

**扩展问题**:
- @Autowired 和 @Resource 的区别？
- 默认按类型还是按名称？
- @Qualifier 注解有什么用？
- 有多个同类型 Bean 怎么办？
- 哪个是 Java 标准的？

---

## Q14: @Component和@Bean的区别

**考察点**: 两种注册Bean的方式的区别、适用场景

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 基本区别

| 特性 | @Component | @Bean |
|------|-----------|-------|
| 作用对象 | 类 | 方法 |
| 使用方式 | 加在类上 | 加在配置类的方法上 |
| 注册方式 | 自动扫描 | 手动注册 |
| 控制程度 | 低（注解就行） | 高（完全控制Bean的创建） |
| 适用范围 | 自己写的类 | 第三方库的类 |
| Bean名称 | 默认类名首字母小写 | 默认方法名 |

### 2. @Component

**用法**：加在类上，配合 @ComponentScan 使用。

```java
@Component
public class UserService {
    // ...
}
```

Spring 扫描到这个注解，就自动把这个类注册为 Bean。

**衍生注解**：
- @Service：业务层
- @Controller：控制层
- @Repository：持久层
- @Configuration：配置类

这些本质上都是 @Component，只是语义不同。

### 3. @Bean

**用法**：加在配置类的方法上，方法返回值就是 Bean。

```java
@Configuration
public class AppConfig {
    
    @Bean
    public UserService userService() {
        return new UserService();
    }
}
```

方法名默认就是 Bean 的名称，也可以通过 name 属性指定。

### 4. 核心区别

#### （1）作用对象不同

- **@Component**：作用在类上
- **@Bean**：作用在方法上

#### （2）控制权不同

- **@Component**：Spring 自动创建 Bean，控制权在 Spring
- **@Bean**：我们自己创建 Bean，控制权在我们手里

@Bean 可以完全控制 Bean 的创建过程：
```java
@Bean
public DataSource dataSource() {
    HikariDataSource ds = new HikariDataSource();
    ds.setJdbcUrl("jdbc:mysql://localhost:3306/test");
    ds.setUsername("root");
    ds.setPassword("123456");
    // 可以做各种配置
    return ds;
}
```

#### （3）适用场景不同

- **@Component**：自己写的类，直接加注解就行
- **@Bean**：第三方库的类，不能修改源码，只能用 @Bean 注册

比如你想用 DruidDataSource，但 DruidDataSource 是第三方的，你不能给它加 @Component，就用 @Bean。

#### （4）Bean 名称

- **@Component**：默认是类名首字母小写，如 UserService → userService
- **@Bean**：默认是方法名，也可以指定 name

### 5. 其他区别

| 特性 | @Component | @Bean |
|------|-----------|-------|
| 作用域 | @Scope | @Scope |
| 懒加载 | @Lazy | @Lazy |
| 初始化方法 | @PostConstruct 或实现InitializingBean | initMethod 属性 |
| 销毁方法 | @PreDestroy 或实现DisposableBean | destroyMethod 属性 |

```java
@Bean(initMethod = "init", destroyMethod = "close")
public DataSource dataSource() {
    return new DruidDataSource();
}
```

### 6. 如何选择

- **自己写的类**：用 @Component（@Service、@Controller 等），简单方便
- **第三方类**：用 @Bean，可以灵活配置
- **需要复杂的创建逻辑**：用 @Bean，完全控制

**答案解析**:

@Component 和 @Bean 都是用来注册 Bean 的，但方式不同。

@Component 是加在类上的，Spring 自动扫描注册。适合自己写的类。
@Bean 是加在方法上的，手动注册。适合第三方类或需要复杂配置的情况。

@Component 是"自动"的，@Bean 是"手动"的。

实际开发中，自己的业务类用 @Component/@Service，第三方组件用 @Bean。

**扩展问题**:
- @Component 和 @Bean 的区别？
- 什么时候用 @Bean？
- @Bean 的 Bean 名称默认是什么？
- @Service、@Controller 和 @Component 的区别？
- @Bean 如何指定初始化方法和销毁方法？

---

## Q15: Spring MVC的工作流程

**考察点**: Spring MVC的请求处理流程、各组件的作用

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. Spring MVC 核心组件

Spring MVC 的核心组件：

1. **DispatcherServlet（前端控制器）**：所有请求的入口，统一调度
2. **HandlerMapping（处理器映射器）**：根据请求找到对应的 Handler（Controller方法）
3. **HandlerAdapter（处理器适配器）**：调用 Handler 执行方法
4. **Controller（处理器）**：处理业务逻辑
5. **ViewResolver（视图解析器）**：解析视图，找到对应的页面
6. **View（视图）**：渲染视图，返回给用户

### 2. 完整工作流程

Spring MVC 处理一个请求的完整流程：

**步骤1：用户发送请求**
- 用户在浏览器输入 URL，发送 HTTP 请求
- 请求到达前端控制器 DispatcherServlet

**步骤2：DispatcherServlet 接收请求**
- DispatcherServlet 是所有请求的统一入口
- 它不处理业务，只负责调度

**步骤3：DispatcherServlet 调用 HandlerMapping**
- DispatcherServlet 调用 HandlerMapping
- HandlerMapping 根据请求 URL 找到对应的 Handler（Controller 中的方法）
- 返回 HandlerExecutionChain（包含 Handler 和拦截器）

**步骤4：DispatcherServlet 调用 HandlerAdapter**
- DispatcherServlet 根据 Handler 选择对应的 HandlerAdapter
- HandlerAdapter 调用 Handler（Controller 方法）

**步骤5：Handler 执行业务逻辑**
- Controller 方法执行业务逻辑
- 返回 ModelAndView（包含数据和视图名）
  - 如果方法返回 String：就是视图名
  - 如果方法返回对象：通过消息转换器转成 JSON（@ResponseBody）

**步骤6：HandlerAdapter 返回 ModelAndView**
- HandlerAdapter 将 ModelAndView 返回给 DispatcherServlet

**步骤7：DispatcherServlet 调用 ViewResolver**
- DispatcherServlet 调用 ViewResolver 解析视图
- ViewResolver 根据视图名找到对应的 View（如 JSP、Thymeleaf）

**步骤8：View 渲染视图**
- View 将 Model 中的数据渲染到视图中
- 生成 HTML 页面

**步骤9：返回响应**
- DispatcherServlet 将渲染结果返回给用户
- 浏览器显示页面

### 3. 流程图

```
用户请求
   ↓
DispatcherServlet
   ↓
HandlerMapping → 找到Handler（Controller方法）
   ↓
DispatcherServlet
   ↓
HandlerAdapter → 调用Handler
   ↓
Controller（Handler） → 执行业务，返回ModelAndView
   ↓
HandlerAdapter
   ↓
DispatcherServlet
   ↓
ViewResolver → 解析视图名，找到View
   ↓
View → 渲染视图（数据+模板=HTML）
   ↓
DispatcherServlet
   ↓
返回响应给用户
```

### 4. @ResponseBody 的流程

如果 Controller 方法加了 @ResponseBody（或类上有 @RestController）：

- 返回值不经过 ViewResolver
- 直接通过 HttpMessageConverter 转换成 JSON/XML
- 写入响应体
- 前后端分离的项目都是这种方式

### 5. 各组件的作用总结

| 组件 | 作用 |
|------|------|
| DispatcherServlet | 前端控制器，统一入口，调度 |
| HandlerMapping | 根据请求找Handler |
| HandlerAdapter | 调用Handler执行 |
| Controller | 处理业务逻辑 |
| ViewResolver | 解析视图 |
| View | 渲染视图 |
| HandlerInterceptor | 拦截器，在Handler前后执行 |

### 6. 为什么叫 MVC

- **Model（模型）**：数据，如 ModelAndView 中的 Model
- **View（视图）**：页面展示，如 JSP、Thymeleaf
- **Controller（控制器）**：处理请求，如 Controller 类

Spring MVC 是 MVC 模式的实现，但和传统的 MVC 有些区别，因为多了 DispatcherServlet 这个前端控制器。

**答案解析**:

Spring MVC 的工作流程是面试高频考点。

核心是 DispatcherServlet，它是所有请求的入口，负责调度各个组件。

流程可以简单概括为：
1. 请求到 DispatcherServlet
2. HandlerMapping 找 Handler
3. HandlerAdapter 调用 Handler
4. Handler 处理业务，返回 ModelAndView
5. ViewResolver 解析视图
6. View 渲染
7. 返回响应

@ResponseBody 的情况也要了解：直接用消息转换器转 JSON，不走视图解析。

Spring Boot 中前后端分离的项目，大部分接口都是 @ResponseBody，返回 JSON。

**扩展问题**:
- Spring MVC 的工作流程？
- DispatcherServlet 的作用？
- HandlerMapping 和 HandlerAdapter 的区别？
- @ResponseBody 的工作原理？
- Spring MVC 有哪些组件？

---

## Q16: Spring Boot常用的starter有哪些

**考察点**: 常用Starter的名称和作用

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 官方 Starter

**Web 开发**：
- **spring-boot-starter-web**：Web 开发，包含 Spring MVC、Tomcat、Jackson
- **spring-boot-starter-webflux**：响应式 Web 开发，WebFlux + Netty
- **spring-boot-starter-websocket**：WebSocket 支持
- **spring-boot-starter-validation**：参数校验（Hibernate Validator）

**数据访问**：
- **spring-boot-starter-data-jpa**：JPA + Hibernate
- **spring-boot-starter-data-redis**：Redis + Lettuce
- **spring-boot-starter-data-mongodb**：MongoDB
- **spring-boot-starter-data-elasticsearch**：Elasticsearch
- **spring-boot-starter-jdbc**：JDBC + HikariCP 连接池
- **mybatis-spring-boot-starter**：MyBatis（第三方）

**安全**：
- **spring-boot-starter-security**：Spring Security 安全框架
- **spring-boot-starter-oauth2-client**：OAuth2 客户端
- **spring-boot-starter-oauth2-resource-server**：OAuth2 资源服务器

**模板引擎**：
- **spring-boot-starter-thymeleaf**：Thymeleaf 模板引擎
- **spring-boot-starter-freemarker**：FreeMarker 模板引擎

**消息队列**：
- **spring-boot-starter-activemq**：ActiveMQ
- **spring-boot-starter-amqp**：RabbitMQ
- **spring-boot-starter-data-redis**：也可以做消息队列

**测试**：
- **spring-boot-starter-test**：测试支持（JUnit、Mock、TestRestTemplate）

**其他**：
- **spring-boot-starter**：核心 starter，包含自动配置、日志、YAML 支持等
- **spring-boot-starter-aop**：AOP 支持（AspectJ）
- **spring-boot-starter-cache**：缓存支持
- **spring-boot-starter-actuator**：监控和管理端点
- **spring-boot-starter-mail**：邮件支持
- **spring-boot-starter-quartz**：定时任务 Quartz
- **spring-boot-starter-task**：定时任务（Spring Task）

### 2. 常用第三方 Starter

- **mybatis-spring-boot-starter**：MyBatis
- **druid-spring-boot-starter**：Druid 数据库连接池
- **pagehelper-spring-boot-starter**：PageHelper 分页插件
- **mapper-spring-boot-starter**：通用 Mapper
- **spring-boot-admin-starter-client**：Spring Boot Admin 监控客户端
- **dynamic-datasource-spring-boot-starter**：动态数据源
- **knife4j-spring-boot-starter**：Knife4j 接口文档
- **xxl-job-spring-boot-starter**：XXL-Job 分布式任务调度

### 3. Starter 的命名规范

- **官方**：`spring-boot-starter-xxx`
- **第三方**：`xxx-spring-boot-starter`

### 4. 选择 Starter 的建议

1. **Web 项目**：spring-boot-starter-web
2. **用 MyBatis**：mybatis-spring-boot-starter + mysql-connector-java
3. **用 Redis**：spring-boot-starter-data-redis
4. **用 RabbitMQ**：spring-boot-starter-amqp
5. **接口文档**：knife4j-spring-boot-starter 或 springdoc-openapi
6. **参数校验**：spring-boot-starter-validation
7. **监控**：spring-boot-starter-actuator + Spring Boot Admin
8. **安全**：spring-boot-starter-security 或 Sa-Token

### 5. 注意事项

- Starter 只是依赖集合，真正的自动配置在 autoconfigure 模块里
- 引入 Starter 不代表所有功能都开启，有些需要加注解（如 @EnableXXX）
- 不需要的 Starter 不要引入，避免不必要的依赖

**答案解析**:

Spring Boot Starter 是 Spring Boot 的重要特性，面试中经常问到。

常用的几个 Starter 必须记住：
- web：Web 开发
- data-redis：Redis
- data-jpa / mybatis：ORM
- validation：参数校验
- security：安全
- test：测试
- actuator：监控
- aop：AOP

第三方 Starter 也需要了解几个常用的：mybatis、druid、pagehelper、knife4j 等。

命名规范也要知道：官方是 spring-boot-starter-xxx，第三方是 xxx-spring-boot-starter。

**扩展问题**:
- 常用的 Starter 有哪些？
- Web 开发用哪个 Starter？
- Redis 用哪个 Starter？
- 官方 Starter 和第三方 Starter 的命名区别？
- Starter 引入了就一定生效吗？

---

## Q17: Spring Boot如何实现热部署

**考察点**: 热部署的实现方式、devtools原理

**难度**: 中等

**频率**: ⭐⭐⭐

**标准答案**:

### 1. 什么是热部署

**热部署**：在应用运行时，修改代码后不需要重新启动应用，就能让修改生效。

好处：提高开发效率，不用每次改代码都重启。

### 2. Spring Boot 热部署的方式

#### 方式1：spring-boot-devtools（推荐）

Spring Boot 官方提供的热部署工具。

**使用方法**：

1. 引入依赖：
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <optional>true</optional>
</dependency>
```

2. IDEA 中开启自动编译：
   - Settings → Build, Execution, Deployment → Compiler → 勾选 Build project automatically
   - Registry（Ctrl+Shift+Alt+/）→ 勾选 compiler.automake.allow.when.app.running

3. 修改代码后，IDEA 会自动编译，devtools 检测到 class 文件变化，自动重启。

**原理**：
- devtools 使用两个类加载器：
  - **base classloader**：加载不变化的类（第三方 jar 包中的类）
  - **restart classloader**：加载自己写的类
- 当代码修改后，restart classloader 被丢弃，重新创建一个，加载修改后的类
- 因为只重新加载自己的类，所以比完全重启快很多

**注意**：
- devtools 是开发环境用的，生产环境不要用
- `<optional>true</optional>` 表示只在本项目有效，不会传递给依赖它的项目

#### 方式2：Spring Loaded

JVM 插件，通过 -javaagent 方式启动，可以实现热部署。

现在用得比较少了，devtools 更方便。

#### 方式3：JRebel

商业软件，功能强大，收费。

- 支持类的热部署、配置文件热部署、页面热部署
- 比 devtools 更强大，几乎可以热部署所有修改
- 但收费，个人开发者可以申请免费 license

#### 方式4：IDEA 的 Debug 模式 + 自动编译

Debug 模式下，修改方法体可以热更新（Hot Swap），不需要重启。

但只能修改方法体，不能加方法、加字段、改类结构。

### 3. devtools 的原理

devtools 的核心是**类加载器**：

1. 启动时，用两个类加载器加载类：
   - base ClassLoader：加载第三方 jar 中的类（不会变）
   - restart ClassLoader：加载项目中的类（可能变化）

2. 当检测到 class 文件变化时：
   - 丢弃旧的 restart ClassLoader
   - 创建新的 restart ClassLoader
   - 重新加载项目中的类
   - base ClassLoader 不变

3. 因为只重新加载项目中的类，所以比完整重启快得多。

### 4. devtools 的其他功能

- **属性默认值**：自动禁用缓存（如 Thymeleaf 缓存），方便开发
- **自动重启**：类文件变化时自动重启
- **LiveReload**：资源变化时自动刷新浏览器
- **全局配置**：~/.spring-boot-devtools.properties

### 5. 生产环境不要用 devtools

devtools 是为开发环境设计的，生产环境要禁用：

1. 打包时排除 devtools
2. 设置 spring.devtools.restart.enabled=false
3. `<optional>true</optional>` 可以防止依赖传递

**答案解析**:

Spring Boot 热部署是开发中常用的功能，面试中偶尔会问到。

最常用的方式是 spring-boot-devtools，官方提供的，简单方便。

devtools 的原理是两个类加载器：base 加载不变的类，restart 加载项目的类。修改代码后重新创建 restart classloader，实现快速重启。

devtools 是"重启"不是"热替换"，它是重新加载类，不是在原有类上修改。JRebel 才是真正的热替换。

生产环境一定不要用 devtools。

**扩展问题**:
- Spring Boot 如何实现热部署？
- devtools 的原理是什么？
- devtools 生产环境能用吗？
- devtools 为什么重启快？
- 热部署和热加载有什么区别？

---

## Q18: Spring的后置处理器BeanPostProcessor

**考察点**: BeanPostProcessor的作用、执行时机、应用场景

**难度**: 困难

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 BeanPostProcessor

**BeanPostProcessor（Bean 后置处理器）**：是 Spring 提供的一个扩展接口，可以在 Bean 初始化的前后执行一些自定义逻辑。

它是 Spring 最重要的扩展点之一，很多功能都是基于它实现的。

### 2. BeanPostProcessor 接口定义

```java
public interface BeanPostProcessor {
    
    // Bean初始化前执行
    default Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        return bean;
    }
    
    // Bean初始化后执行
    default Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        return bean;
    }
}
```

两个方法：
- **postProcessBeforeInitialization**：在 Bean 初始化之前执行（init-method 之前）
- **postProcessAfterInitialization**：在 Bean 初始化之后执行（init-method 之后）

注意：返回值可以是原对象，也可以是包装后的对象（如代理对象）。

### 3. 执行时机

在 Bean 的生命周期中，BeanPostProcessor 的执行位置：

```
实例化 Bean
    ↓
属性赋值
    ↓
Aware 回调
    ↓
postProcessBeforeInitialization  ← 前置处理
    ↓
InitializingBean.afterPropertiesSet
    ↓
init-method
    ↓
postProcessAfterInitialization  ← 后置处理
    ↓
Bean 就绪
```

### 4. 自定义 BeanPostProcessor

```java
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {
    
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        System.out.println("初始化前：" + beanName);
        return bean; // 返回原对象
    }
    
    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        System.out.println("初始化后：" + beanName);
        return bean;
    }
}
```

只要把自定义的 BeanPostProcessor 注册到容器中（加 @Component），Spring 就会自动识别。

### 5. 典型应用场景

BeanPostProcessor 在 Spring 中应用非常广泛：

**（1）AOP 动态代理**
- AOP 就是在 postProcessAfterInitialization 中创建代理对象
- 如果 Bean 需要被代理，返回代理对象替换原对象

**（2）依赖注入（@Autowired）**
- @Autowired 注解的处理是通过 BeanPostProcessor 实现的
- 在属性赋值阶段处理

**（3）@Value 注解**
- @Value 注解的解析也是通过 BeanPostProcessor

**（4）@Resource 注解**
- CommonAnnotationBeanPostProcessor 处理 @Resource、@PostConstruct、@PreDestroy

**（5）自定义注解处理**
- 可以通过 BeanPostProcessor 处理自定义注解

### 6. 重要的 BeanPostProcessor 实现

Spring 中有很多 BeanPostProcessor 的实现：

- **AutowiredAnnotationBeanPostProcessor**：处理 @Autowired 注解
- **CommonAnnotationBeanPostProcessor**：处理 @Resource、@PostConstruct、@PreDestroy
- **AnnotationAwareAspectJAutoProxyCreator**：AOP 代理创建
- **ApplicationContextAwareProcessor**：处理 Aware 接口
- **InitDestroyAnnotationBeanPostProcessor**：处理 @PostConstruct、@PreDestroy

### 7. BeanFactoryPostProcessor

还有一个类似的接口：BeanFactoryPostProcessor（Bean 工厂后置处理器）。

- **BeanPostProcessor**：处理 Bean 对象（Bean 实例化后）
- **BeanFactoryPostProcessor**：处理 Bean 定义（Bean 实例化前）

BeanFactoryPostProcessor 可以修改 BeanDefinition，在 Bean 创建之前。

典型应用：PropertySourcesPlaceholderConfigurer（处理 ${...} 占位符）。

**答案解析**:

BeanPostProcessor 是 Spring 最重要的扩展点之一，也是面试难点。

它有两个方法：postProcessBeforeInitialization（初始化前）和 postProcessAfterInitialization（初始化后）。

很多 Spring 的核心功能都是通过 BeanPostProcessor 实现的：
- AOP 代理：在 postProcessAfterInitialization 中创建代理
- @Autowired 注入：处理属性注入
- @Resource、@PostConstruct 等注解处理

理解了 BeanPostProcessor，就能理解 Spring 很多功能的实现原理。

还要注意和 BeanFactoryPostProcessor 的区别：
- BeanPostProcessor：操作 Bean 实例
- BeanFactoryPostProcessor：操作 BeanDefinition（Bean 的定义信息）

**扩展问题**:
- BeanPostProcessor 的作用？
- 两个方法分别在什么时候执行？
- AOP 是在哪个方法中实现的？
- BeanPostProcessor 和 BeanFactoryPostProcessor 的区别？
- 有哪些常见的 BeanPostProcessor 实现？

---

## Q19: FactoryBean的作用

**考察点**: FactoryBean的概念、用法、和普通Bean的区别

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 FactoryBean

**FactoryBean**：是 Spring 提供的一个特殊的 Bean，它是一个**工厂 Bean**，可以用来创建其他 Bean。

普通 Bean 直接返回实例，FactoryBean 可以自定义创建 Bean 的过程。

### 2. FactoryBean 接口定义

```java
public interface FactoryBean<T> {
    
    // 返回创建的Bean对象
    T getObject() throws Exception;
    
    // 返回Bean的类型
    Class<?> getObjectType();
    
    // 是否是单例，默认true
    default boolean isSingleton() {
        return true;
    }
}
```

三个方法：
- **getObject()**：返回创建的 Bean 对象
- **getObjectType()**：返回 Bean 的类型
- **isSingleton()**：是否单例，默认单例

### 3. 使用示例

```java
public class UserFactoryBean implements FactoryBean<User> {
    
    private String name;
    private int age;
    
    @Override
    public User getObject() throws Exception {
        // 自定义创建User的过程
        User user = new User();
        user.setName(name);
        user.setAge(age);
        return user;
    }
    
    @Override
    public Class<?> getObjectType() {
        return User.class;
    }
    
    @Override
    public boolean isSingleton() {
        return true;
    }
    
    // setter
    public void setName(String name) {
        this.name = name;
    }
    public void setAge(int age) {
        this.age = age;
    }
}
```

### 4. 获取 FactoryBean 创建的对象

通过 getBean 获取时，默认获取的是 FactoryBean 创建的对象，不是 FactoryBean 本身。

```java
// 获取的是getObject()返回的User对象
User user = context.getBean("userFactoryBean", User.class);

// 获取FactoryBean本身，需要加&前缀
FactoryBean factory = context.getBean("&userFactoryBean", FactoryBean.class);
```

**规则**：
- `getBean("beanName")`：获取 FactoryBean 创建的对象
- `getBean("&beanName")`：获取 FactoryBean 本身

### 5. FactoryBean 和 BeanFactory 的区别

这两个名字很像，但完全不同：

| 特性 | BeanFactory | FactoryBean |
|------|-------------|-------------|
| 作用 | IOC 容器，管理所有 Bean | 工厂 Bean，创建一个 Bean |
| 地位 | 容器 | 被容器管理的 Bean |
| 用途 | 管理 Bean | 自定义 Bean 创建过程 |
| 获取 | 直接用 | getBean加&获取本身 |

### 6. 应用场景

FactoryBean 用于创建复杂的 Bean，当 Bean 的创建过程很复杂时，可以用 FactoryBean 封装。

**实际应用**：
- **MyBatis 的 SqlSessionFactoryBean**：创建 SqlSessionFactory
- **DruidDataSourceFactoryBean**：创建 Druid 数据源
- **各种第三方框架的集成**：需要复杂初始化的 Bean

以 MyBatis 为例：
```java
@Bean
public SqlSessionFactoryBean sqlSessionFactory(DataSource dataSource) {
    SqlSessionFactoryBean factoryBean = new SqlSessionFactoryBean();
    factoryBean.setDataSource(dataSource);
    // 各种配置...
    return factoryBean;
}
```

虽然返回的是 SqlSessionFactoryBean，但 Spring 会调用它的 getObject() 方法，实际注册到容器中的是 SqlSessionFactory。

### 7. 为什么需要 FactoryBean

有些 Bean 的创建过程非常复杂，不是简单的 new 一下就完事，需要很多配置和初始化。

FactoryBean 把复杂的创建过程封装起来，使用者只需要配置属性，不需要关心创建细节。

这是工厂模式的典型应用。

**答案解析**:

FactoryBean 是 Spring 中的一个重要概念，也是面试常考题。

FactoryBean 是一个特殊的 Bean，它的作用是创建其他 Bean。它是工厂模式的体现。

和普通 Bean 的区别：
- 普通 Bean：getBean 返回的是对象本身
- FactoryBean：getBean 返回的是 getObject() 的结果，加 & 才返回 FactoryBean 本身

FactoryBean 和 BeanFactory 的区别也要分清：
- BeanFactory 是容器（工厂）
- FactoryBean 是 Bean（工厂 Bean）

实际开发中，FactoryBean 常用于集成第三方框架，比如 MyBatis、Druid 等。

**扩展问题**:
- 什么是 FactoryBean？
- FactoryBean 和 BeanFactory 的区别？
- 如何获取 FactoryBean 本身？
- FactoryBean 有哪些应用场景？
- getObject() 和 getObjectType() 的作用？

---

## Q20: Spring Cloud的核心组件和功能

**考察点**: Spring Cloud各组件的作用、整体架构

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 Spring Cloud

Spring Cloud 是一系列框架的有序集合，利用 Spring Boot 的开发便利性，简化了分布式系统的开发。

它提供了微服务架构中常见的组件：服务注册与发现、配置中心、网关、负载均衡、熔断器、远程调用等。

### 2. 核心组件

#### （1）服务注册与发现

**Spring Cloud Netflix Eureka**（已停更）
- 服务注册中心
- 服务提供者注册服务，服务消费者发现服务
- CAP 中的 AP（高可用、分区容错）

**Spring Cloud Alibaba Nacos Discovery**（推荐）
- 阿里巴巴开源的服务注册中心
- 同时支持 AP 和 CP 模式
- 同时也是配置中心
- 功能更强大，国内使用广泛

**Spring Cloud Consul**：HashiCorp 开源的，也可以做服务注册和配置中心。

#### （2）配置中心

**Spring Cloud Config**
- Spring 官方的配置中心
- 基于 Git/SVN/本地文件存储配置
- 需要配合消息总线实现动态刷新

**Spring Cloud Alibaba Nacos Config**（推荐）
- 阿里巴巴开源的配置中心
- 支持动态刷新
- 支持多种格式（YAML、Properties、JSON等）
- 和服务注册中心整合在一起

#### （3）服务调用

**Spring Cloud OpenFeign**
- 声明式的 HTTP 客户端
- 像调用本地方法一样调用远程服务
- 底层用 Ribbon 做负载均衡
- 基于接口注解，非常优雅

**RestTemplate**：
- Spring 自带的 HTTP 客户端
- 可以配合 Ribbon 使用
- 没有 Feign 优雅

#### （4）负载均衡

**Spring Cloud Netflix Ribbon**（停更中）
- 客户端负载均衡
- 和 RestTemplate、Feign 配合使用
- 多种负载均衡策略：轮询、随机、加权等

**Spring Cloud LoadBalancer**（推荐）
- Spring 官方推出的负载均衡器
- 替代 Ribbon
- 功能相对简单，但足够用

#### （5）服务网关

**Spring Cloud Netflix Zuul**（已停更）
- 基于 Servlet 的网关
- 同步阻塞
- 性能一般

**Spring Cloud Gateway**（推荐）
- Spring 官方的网关
- 基于 WebFlux，响应式，异步非阻塞
- 性能更好
- 功能强大：路由、过滤、限流、熔断等

**Spring Cloud Alibaba Sentinel Gateway**：
- 集成 Sentinel 的网关限流

#### （6）熔断器/限流降级

**Spring Cloud Netflix Hystrix**（已停更）
- 熔断器，防止服务雪崩
- 支持降级、限流、熔断
- 已进入维护模式

**Spring Cloud Alibaba Sentinel**（推荐）
- 阿里巴巴开源的
- 流量控制、熔断降级、系统负载保护
- 功能强大，有控制台
- 国内使用广泛

**Resilience4j**：
- 另一个熔断组件，函数式编程风格

#### （7）消息驱动

**Spring Cloud Stream**
- 消息驱动的微服务
- 屏蔽底层消息中间件的差异
- 支持 RabbitMQ、Kafka

**Spring Cloud Bus**
- 消息总线
- 配合 Config 实现配置动态刷新
- 支持 RabbitMQ、Kafka

#### （8）链路追踪

**Spring Cloud Sleuth**
- 分布式链路追踪
- 给请求添加 traceId、spanId
- 需要配合 Zipkin、SkyWalking 等使用

**Spring Cloud Alibaba Seata**
- 分布式事务解决方案
- 支持 AT、TCC、SAGA 等模式

### 3. Spring Cloud 版本说明

Spring Cloud 的版本是用伦敦地铁站命名的：
- Greenwich、Hoxton、Istanbul、Jubilee 等

Spring Cloud Alibaba 是 Spring Cloud 的一个子项目，主要集成了阿里巴巴的开源组件。

### 4. 微服务整体架构

一个典型的 Spring Cloud 微服务架构：

```
用户请求
    ↓
API 网关（Gateway）
    ↓
服务调用（OpenFeign + LoadBalancer）
    ↓
服务注册与发现（Nacos）
    ↓
配置中心（Nacos Config）
    ↓
熔断降级（Sentinel）
    ↓
链路追踪（Sleuth + Zipkin/SkyWalking）
    ↓
各个微服务
```

### 5. 注意事项

Spring Cloud Netflix 很多组件已经停更（Eureka、Zuul、Hystrix、Ribbon），推荐用 Spring Cloud Alibaba 的替代方案。

目前国内最流行的技术栈是：**Spring Cloud Alibaba**（Nacos + Sentinel + Dubbo/Feign + Gateway）。

**答案解析**:

Spring Cloud 组件是面试常考题，特别是微服务相关的岗位。

核心组件需要记住：
1. 服务注册与发现：Nacos、Eureka
2. 配置中心：Nacos Config、Spring Cloud Config
3. 服务调用：OpenFeign、RestTemplate
4. 负载均衡：LoadBalancer、Ribbon
5. 网关：Gateway、Zuul
6. 熔断限流：Sentinel、Hystrix
7. 消息驱动：Stream、Bus
8. 链路追踪：Sleuth + Zipkin
9. 分布式事务：Seata

现在 Spring Cloud Netflix 很多组件停更了，推荐用 Spring Cloud Alibaba 的组件（Nacos、Sentinel）。

每个组件的基本作用要了解，不需要深入细节，但要知道是干什么的。

**扩展问题**:
- Spring Cloud 有哪些核心组件？
- 服务注册与发现用什么？
- 网关用什么？Gateway 和 Zuul 的区别？
- 熔断器用什么？Sentinel 和 Hystrix 的区别？
- Nacos 有什么功能？

---

## Reference

1. Spring官方文档. *Spring Framework Documentation*. https://docs.spring.io/spring-framework/docs/current/reference/html/, 访问时间：2026-07-28
2. Spring官方文档. *Spring Boot Reference Documentation*. https://docs.spring.io/spring-boot/docs/current/reference/html/, 访问时间：2026-07-28
3. 美团技术团队. *Spring事务实现原理*. https://tech.meituan.com, 访问时间：2026-07-28
4. 牛客网. *Spring/Spring Boot面试题精选*. https://www.nowcoder.com, 访问时间：2026-07-28
5. 阿里中间件团队. *Spring Cloud Alibaba官方文档*. https://sca.aliyun.com, 访问时间：2026-07-28

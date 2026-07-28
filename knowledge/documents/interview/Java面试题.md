---
title: Java后端开发工程师面试题
type: interview_questions
role: Java后端开发工程师
version: "0.2.0"
---

# Java后端开发工程师面试题

## 技术考察重点

- Java 基础（集合/多线程/JVM/GC）
- Spring Boot/MyBatis 原理和源码理解
- MySQL（索引/事务/锁/分库分表）
- Redis（数据类型/缓存策略/持久化）
- 计算机网络（HTTP/HTTPS/TCP）
- 操作系统（进程/线程/内存管理）

## 高频面试题

### Q1: HashMap 的底层实现原理？JDK 1.7 和 1.8 有什么区别？

- **类别**: Java基础
- **难度**: 中等
- **频率**: 极高

<details>
<summary>答题要点</summary>

**底层结构**：数组 + 链表/红黑树

**JDK 1.7**：数组 + 单向链表，头插法
**JDK 1.8**：数组 + 链表 + 红黑树（链表长度 ≥ 8 且数组长度 ≥ 64 时转红黑树），尾插法

**put 流程**：
1. 计算 key 的 hash 值 → 确定数组下标
2. 无冲突直接插入；有冲突用 equals 判断
3. 链表过长则转为红黑树

**1.8 改进**：
- 引入红黑树，避免极端情况下的 O(n) 查询
- 头插法改尾插法，解决扩容时的死循环问题
- hash 算法简化（高 16 位异或低 16 位）

</details>

---

### Q2: JVM 内存模型和垃圾回收机制？

- **类别**: JVM
- **难度**: 中等
- **频率**: 极高

<details>
<summary>答题要点</summary>

**内存模型**：
- 线程共享：堆（Heap）、方法区（元空间）
- 线程私有：虚拟机栈、本地方法栈、程序计数器

**堆的分代**：
- 新生代（Eden + S0 + S1）：Minor GC
- 老年代：Major GC / Full GC

**GC 算法**：
- 标记-清除：产生碎片
- 复制算法：新生代默认
- 标记-整理：老年代使用
- 分代收集：新生代复制 + 老年代标记整理

**垃圾收集器**：
- 新生代：Serial、ParNew、Parallel Scavenge
- 老年代：Serial Old、Parallel Old、CMS
- 全区域：G1（JDK 9+ 默认）、ZGC（低延迟）

</details>

---

### Q3: Spring 的 IOC 和 AOP 的理解和实现原理？

- **类别**: Spring
- **难度**: 中等
- **频率**: 极高

<details>
<summary>答题要点</summary>

**IOC（控制反转）**：
- 将对象的创建和管理交给 Spring 容器
- 通过 DI（依赖注入）实现：构造器注入、Setter 注入、字段注入（@Autowired）
- 核心：BeanFactory + ApplicationContext

**AOP（面向切面编程）**：
- 将横切关注点（日志、事务、权限）从业务代码中分离
- 实现原理：JDK 动态代理（接口）或 CGLIB 代理（类）
- 关键概念：切面（Aspect）、切点（Pointcut）、通知（Advice）

</details>

---

### Q4: MySQL 索引底层数据结构（B+Tree）？什么时候索引会失效？

- **类别**: 数据库
- **难度**: 中等
- **频率**: 极高

<details>
<summary>答题要点</summary>

**B+Tree 特点**：
- 非叶子节点只存 key 不存 data，叶子节点存完整数据
- 叶子节点通过双向链表连接，支持范围查询
- 高度通常 3-4 层，查找效率稳定 O(log n)

**索引失效场景**：
1. LIKE 以 % 开头（`LIKE '%abc'`）
2. 索引列上使用函数或计算（`WHERE YEAR(date) = 2024`）
3. 类型隐式转换（字符串不加引号）
4. OR 条件中有一个列无索引
5. 复合索引不满足最左前缀原则
6. 使用 != / <> / NOT IN

</details>

---

### Q5: Redis 缓存穿透/击穿/雪崩的区别和解决方案？

- **类别**: Redis
- **难度**: 中等
- **频率**: 极高

<details>
<summary>答题要点</summary>

| 问题 | 描述 | 解决方案 |
|------|------|----------|
| **缓存穿透** | 查询不存在的数据，请求穿透缓存直达 DB | 布隆过滤器、缓存空值（短 TTL） |
| **缓存击穿** | 热点 key 过期瞬间，大量请求打向 DB | 互斥锁、逻辑过期（永不过期+异步更新） |
| **缓存雪崩** | 大量 key 同时过期，导致 DB 压力骤增 | 过期时间加随机值、多级缓存、限流降级 |

</details>

---

### Q6: 线程池的核心参数和工作原理？

- **类别**: Java多线程
- **难度**: 中等
- **频率**: 高

<details>
<summary>答题要点</summary>

**七大参数**：
1. corePoolSize：核心线程数
2. maximumPoolSize：最大线程数
3. keepAliveTime：空闲线程存活时间
4. unit：时间单位
5. workQueue：阻塞队列
6. threadFactory：线程工厂
7. handler：拒绝策略（AbortPolicy/CallerRunsPolicy/DiscardPolicy/DiscardOldestPolicy）

**工作流程**：
核心线程 → 阻塞队列 → 最大线程 → 拒绝策略

</details>

---

### Q7: TCP 三次握手和四次挥手？为什么不是两次或四次？

- **类别**: 网络
- **难度**: 基础
- **频率**: 高

<details>
<summary>答题要点</summary>

**三次握手**：
1. SYN：客户端 → 服务端
2. SYN+ACK：服务端 → 客户端
3. ACK：客户端 → 服务端

**为什么是三次？** 防止旧连接请求（SYN）到达服务端，服务端误开连接。两次无法确认双方收发能力完好。

**四次挥手**：
1. FIN：主动方 → 被动方
2. ACK：被动方 → 主动方
3. FIN：被动方 → 主动方
4. ACK：主动方 → 被动方（2MSL 等待）

**为什么四次？** TCP 全双工，双方都要关闭自己的发送通道。被动方可能还有数据要发，ACK 和 FIN 分开发送。

</details>

---

### Q8: 分布式锁的实现方案和对比？

- **类别**: 分布式
- **难度**: 困难
- **频率**: 中

<details>
<summary>答题要点</summary>

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Redis (SETNX)** | 性能高，实现简单 | 需要处理锁过期续期（Redisson 看门狗） |
| **ZooKeeper** | 强一致性，自动释放 | 性能较低，实现复杂 |
| **MySQL** | 简单，已有的基础设施 | 性能差，不可靠 |

**Redis 实现要点**：
- `SET key value NX PX expire_time`（加锁）
- Lua 脚本释放锁（判断 value 后删除，保证原子性）
- Redisson 看门狗自动续期

</details>

---

### Q9: 如何设计一个短链接系统？

- **类别**: 系统设计
- **难度**: 困难
- **频率**: 中

<details>
<summary>答题要点</summary>

1. **功能需求**：长 URL → 短 URL，短 URL → 重定向到长 URL
2. **核心算法**：哈希（MurmurHash）+ 62 进制编码（0-9, a-z, A-Z），7 位字符可支持 ~3.5 万亿个短链接
3. **哈希冲突处理**：哈希后拼接递增序号再哈希
4. **存储**：MySQL + Redis 缓存热点 URL
5. **高并发**：发号器（预生成短码）、分布式 ID（雪花算法）
6. **301（永久）vs 302（临时）重定向**：302 方便统计点击量

</details>

---

### Q10: synchronized 和 ReentrantLock 的区别和使用场景？

- **类别**: Java多线程
- **难度**: 中等
- **频率**: 高

<details>
<summary>答题要点</summary>

| 对比维度 | synchronized | ReentrantLock |
|----------|-------------|---------------|
| 实现 | JVM 层面（monitor） | API 层面（AQS） |
| 锁释放 | 自动释放（代码块结束/异常） | 必须手动 unlock（finally 中） |
| 可中断 | 不支持 | lockInterruptibly() 支持 |
| 公平锁 | 非公平 | 可选公平/非公平 |
| 条件变量 | wait/notify（1个） | Condition（多个） |
| 尝试获取 | 不支持 | tryLock() 支持超时 |

**JDK 6+ synchronized 优化**：偏向锁 → 轻量级锁（自旋）→ 重量级锁，性能与 ReentrantLock 接近。简单场景优先使用 synchronized。

</details>

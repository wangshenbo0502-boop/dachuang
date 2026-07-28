---
title: "Java并发编程面试题（20题）"
category: "面试题"
type: "Java后端"
difficulty: "中等"
tags: ["并发编程", "多线程", "synchronized", "线程池", "AQS"]
source: ["Java并发编程的艺术", "JUC源码分析", "美团技术团队博客"]
last_update: "2026-07-28"
---

# Java并发编程面试题（20题）

> 本文档涵盖Java并发编程的核心知识点，包括线程安全、锁机制、线程池、并发容器、JUC工具类等重点内容，是中高级Java工程师面试的重中之重。

---

## Q1: 什么是线程安全

**考察点**: 线程安全的定义、竞态条件、原子性可见性有序性

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 线程安全的定义

当多个线程同时访问一个对象时，如果不用考虑这些线程在运行时环境下的调度和交替执行，也不需要进行额外的同步，或者在调用方进行任何其他的协调操作，调用这个对象的行为都可以获得正确的结果，那就称这个对象是线程安全的。

简单说：**多个线程同时访问，结果仍然正确**。

### 2. 线程安全的三要素

**（1）原子性（Atomicity）**

一个操作是不可分割的，要么全部执行，要么全部不执行，执行过程中不会被其他线程打断。

```java
// 非原子操作：i++分三步（读-改-写）
int i = 0;
i++; // 1.读取i 2.i+1 3.写回i

// 原子操作：synchronized或AtomicInteger
synchronized (this) {
    i++;
}
```

**（2）可见性（Visibility）**

一个线程修改了共享变量的值，其他线程能够立即看到修改后的值。

```java
// 可见性问题：线程修改了flag，主线程可能看不到
boolean flag = true;

// 线程1
new Thread(() -> {
    flag = false;
}).start();

// 主线程
while (flag) {
    // 可能一直循环，因为看不到flag的修改
}
```

解决方法：volatile、synchronized、final。

**（3）有序性（Ordering）**

程序执行的顺序按照代码的先后顺序执行。

CPU 和编译器可能会对指令进行重排序，单线程下没问题，但多线程下可能出现问题。

```java
// 有序性问题：指令重排导致意外结果
int a = 0;
boolean flag = false;

// 线程1
a = 1;        // 操作1
flag = true;  // 操作2
// 可能被重排为：先flag=true，再a=1

// 线程2
if (flag) {
    System.out.println(a); // 可能输出0
}
```

解决方法：volatile、synchronized、happens-before 原则。

### 3. 竞态条件

当多个线程访问共享数据时，如果执行顺序不同会导致结果不同，这就是竞态条件。

典型的竞态条件：
- 先检查后执行（Check-Then-Act）
- 读改写（Read-Modify-Write）

```java
// 先检查后执行
if (!list.contains(x)) { // 检查
    list.add(x);         // 执行
}
// 多个线程可能都通过检查，都add进去了
```

### 4. 实现线程安全的方法

1. **互斥同步**：synchronized、ReentrantLock
2. **非阻塞同步**：CAS、Atomic 原子类
3. **无同步方案**：
   - 栈封闭：局部变量，线程私有
   - 线程本地存储：ThreadLocal
   - 不可变对象：final、immutable

**答案解析**:

线程安全是并发编程的基础概念，也是面试必考题。

线程安全的三要素：原子性、可见性、有序性。这三个特性都需要保证，才能说是线程安全的。

原子性是说操作不可分割，可见性是说修改能被其他线程看到，有序性是说指令不会被乱序执行。

实现线程安全的方式有很多，最常用的是 synchronized 和各种并发工具类。

synchronized 可以同时保证三个特性：原子性（锁保证同一时间只有一个线程执行）、可见性（解锁前会把修改刷回主存）、有序性（锁的内存语义）。

**扩展问题**:
- 线程安全的三要素是什么？
- 原子性、可见性、有序性分别是什么？
- 如何保证线程安全？
- 什么是竞态条件？
- synchronized 能保证三个特性吗？

---

## Q2: synchronized 的底层原理

**考察点**: synchronized的实现、对象头、monitor、锁升级

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. synchronized 的使用方式

synchronized 可以用在三个地方：

**（1）修饰实例方法**
```java
public synchronized void method() {
    // 锁的是当前对象this
}
```

**（2）修饰静态方法**
```java
public static synchronized void method() {
    // 锁的是类的Class对象
}
```

**（3）修饰代码块**
```java
synchronized (obj) {
    // 锁的是obj对象
}
```

### 2. 底层原理：Monitor 监视器

synchronized 是基于对象头中的 Monitor（监视器锁）实现的。

**对象头（Object Header）**：
每个对象都有对象头，包含两部分：
1. **Mark Word（标记字段）**：存储对象的 hashCode、GC 年龄、锁信息等
2. **Klass Pointer（类型指针）**：指向对象所属类的元数据

**Mark Word 在不同锁状态下的内容**：

| 锁状态 | 25位 | 4位 | 1位(偏向锁) | 2位(锁标志位) |
|--------|------|-----|------------|--------------|
| 无锁 | 对象hashCode | 对象分代年龄 | 0 | 01 |
| 偏向锁 | 线程ID | Epoch | 1 | 01 |
| 轻量级锁 | 指向栈中锁记录的指针 | - | - | 00 |
| 重量级锁 | 指向monitor的指针 | - | - | 10 |
| GC标记 | 空 | - | - | 11 |

### 3. 锁的升级过程

JDK6 对 synchronized 做了大量优化，引入了锁升级机制：**无锁 → 偏向锁 → 轻量级锁 → 重量级锁**。

锁只能升级，不能降级（除了偏向锁可以重置为无锁）。

#### （1）偏向锁

**场景**：只有一个线程访问同步块。

**原理**：
- 当一个线程访问同步块时，会在对象头的 Mark Word 中存储线程 ID
- 以后这个线程进入时，不需要 CAS 加锁，直接判断线程 ID 是否是自己
- 如果是，直接进入，几乎没有额外开销

**优点**：只有一个线程时，性能极高，几乎无锁开销。

#### （2）轻量级锁

**场景**：多个线程交替访问同步块，没有竞争或竞争很轻。

**原理**：
- 当有另一个线程来竞争锁时，偏向锁升级为轻量级锁
- 线程在自己的栈帧中创建一个 Lock Record（锁记录）
- 用 CAS 尝试将对象头的 Mark Word 替换为指向 Lock Record 的指针
- 成功则获取锁，失败则自旋等待

**优点**：竞争不激烈时，性能比重量级锁好。

**自旋**：
- 竞争失败的线程不会立即阻塞，而是循环等待（自旋）
- 避免了线程切换的开销
- 但自旋会占用 CPU，长时间自旋浪费 CPU
- JDK6 引入自适应自旋，根据之前的自旋情况决定自旋次数

#### （3）重量级锁

**场景**：多个线程同时竞争，自旋失败多次。

**原理**：
- 轻量级锁自旋一定次数后还没获取到锁，就升级为重量级锁
- 依赖操作系统的 Mutex 互斥量
- 线程会被阻塞，进入等待队列
- 需要操作系统从用户态切换到内核态，开销大

### 4. 其他优化

**锁消除**：JIT 编译时，检测到不可能存在共享数据竞争的锁，就消除这个锁。

**锁粗化**：如果有一系列连续的操作都对同一个对象反复加锁解锁，会把锁的范围扩大到整个操作序列。

**答案解析**:

synchronized 的底层原理是面试高频考点，特别是锁升级过程。

JDK6 之前 synchronized 是重量级锁，性能差。JDK6 之后做了很多优化，引入了偏向锁、轻量级锁、自旋锁、自适应自旋、锁消除、锁粗化等，性能大大提升。

锁升级的过程：无锁 → 偏向锁 → 轻量级锁 → 重量级锁。
- 只有一个线程：偏向锁，性能最好
- 多个线程交替执行：轻量级锁，性能中等
- 多个线程同时竞争：重量级锁，性能最差

synchronized 是可重入的，一个线程可以多次获取同一把锁，锁的是对象，不是代码。

**扩展问题**:
- synchronized 的底层原理？
- 锁升级的过程是什么？
- 偏向锁、轻量级锁、重量级锁的区别？
- 对象头包含什么内容？
- 什么是自旋锁？什么是自适应自旋？

---

## Q3: synchronized 和 ReentrantLock 的区别

**考察点**: 两种锁的对比、功能差异、性能差异

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 基本介绍

**synchronized**：
- Java 关键字，JVM 层面实现
- 自动加锁和释放锁
- 可重入

**ReentrantLock**：
- JDK 提供的类，API 层面实现
- 需要手动加锁和释放锁
- 可重入
- 实现了 Lock 接口

### 2. 核心区别对比

| 特性 | synchronized | ReentrantLock |
|------|-------------|---------------|
| 实现层面 | JVM 关键字 | JDK API 类 |
| 锁的释放 | 自动释放 | 手动释放（必须在finally中unlock） |
| 可重入 | 是 | 是 |
| 公平锁 | 非公平 | 默认非公平，可设置为公平 |
| 可中断 | 不可中断 | 可中断（lockInterruptibly） |
| 超时获取 | 不支持 | 支持（tryLock 带超时） |
| 绑定条件 | 一个条件 | 可绑定多个 Condition |
| 性能 | JDK6后性能差不多 | 差不多 |
| 锁类型 | 悲观锁 | 悲观锁 |
| 底层实现 | Monitor | AQS |

### 3. 详细说明

#### （1）公平锁

- **synchronized**：只能是非公平锁
- **ReentrantLock**：默认非公平，构造函数传入 true 可设置为公平锁

公平锁：按照线程到达的顺序获取锁，先到先得。
非公平锁：新来的线程可以插队，可能先获取锁。

非公平锁性能更好，因为可以减少线程切换的开销。

```java
ReentrantLock fairLock = new ReentrantLock(true); // 公平锁
ReentrantLock unfairLock = new ReentrantLock(false); // 非公平锁（默认）
```

#### （2）可中断

- **synchronized**：不可中断，一个线程获取不到锁就一直阻塞
- **ReentrantLock**：可中断，用 lockInterruptibly() 方法，等待过程中可以响应中断

```java
reentrantLock.lockInterruptibly(); // 可中断的加锁
```

#### （3）超时获取

- **synchronized**：不支持，获取不到就一直等
- **ReentrantLock**：支持 tryLock 带超时时间，超时获取不到就放弃

```java
if (reentrantLock.tryLock(5, TimeUnit.SECONDS)) {
    try {
        // 5秒内获取到了锁
    } finally {
        reentrantLock.unlock();
    }
} else {
    // 超时没获取到锁
}
```

#### （4）绑定多个条件

- **synchronized**：只能有一个等待队列（wait/notify）
- **ReentrantLock**：可以有多个 Condition，每个 Condition 对应一个等待队列

```java
ReentrantLock lock = new ReentrantLock();
Condition notFull = lock.newCondition();
Condition notEmpty = lock.newCondition();
// 两个条件，分别对应不同的等待队列
```

这在实现生产者消费者模式时很有用。

### 4. 使用建议

- 优先使用 synchronized：简单、自动释放锁、不会出错
- 需要 ReentrantLock 的高级功能时（公平锁、可中断、超时、多条件），再用 ReentrantLock
- ReentrantLock 一定要在 finally 中释放锁，防止死锁

**答案解析**:

synchronized 和 ReentrantLock 是两种最常用的锁，也是面试高频考点。

JDK6 之前，ReentrantLock 性能比 synchronized 好很多。JDK6 之后，synchronized 做了很多优化（偏向锁、轻量级锁、自旋等），性能和 ReentrantLock 差不多了。

所以现在优先使用 synchronized，除非需要 ReentrantLock 的高级功能。

ReentrantLock 的高级功能：
1. 公平锁：按顺序获取锁
2. 可中断：等待过程中可以被中断
3. 超时获取：等一段时间，获取不到就放弃
4. 多条件：多个等待队列

两者都是可重入的，都是悲观锁。

**扩展问题**:
- synchronized 和 ReentrantLock 的区别？
- 什么是公平锁？什么是非公平锁？
- ReentrantLock 有哪些高级功能？
- 什么是可重入锁？
- 两者如何选择？

---

## Q4: volatile 关键字的作用和原理

**考察点**: volatile的两大作用、内存屏障、可见性有序性

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. volatile 的作用

volatile 是 Java 中的关键字，用于修饰变量。它有两个作用：

**（1）保证可见性**

当一个线程修改了 volatile 变量的值，新值对其他线程是立即可见的。

**（2）保证有序性（禁止指令重排序）**

volatile 会禁止指令重排序，保证代码执行的顺序性。

注意：volatile **不保证原子性**。

### 2. 保证可见性的原理

Java 内存模型（JMM）规定：
- 所有变量都存储在主内存中
- 每个线程有自己的工作内存（缓存）
- 线程对变量的操作都在工作内存中进行，不能直接读写主内存

普通变量的问题：
- 线程修改了变量，写回主内存的时机不确定
- 其他线程可能看不到修改

volatile 变量的特殊规则：
- **写操作**：修改 volatile 变量后，立即刷新回主内存
- **读操作**：读取 volatile 变量时，先从主内存刷新最新值到工作内存

这样保证了一个线程的修改对其他线程立即可见。

### 3. 保证有序性的原理

volatile 通过**内存屏障（Memory Barrier）**来禁止指令重排序。

内存屏障是一种 CPU 指令，作用是：
1. 保证屏障前的操作和屏障后的操作的顺序
2. 强制刷出各种 CPU 缓存，保证可见性

volatile 的内存屏障插入策略：
- 在每个 volatile **写操作**前插入 StoreStore 屏障，后插入 StoreLoad 屏障
- 在每个 volatile **读操作**后插入 LoadLoad 屏障和 LoadStore 屏障

简单理解：
- volatile 写之前的操作不会被重排到写之后
- volatile 读之后的操作不会被重排到读之前

这就是 volatile 的**内存语义**。

### 4. volatile 的应用场景

**（1）状态标记量**

```java
volatile boolean flag = true;

// 线程1
while (flag) {
    // 做事情
}

// 线程2
flag = false; // 线程1能立即看到
```

**（2）双重检查锁定（DCL）实现单例**

```java
public class Singleton {
    private volatile static Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {         // 第一次检查
            synchronized (Singleton.class) {
                if (instance == null) { // 第二次检查
                    instance = new Singleton(); // volatile防止指令重排
                }
            }
        }
        return instance;
    }
}
```

为什么要用 volatile？因为 `new Singleton()` 不是原子操作，可能被重排序：
1. 分配内存空间
2. 初始化对象
3. 将引用指向分配的内存

如果没有 volatile，步骤 2 和 3 可能被重排，导致另一个线程拿到一个未初始化的对象。

### 5. volatile 和 synchronized 的区别

| 特性 | volatile | synchronized |
|------|----------|-------------|
| 作用 | 修饰变量 | 修饰方法、代码块 |
| 原子性 | 不保证 | 保证 |
| 可见性 | 保证 | 保证 |
| 有序性 | 保证 | 保证 |
| 阻塞 | 不会阻塞 | 会阻塞 |
| 级别 | 轻量级 | 重量级 |

**答案解析**:

volatile 是并发编程的重要关键字，也是面试高频考点。

volatile 有两个作用：保证可见性和保证有序性。但它不保证原子性，这是最常考的点。

可见性是通过写回主内存、从主内存刷新实现的。有序性是通过内存屏障实现的。

volatile 最经典的应用是双重检查锁定的单例模式。为什么要用 volatile？因为防止指令重排序导致拿到未初始化的对象。

volatile 是轻量级的同步机制，不会造成线程阻塞，性能比 synchronized 好，但功能也有限（不保证原子性）。

**扩展问题**:
- volatile 的作用？
- volatile 能保证原子性吗？
- volatile 的可见性是怎么实现的？
- volatile 的有序性是怎么实现的？
- 双重检查锁定的单例为什么要用 volatile？

---

## Q5: 什么是 CAS，有什么问题

**考察点**: CAS的概念、原理、ABA问题、三大问题

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 CAS

**CAS（Compare And Swap，比较并交换）**：一种无锁原子操作。

**原理**：
CAS 有三个操作数：
- **V**：要读写的内存位置（变量的当前值）
- **A**：进行比较的预期值
- **B**：拟写入的新值

当且仅当 V 的值等于 A 时，CAS 才会用原子方式用新值 B 更新 V，否则什么都不做。

简单说：**我认为 V 应该是 A，如果是，就改成 B；如果不是，就不改，告诉我现在是多少。**

```java
// 伪代码
boolean compareAndSwap(V, A, B) {
    if (V == A) {
        V = B;
        return true;
    }
    return false;
}
```

CAS 是 CPU 级别的原子指令，由硬件保证原子性。

### 2. CAS 的应用

**Atomic 原子类**：AtomicInteger、AtomicLong 等都是用 CAS 实现的。

```java
AtomicInteger atomicInt = new AtomicInteger(0);
atomicInt.incrementAndGet(); // 原子递增，底层用CAS
```

**AtomicInteger 的 getAndAdd 源码**：
```java
public final int getAndAddInt(Object o, long offset, int delta) {
    int v;
    do {
        v = getIntVolatile(o, offset); // 读取当前值
    } while (!compareAndSwapInt(o, offset, v, v + delta)); // CAS尝试更新
    return v;
}
```

这就是**自旋 CAS**：不成功就一直重试，直到成功。

### 3. CAS 的优点

- **无锁**：不需要加锁，线程不会阻塞
- **性能好**：竞争不激烈时，性能比锁好
- **非阻塞**：一个线程失败不会影响其他线程

### 4. CAS 的三大问题

#### （1）ABA 问题

**问题**：
如果一个变量原来是 A，变成了 B，又变回了 A，那么 CAS 会误认为它从来没有变过。

```
线程1：读取值为A
线程2：把A改成B
线程2：把B改回A
线程1：CAS操作，发现还是A，认为没变过，更新成功
```

虽然值没变，但实际上中间发生过变化，在某些场景下这是有问题的。

**解决方法**：使用**版本号**或**时间戳**。
- 每次变量更新时，版本号加 1
- CAS 时比较版本号，而不是只比较值
- Java 中提供了 AtomicStampedReference 和 AtomicMarkableReference

#### （2）循环时间长开销大

**问题**：
自旋 CAS 如果长时间不成功，会一直循环，占用 CPU 资源。

```java
while (!compareAndSwap(...)) {
    // 一直循环，占用CPU
}
```

**解决方法**：
- 自适应自旋：根据之前的自旋情况调整自旋次数
- 一定次数后失败，退化为阻塞
- JVM 支持 pause 指令，减少 CPU 消耗

#### （3）只能保证一个共享变量的原子操作

**问题**：
CAS 只能对一个共享变量执行原子操作，不能同时保证多个变量的原子性。

**解决方法**：
- 用锁（synchronized、Lock）
- 把多个变量合成一个对象，用 AtomicReference 保证引用的原子性
- Java 中提供了 AtomicReference，可以保证对象引用的原子更新

### 5. CAS 和 synchronized 的对比

| 特性 | CAS | synchronized |
|------|-----|-------------|
| 类型 | 乐观锁 | 悲观锁 |
| 阻塞 | 不阻塞 | 阻塞 |
| 适用场景 | 竞争少，读多写少 | 竞争多，写多 |
| 原子操作数 | 单个变量 | 整个代码块 |
| ABA问题 | 有 | 无 |

**答案解析**:

CAS 是乐观锁的实现方式，也是面试高频考点。

CAS 的核心思想是：先比较再更新，如果预期值和实际值一致就更新，否则重试。

CAS 的三大问题：ABA 问题、循环时间长开销大、只能保证一个变量的原子操作。其中 ABA 问题是最常考的。

ABA 问题的解决方法是加版本号，Java 中提供了 AtomicStampedReference。

AtomicInteger 等原子类就是用 CAS + 自旋实现的，性能比 synchronized 好，适合竞争不激烈的场景。

**扩展问题**:
- 什么是 CAS？原理是什么？
- CAS 有什么缺点？
- 什么是 ABA 问题？如何解决？
- CAS 和 synchronized 的区别？
- AtomicInteger 的实现原理？

---

## Q6: ThreadLocal 的原理和内存泄漏问题

**考察点**: ThreadLocal的原理、ThreadLocalMap、内存泄漏原因

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 ThreadLocal

ThreadLocal 是线程本地变量，每个线程都有自己的副本，线程之间互不干扰。

```java
ThreadLocal<String> threadLocal = new ThreadLocal<>();

// 线程1
threadLocal.set("value1");
System.out.println(threadLocal.get()); // value1

// 线程2
threadLocal.set("value2");
System.out.println(threadLocal.get()); // value2
```

每个线程有自己独立的值，互不影响。

### 2. 底层原理

每个 Thread 对象都有一个 `threadLocals` 成员变量，类型是 `ThreadLocal.ThreadLocalMap`。

```java
// Thread类的成员变量
ThreadLocal.ThreadLocalMap threadLocals = null;
```

ThreadLocalMap 是一个自定义的 Map，key 是 ThreadLocal 对象本身，value 是要存储的值。

```
Thread
└── threadLocals (ThreadLocalMap)
    ├── Entry(threadLocal1, value1)
    ├── Entry(threadLocal2, value2)
    └── ...
```

**set 方法**：
```java
public void set(T value) {
    Thread t = Thread.currentThread();
    ThreadLocalMap map = getMap(t);
    if (map != null)
        map.set(this, value); // key是ThreadLocal本身
    else
        createMap(t, value);
}
```

**get 方法**：
```java
public T get() {
    Thread t = Thread.currentThread();
    ThreadLocalMap map = getMap(t);
    if (map != null) {
        ThreadLocalMap.Entry e = map.getEntry(this);
        if (e != null) {
            @SuppressWarnings("unchecked")
            T result = (T)e.value;
            return result;
        }
    }
    return setInitialValue();
}
```

简单说：**每个线程有自己的 ThreadLocalMap，key 是 ThreadLocal 对象，value 是存储的值。**

### 3. ThreadLocalMap 的结构

ThreadLocalMap 是一个自定义的哈希表，和 HashMap 类似，但有区别：

- 底层是 Entry 数组
- Entry 继承自 WeakReference（弱引用）
- key 是 ThreadLocal（弱引用）
- value 是存储的值（强引用）

```java
static class Entry extends WeakReference<ThreadLocal<?>> {
    Object value;
    Entry(ThreadLocal<?> k, Object v) {
        super(k);
        value = v;
    }
}
```

### 4. 内存泄漏问题

**什么是内存泄漏**：对象已经没用了，但无法被 GC 回收，导致内存越用越少。

**为什么会内存泄漏**：

1. ThreadLocalMap 的 key 是弱引用，当 ThreadLocal 没有强引用时，下次 GC key 就会被回收
2. 但 value 是强引用，不会被回收
3. 如果线程一直活着（比如线程池中的线程），ThreadLocalMap 也一直活着
4. 这些 key 为 null 的 Entry 的 value 就一直被引用着，无法回收
5. 导致内存泄漏

```
Thread → ThreadLocalMap → Entry(key为null, value强引用)
```

**为什么 key 设计成弱引用**：
如果 key 是强引用，即使 ThreadLocal 对象被回收了，key 还会强引用它，导致 ThreadLocal 也无法回收，泄漏更严重。

弱引用至少能让 ThreadLocal 对象被回收，key 变成 null。

**如何避免内存泄漏**：
- 使用完 ThreadLocal 后，调用 **remove() 方法**手动清除
- 这是最佳实践

```java
try {
    threadLocal.set(value);
    // 使用
} finally {
    threadLocal.remove(); // 用完清除，防止内存泄漏
}
```

ThreadLocalMap 自己也有一些清理机制（set、get、remove 时会清理一些 key 为 null 的 Entry），但不是每次都清理，不能完全依赖。

### 5. ThreadLocal 的应用场景

1. **每个线程需要独立副本**：比如 SimpleDateFormat，每个线程一个实例
2. **传递上下文信息**：用户信息、请求 ID 等，在方法调用链中传递
3. **数据库连接管理**：每个线程一个连接
4. **事务管理**：保证同一个线程用同一个连接
5. **MDC 日志**：日志中添加请求追踪信息

**答案解析**:

ThreadLocal 是面试高频考点，特别是内存泄漏问题。

ThreadLocal 的原理：每个线程有自己的 ThreadLocalMap，key 是 ThreadLocal 对象，value 是存储的值。这样每个线程都有自己的副本，互不干扰。

内存泄漏是重点：key 是弱引用，value 是强引用。ThreadLocal 被回收后，key 变成 null，但 value 还被 Entry 引用着，而 Entry 又被 ThreadLocalMap 引用，ThreadLocalMap 被 Thread 引用。如果线程一直活着，value 就永远无法回收，导致内存泄漏。

解决方法是使用完后手动调用 remove() 方法。

线程池中的线程尤其要注意，因为线程会被复用，如果不清理，下一个任务可能拿到上一个任务的值，而且会内存泄漏。

**扩展问题**:
- ThreadLocal 的原理是什么？
- ThreadLocal 为什么会内存泄漏？
- 如何避免 ThreadLocal 内存泄漏？
- ThreadLocalMap 的 key 为什么是弱引用？
- ThreadLocal 有哪些应用场景？

---

## Q7: 线程池的核心参数和工作原理

**考察点**: 线程池的7个核心参数、执行流程、拒绝策略

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是线程池

线程池是一种池化技术，预先创建一些线程，放在池子里，需要的时候直接用，用完放回去，避免频繁创建和销毁线程。

**好处**：
1. 降低资源消耗：重复利用已创建的线程
2. 提高响应速度：任务来了直接用线程，不需要等待创建
3. 提高线程的可管理性：统一管理线程，避免无限创建

### 2. 核心参数

ThreadPoolExecutor 有 7 个核心参数：

```java
public ThreadPoolExecutor(
    int corePoolSize,           // 核心线程数
    int maximumPoolSize,        // 最大线程数
    long keepAliveTime,         // 非核心线程空闲存活时间
    TimeUnit unit,              // 时间单位
    BlockingQueue<Runnable> workQueue,  // 任务队列
    ThreadFactory threadFactory,        // 线程工厂
    RejectedExecutionHandler handler    // 拒绝策略
)
```

#### （1）corePoolSize（核心线程数）
- 线程池中长期保持的线程数
- 即使这些线程是空闲的，也不会被销毁
- 可以设置 allowCoreThreadTimeOut 让核心线程也超时销毁

#### （2）maximumPoolSize（最大线程数）
- 线程池最多能创建的线程数
- 核心线程 + 非核心线程

#### （3）keepAliveTime（非核心线程空闲存活时间）
- 非核心线程空闲多久后被销毁
- 如果 allowCoreThreadTimeOut=true，核心线程也会受这个时间限制

#### （4）unit（时间单位）
- keepAliveTime 的时间单位
- 秒、毫秒、微秒等

#### （5）workQueue（任务队列）
- 存放等待执行任务的阻塞队列
- 常见的：
  - ArrayBlockingQueue：有界队列，数组实现
  - LinkedBlockingQueue：无界队列（默认容量 Integer.MAX_VALUE），链表实现
  - SynchronousQueue：不存储任务，直接交给线程
  - PriorityBlockingQueue：优先级队列

#### （6）threadFactory（线程工厂）
- 创建线程的工厂
- 可以给线程设置名字、优先级、是否守护线程等
- 默认使用 Executors.defaultThreadFactory()

#### （7）handler（拒绝策略）
- 线程池满了（线程数达到最大且队列也满了），新任务怎么处理
- 四种内置拒绝策略：
  1. **AbortPolicy**：抛出异常（默认）
  2. **CallerRunsPolicy**：由调用线程自己执行
  3. **DiscardPolicy**：直接丢弃任务
  4. **DiscardOldestPolicy**：丢弃队列中最老的任务，重试当前任务

### 3. 工作原理（执行流程）

提交一个新任务时，线程池的处理流程：

1. **当前线程数 < corePoolSize**：创建核心线程执行任务
2. **当前线程数 >= corePoolSize**：任务加入任务队列
3. **任务队列满了**：创建非核心线程执行任务
4. **当前线程数 == maximumPoolSize**：执行拒绝策略

```
新任务
  ↓
当前线程数 < 核心线程数？
  ├─ 是 → 创建核心线程执行
  └─ 否 → 队列满了吗？
          ├─ 否 → 加入队列
          └─ 是 → 当前线程数 < 最大线程数？
                  ├─ 是 → 创建非核心线程执行
                  └─ 否 → 执行拒绝策略
```

### 4. 为什么用核心线程 + 队列 + 非核心线程的设计？

这是一种折中设计：
- 核心线程：保证基本的处理能力
- 任务队列：缓冲任务，避免频繁创建销毁线程
- 非核心线程：应对突增的任务量

既不会因为线程太少处理不过来，也不会因为线程太多浪费资源。

**答案解析**:

线程池是面试最高频的考点之一，必须熟练掌握。

7 个核心参数：核心线程数、最大线程数、空闲时间、时间单位、任务队列、线程工厂、拒绝策略。

执行流程：核心线程 → 队列 → 非核心线程 → 拒绝策略。这个顺序很重要，是先排队再扩容，不是先扩容再排队。

四种拒绝策略需要记住：
1. AbortPolicy：抛异常（默认）
2. CallerRunsPolicy：调用者自己执行
3. DiscardPolicy：直接丢弃
4. DiscardOldestPolicy：丢最老的，重试

实际使用中，不推荐用 Executors 创建线程池，要手动用 ThreadPoolExecutor 创建，避免资源耗尽。

**扩展问题**:
- 线程池的核心参数有哪些？
- 线程池的执行流程？
- 拒绝策略有哪些？
- 常见的任务队列有哪些？
- 为什么不推荐用 Executors 创建线程池？

---

## Q8: 常见的线程池类型和适用场景

**考察点**: Executors提供的四种线程池、各自的特点和适用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

Executors 类提供了四种常见的线程池：

### 1. FixedThreadPool（固定大小线程池）

```java
ExecutorService pool = Executors.newFixedThreadPool(10);
```

**特点**：
- 核心线程数 = 最大线程数，都是 nThreads
- 没有非核心线程
- 任务队列是 LinkedBlockingQueue（无界）
- 线程数固定，不会变

**构造**：
```java
new ThreadPoolExecutor(
    nThreads, nThreads,
    0L, TimeUnit.MILLISECONDS,
    new LinkedBlockingQueue<Runnable>()
)
```

**适用场景**：
- 任务量比较稳定
- 需要控制并发线程数
- 长期执行的任务

**注意**：
- 队列是无界的，如果任务提交太快，队列可能无限增长，导致 OOM

### 2. CachedThreadPool（缓存线程池）

```java
ExecutorService pool = Executors.newCachedThreadPool();
```

**特点**：
- 核心线程数 = 0
- 最大线程数 = Integer.MAX_VALUE（几乎无限）
- 任务队列是 SynchronousQueue（不存储任务）
- 空闲线程 60 秒后销毁
- 来一个任务就创建一个线程（如果没有空闲线程）

**构造**：
```java
new ThreadPoolExecutor(
    0, Integer.MAX_VALUE,
    60L, TimeUnit.SECONDS,
    new SynchronousQueue<Runnable>()
)
```

**适用场景**：
- 大量短生命周期的任务
- 任务量大但执行时间短
- 突发的大量任务

**注意**：
- 最大线程数是 Integer.MAX_VALUE，如果任务太多，可能创建大量线程，导致 OOM

### 3. SingleThreadExecutor（单线程线程池）

```java
ExecutorService pool = Executors.newSingleThreadExecutor();
```

**特点**：
- 核心线程数 = 最大线程数 = 1
- 只有一个线程
- 任务队列是 LinkedBlockingQueue（无界）
- 任务按顺序执行

**构造**：
```java
new ThreadPoolExecutor(
    1, 1,
    0L, TimeUnit.MILLISECONDS,
    new LinkedBlockingQueue<Runnable>()
)
```

**适用场景**：
- 需要保证任务按顺序执行
- 只有一个工作线程

**注意**：
- 队列无界，可能 OOM

### 4. ScheduledThreadPool（定时任务线程池）

```java
ScheduledExecutorService pool = Executors.newScheduledThreadPool(5);
```

**特点**：
- 核心线程数指定，最大线程数 Integer.MAX_VALUE
- 任务队列是 DelayedWorkQueue（延迟队列）
- 支持定时和周期性任务

**常用方法**：
```java
// 延迟执行
schedule(Runnable command, long delay, TimeUnit unit)

// 固定频率执行（以上一次开始时间为基准）
scheduleAtFixedRate(Runnable command, long initialDelay, long period, TimeUnit unit)

// 固定延迟执行（以上一次结束时间为基准）
scheduleWithFixedDelay(Runnable command, long initialDelay, long delay, TimeUnit unit)
```

**适用场景**：
- 定时任务
- 周期性任务

### 5. 对比总结

| 线程池类型 | 核心线程 | 最大线程 | 队列 | 特点 | 适用场景 |
|-----------|---------|---------|------|------|---------|
| FixedThreadPool | 固定 | 固定 | 无界队列 | 线程数固定 | 任务稳定 |
| CachedThreadPool | 0 | 无限 | 同步队列 | 按需创建线程 | 大量短任务 |
| SingleThreadExecutor | 1 | 1 | 无界队列 | 单线程顺序执行 | 顺序任务 |
| ScheduledThreadPool | 指定 | 无限 | 延迟队列 | 定时任务 | 定时/周期任务 |

### 6. 为什么《阿里巴巴Java开发手册》不推荐用 Executors？

**原因**：
- FixedThreadPool 和 SingleThreadExecutor：队列是无界的（LinkedBlockingQueue），可能堆积大量任务导致 OOM
- CachedThreadPool 和 ScheduledThreadPool：最大线程数是 Integer.MAX_VALUE，可能创建大量线程导致 OOM

**推荐**：
- 手动用 ThreadPoolExecutor 创建线程池
- 根据业务场景设置合理的参数
- 使用有界队列，控制资源

**答案解析**:

四种常见的线程池是面试常考题。需要记住每种线程池的特点和适用场景。

FixedThreadPool：固定线程数，适合任务量稳定的场景。
CachedThreadPool：缓存线程，适合大量短任务。
SingleThreadExecutor：单线程，保证顺序执行。
ScheduledThreadPool：定时任务。

但这四种线程池都有 OOM 的风险，要么队列无界，要么线程数无界。所以阿里巴巴开发手册推荐手动创建 ThreadPoolExecutor，自己设置参数。

实际开发中，要根据任务类型（CPU密集型/IO密集型）、任务量、系统资源等来设置合理的参数。

**扩展问题**:
- 常见的线程池有哪些？
- FixedThreadPool 和 CachedThreadPool 的区别？
- 为什么不推荐用 Executors 创建线程池？
- ScheduledThreadPool 有哪些方法？
- 如何合理设置核心线程数？

---

## Q9: 什么是死锁，如何避免

**考察点**: 死锁的四个必要条件、如何避免和排查

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是死锁

**死锁**：两个或多个线程在执行过程中，因争夺资源而造成的一种互相等待的现象，如果没有外力干涉，它们都将无法推进下去。

```java
// 死锁示例
Object lockA = new Object();
Object lockB = new Object();

// 线程1：先拿A，再拿B
new Thread(() -> {
    synchronized (lockA) {
        System.out.println("线程1拿到了锁A");
        try { Thread.sleep(100); } catch (InterruptedException e) {}
        synchronized (lockB) {
            System.out.println("线程1拿到了锁B");
        }
    }
}).start();

// 线程2：先拿B，再拿A
new Thread(() -> {
    synchronized (lockB) {
        System.out.println("线程2拿到了锁B");
        try { Thread.sleep(100); } catch (InterruptedException e) {}
        synchronized (lockA) {
            System.out.println("线程2拿到了锁A");
        }
    }
}).start();
```

线程1拿着锁A等锁B，线程2拿着锁B等锁A，互相等待，永远等不到，这就是死锁。

### 2. 死锁的四个必要条件

死锁必须同时满足以下四个条件，缺一不可：

**（1）互斥条件**
- 资源只能被一个线程占用
- 其他请求线程只能等待

**（2）请求与保持条件**
- 线程已经持有了至少一个资源
- 又请求其他被其他线程持有的资源
- 请求的同时不释放已有的资源

**（3）不可剥夺条件**
- 已获得的资源不能被其他线程强行剥夺
- 只能自己释放

**（4）循环等待条件**
- 存在一个线程等待资源的循环链
- 每个线程都在等待下一个线程持有的资源

### 3. 如何避免死锁

破坏四个必要条件中的任意一个，就能避免死锁。

#### （1）破坏互斥条件
- 资源可以共享，不互斥
- 比较难，因为很多资源本身就需要互斥

#### （2）破坏请求与保持条件
- 一次性申请所有需要的资源
- 要么全拿到，要么一个都不拿
- 缺点：资源利用率低

```java
// 一次性申请所有锁
if (tryLockAll(lockA, lockB)) {
    try {
        // 执行业务
    } finally {
        unlockAll(lockA, lockB);
    }
}
```

#### （3）破坏不可剥夺条件
- 持有部分资源的线程，如果申请不到其他资源，就释放已有的资源
- 可以用 ReentrantLock 的 tryLock 实现

```java
if (lockA.tryLock()) {
    try {
        if (lockB.tryLock(1, TimeUnit.SECONDS)) {
            try {
                // 执行业务
            } finally {
                lockB.unlock();
            }
        }
    } finally {
        lockA.unlock();
    }
}
```

#### （4）破坏循环等待条件
- 所有线程按相同的顺序获取锁
- 给资源编号，按编号从小到大获取
- 最常用也最有效的方法

```java
// 两个线程都先拿A，再拿B，就不会死锁了
// 线程1：A → B
// 线程2：A → B
```

### 4. 死锁排查

**（1）jstack 命令**
```bash
jstack <pid>
```
jstack 会检测死锁，并输出死锁信息。

**（2）jconsole / VisualVM**
图形化工具，可以检测死锁。

**（3）代码检测**
用 ThreadMXBean 检测：
```java
ThreadMXBean bean = ManagementFactory.getThreadMXBean();
long[] deadlockedThreads = bean.findDeadlockedThreads();
if (deadlockedThreads != null) {
    // 发现死锁
}
```

**答案解析**:

死锁是并发编程中的经典问题，也是面试必考题。

死锁的四个必要条件：互斥、请求与保持、不可剥夺、循环等待。四个条件同时满足才会死锁。

避免死锁的方法就是破坏其中一个条件。最常用的是破坏循环等待条件（按顺序获取锁）和破坏不可剥夺条件（tryLock 超时释放）。

排查死锁最常用的是 jstack 命令，它可以自动检测死锁。

实际开发中，要注意锁的顺序，尽量按相同的顺序获取锁，减少死锁的概率。

**扩展问题**:
- 什么是死锁？
- 死锁的四个必要条件？
- 如何避免死锁？
- 如何排查死锁？
- 如何用 jstack 检测死锁？

---

## Q10: wait 和 sleep 的区别

**考察点**: wait和sleep的区别、所属类、锁的释放、唤醒方式

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 核心区别对比

| 特性 | wait() | sleep() |
|------|--------|---------|
| 所属类 | Object 类的方法 | Thread 类的静态方法 |
| 作用 | 线程间通信/协作 | 让线程暂停一段时间 |
| 锁的释放 | 会释放锁 | 不会释放锁 |
| 使用位置 | 必须在同步方法/同步块中 | 任何地方 |
| 唤醒方式 | notify() / notifyAll() / 超时 | 时间到 / interrupt() |
| 异常 | InterruptedException | InterruptedException |

### 2. 详细说明

#### （1）所属类不同

- **wait()**：是 Object 类的方法，每个对象都有
- **sleep()**：是 Thread 类的静态方法

为什么 wait 在 Object 类？
因为 wait 和锁有关，每个对象都可以作为锁（monitor），所以每个对象都应该有 wait 方法。

#### （2）锁的释放不同（最核心的区别）

- **wait()**：调用后会释放锁，其他线程可以获取锁
- **sleep()**：调用后不会释放锁，抱着锁睡觉

```java
// wait 会释放锁
synchronized (obj) {
    obj.wait(); // 释放锁，其他线程可以进入同步块
}

// sleep 不释放锁
synchronized (obj) {
    Thread.sleep(1000); // 抱着锁睡1秒，其他线程进不来
}
```

#### （3）使用位置不同

- **wait()**：必须在同步方法或同步块中调用（必须先获取锁）
- **sleep()**：可以在任何地方调用

如果 wait 不在同步块中调用，会抛出 IllegalMonitorStateException。

#### （4）唤醒方式不同

- **wait()**：被 notify() 或 notifyAll() 唤醒，或超时
- **sleep()**：睡眠时间到了自动唤醒，或被 interrupt() 中断

#### （5）用途不同

- **wait()**：用于线程间通信，生产者消费者模式
- **sleep()**：只是让线程暂停一段时间

### 3. 为什么 wait 要在同步块中调用

因为 wait 是要释放锁的，如果没有锁，怎么释放？所以必须先获取锁，才能调用 wait。

而且为了避免丢失唤醒信号（信号丢失问题），也需要在同步块中调用。

### 4. 示例：生产者消费者模式

```java
// 生产者
synchronized (queue) {
    while (queue.isFull()) {
        queue.wait(); // 队列满了，等待
    }
    queue.add(item);
    queue.notifyAll(); // 通知消费者
}

// 消费者
synchronized (queue) {
    while (queue.isEmpty()) {
        queue.wait(); // 队列空了，等待
    }
    queue.take();
    queue.notifyAll(); // 通知生产者
}
```

**答案解析**:

wait 和 sleep 的区别是经典面试题，也是必考题。

最核心的区别是：wait 会释放锁，sleep 不会释放锁。

其他区别：
- wait 是 Object 的方法，sleep 是 Thread 的静态方法
- wait 必须在同步块中调用，sleep 不需要
- wait 用 notify 唤醒，sleep 时间到了自动醒

wait 和 notify/notifyAll 一起使用，实现线程间的协作，比如生产者消费者模式。

注意 wait 要用 while 循环判断条件，而不是 if，因为可能有虚假唤醒（spurious wakeup）。

**扩展问题**:
- wait 和 sleep 的区别？
- 为什么 wait() 定义在 Object 类中？
- 为什么 wait 必须在同步块中调用？
- 为什么 wait 要用 while 循环而不是 if？
- notify 和 notifyAll 的区别？

---

## Q11: 什么是 AQS（抽象队列同步器）

**考察点**: AQS的原理、state变量、CLH队列、两种模式

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 AQS

**AQS（AbstractQueuedSynchronizer，抽象队列同步器）**：是 Java 并发包中很多同步工具的基础框架。

很多 JUC 工具类都是基于 AQS 实现的，比如：
- ReentrantLock
- ReentrantReadWriteLock
- Semaphore
- CountDownLatch
- CyclicBarrier（内部用的是 Generation，但思想类似）
- FutureTask

AQS 解决了实现同步器时涉及的大量细节问题：同步状态的原子性管理、线程的阻塞与解除阻塞、队列管理等。

### 2. 核心思想

AQS 的核心思想：
- 用一个 **volatile 的 int 变量 state** 表示同步状态
- 用一个 **CLH 队列**（双向链表）存放等待的线程
- 线程获取不到锁时，加入队列等待
- 锁释放时，唤醒队列中的等待线程

### 3. 核心组成

#### （1）state 状态变量

```java
private volatile int state;
```

- 用 volatile 保证可见性
- 通过 CAS 原子修改
- state 的含义由子类定义：
  - ReentrantLock：state 表示锁的重入次数
  - Semaphore：state 表示剩余许可数
  - CountDownLatch：state 表示剩余计数

#### （2）CLH 等待队列

CLH 是一个**双向链表队列**，存放等待的线程。

```
      head <--> node1 <--> node2 <--> ... <--> tail
```

每个节点（Node）包含：
- thread：等待的线程
- waitStatus：等待状态
- prev / next：前后指针
- nextWaiter：下一个等待条件的节点

当线程获取锁失败时，会被封装成 Node 加入队列尾部。
当锁被释放时，会唤醒头节点的后继节点。

#### （3）两种模式

AQS 支持两种模式：

**独占模式（Exclusive）**：
- 同一时间只能有一个线程持有锁
- 如 ReentrantLock
- 核心方法：tryAcquire、tryRelease

**共享模式（Share）**：
- 同一时间可以有多个线程持有
- 如 Semaphore、CountDownLatch、ReadWriteLock 的读锁
- 核心方法：tryAcquireShared、tryReleaseShared

### 4. 工作原理

**获取锁（独占模式）**：
1. 尝试获取锁（tryAcquire）
2. 成功：直接返回
3. 失败：
   - 封装成 Node 加入队列尾部
   - 进入循环，检查自己是不是 head 的下一个节点
   - 如果是，再尝试获取锁
   - 如果还是失败，挂起自己（LockSupport.park()）
   - 等待被唤醒

**释放锁（独占模式）**：
1. 释放锁（tryRelease）
2. 唤醒头节点的后继节点（LockSupport.unpark()）
3. 被唤醒的线程重新尝试获取锁

### 5. 模板方法模式

AQS 使用了模板方法模式：
- AQS 定义了整体的流程（acquire、release 等）
- 子类只需要实现几个简单的 protected 方法：
  - tryAcquire / tryRelease（独占）
  - tryAcquireShared / tryReleaseShared（共享）
  - isHeldExclusively

子类通过控制 state 来实现不同的同步语义。

### 6. 为什么叫"抽象队列同步器"

- **抽象**：抽象类，需要子类继承实现
- **队列**：内部用队列管理等待线程
- **同步器**：实现同步功能

**答案解析**:

AQS 是 JUC 的基础，也是面试高频难点。

AQS 的核心：state 变量 + CLH 队列 + CAS。

state 表示同步状态，用 volatile + CAS 保证原子性和可见性。
CLH 队列存放等待的线程，是一个双向链表。

获取锁的流程：尝试获取 → 失败 → 入队 → 挂起
释放锁的流程：释放 → 唤醒后继

AQS 支持独占和共享两种模式。独占模式同一时间只能一个线程持有，共享模式可以多个线程持有。

很多 JUC 工具类都是基于 AQS 的，理解了 AQS，就能理解很多并发工具的原理。

**扩展问题**:
- 什么是 AQS？
- AQS 的原理是什么？
- AQS 有哪两种模式？
- AQS 中的 state 是什么？
- 哪些工具类是基于 AQS 的？

---

## Q12: CountDownLatch 和 CyclicBarrier 的区别

**考察点**: 两种同步工具的区别、原理、使用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. CountDownLatch（倒计时门闩）

**作用**：一个线程等待多个线程完成后，再继续执行。

**原理**：
- 有一个计数器，初始值为 N
- 每个线程完成后调用 countDown()，计数器减 1
- 等待的线程调用 await()，当计数器变为 0 时，await 返回

```java
CountDownLatch latch = new CountDownLatch(3);

// 3个工作线程
for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        // 做事情
        latch.countDown(); // 完成后减1
    }).start();
}

// 主线程等待
latch.await(); // 计数器变为0时返回
System.out.println("所有任务完成");
```

**特点**：
- 一次性的，计数器到 0 就不能再用了
- 一个线程等多个线程
- 基于 AQS 共享模式

### 2. CyclicBarrier（循环栅栏）

**作用**：一组线程互相等待，所有线程都到达栅栏位置后，再一起继续执行。

**原理**：
- 有一个计数器，初始值为 N（参与的线程数）
- 每个线程到达后调用 await()，计数器减 1，然后等待
- 当计数器变为 0 时，所有等待的线程被唤醒，一起继续执行
- 可以重复使用（计数器会重置）

```java
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    System.out.println("所有人都到了，出发！"); // 最后一个到达的线程执行
});

// 3个线程
for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        // 第一阶段
        barrier.await(); // 等待其他人
        
        // 第二阶段
        barrier.await(); // 可以重复使用
    }).start();
}
```

**特点**：
- 可以循环使用（计数器会重置）
- 多个线程互相等待
- 基于 ReentrantLock + Condition
- 可以设置一个栅栏动作（barrierAction），最后一个到达的线程执行

### 3. 对比总结

| 特性 | CountDownLatch | CyclicBarrier |
|------|---------------|---------------|
| 作用 | 一个线程等多个线程 | 多个线程互相等待 |
| 可重用 | 一次性，不能重置 | 可循环使用 |
| 计数器 | 只能减 | 可以重置 |
| 实现 | AQS共享模式 | ReentrantLock + Condition |
| 等待方 | 主线程等工作线程 | 工作线程之间互等 |
| 特殊功能 | - | 可设置barrierAction |
| 异常 | - | 可以感知中断，有broken状态 |

### 4. 适用场景

**CountDownLatch**：
- 主线程等待多个子任务完成后再继续
- 比如：并发启动多个线程加载数据，都加载完后再处理

**CyclicBarrier**：
- 多个线程需要等待彼此到达某个点后再一起继续
- 比如：多线程计算，所有线程计算完第一阶段后，再一起进行第二阶段
- 可以重复使用的场景

### 5. 一句话总结

- **CountDownLatch**：我等你们所有人做完，我再做
- **CyclicBarrier**：我们大家都到齐了，再一起做下一件事

**答案解析**:

CountDownLatch 和 CyclicBarrier 都是 JUC 中的同步工具类，经常被放在一起比较。

核心区别：
1. CountDownLatch 是一个等多个，CyclicBarrier 是多个互相等
2. CountDownLatch 是一次性的，CyclicBarrier 可以重复使用

CountDownLatch 基于 AQS 的共享模式，state 表示剩余计数。
CyclicBarrier 基于 ReentrantLock + Condition，内部有一个计数器和一个 generation（代）的概念。

实际使用中，根据场景选择：
- 主线程等子任务：CountDownLatch
- 多线程互相等，还要复用：CyclicBarrier

**扩展问题**:
- CountDownLatch 和 CyclicBarrier 的区别？
- CountDownLatch 的原理？
- CyclicBarrier 的原理？
- CountDownLatch 可以重复使用吗？
- 各自的使用场景？

---

## Q13: 什么是乐观锁和悲观锁

**考察点**: 乐观锁和悲观锁的概念、实现方式、适用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 基本概念

**悲观锁**：
- 认为并发冲突一定会发生
- 每次操作前都先加锁
- 别人要操作就阻塞等待
- 悲观、保守

**乐观锁**：
- 认为并发冲突很少发生
- 操作时不加锁，直接修改
- 提交时检查有没有冲突
- 有冲突就重试，没有就成功
- 乐观、积极

### 2. 实现方式

#### 悲观锁的实现

**synchronized**：
```java
synchronized (obj) {
    // 操作共享资源
}
```

**ReentrantLock**：
```java
lock.lock();
try {
    // 操作共享资源
} finally {
    lock.unlock();
}
```

**数据库行锁**：
```sql
SELECT * FROM table WHERE id = 1 FOR UPDATE;
```

#### 乐观锁的实现

**CAS（Compare And Swap）**：
```java
AtomicInteger atomicInt = new AtomicInteger(0);
atomicInt.incrementAndGet(); // 底层CAS
```

**版本号机制**：
```sql
-- 先查版本号
SELECT version FROM table WHERE id = 1;

-- 更新时带版本号
UPDATE table SET value = ?, version = version + 1 
WHERE id = 1 AND version = ?;
```

如果影响行数为 0，说明版本号变了，有冲突，重试。

### 3. 对比总结

| 特性 | 悲观锁 | 乐观锁 |
|------|--------|--------|
| 思想 | 认为一定会冲突 | 认为很少冲突 |
| 加锁 | 是 | 否 |
| 阻塞 | 会 | 不会 |
| 冲突处理 | 等待 | 重试 |
| 适用场景 | 写多，冲突多 | 读多，冲突少 |
| 性能 | 冲突多的时候好 | 冲突少的时候好 |
| 代表 | synchronized、Lock | CAS、版本号 |

### 4. 优缺点

**悲观锁**：
- 优点：简单，冲突多的时候性能稳定
- 缺点：加锁开销大，有死锁风险，并发度不高

**乐观锁**：
- 优点：不加锁，并发度高，没有死锁
- 缺点：冲突多的时候不断重试，性能差；只能保证单个变量的原子操作；有ABA问题

### 5. 适用场景

**悲观锁**：
- 写操作多，冲突概率高
- 竞争激烈的场景
- 需要保证强一致性

**乐观锁**：
- 读操作多，冲突概率低
- 竞争不激烈的场景
- 追求高并发、高吞吐量

**答案解析**:

乐观锁和悲观锁是两种不同的并发控制思想，也是面试常考题。

悲观锁就是先加锁再操作，synchronized 和 Lock 都是悲观锁。
乐观锁就是操作时不加锁，提交时检查冲突，CAS 和版本号是乐观锁的实现。

不能说哪个一定好，要看场景：
- 冲突多，写多读少：悲观锁更好
- 冲突少，读多写少：乐观锁更好

CAS 是乐观锁的经典实现，Atomic 系列原子类就是用 CAS 实现的。

数据库中也有乐观锁和悲观锁：for update 是悲观锁，版本号是乐观锁。

**扩展问题**:
- 什么是乐观锁？什么是悲观锁？
- 乐观锁和悲观锁的区别？
- 乐观锁有哪些实现方式？
- CAS 是乐观锁还是悲观锁？
- 各自的适用场景？

---

## Q14: Java内存模型（JMM）

**考察点**: JMM的概念、主内存与工作内存、内存交互操作

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 JMM

**JMM（Java Memory Model，Java 内存模型）**：

JMM 是一种规范，定义了 Java 程序中各种变量（线程共享变量）的访问规则，以及在 JVM 中将变量存储到内存和从内存中读取变量的底层细节。

JMM 的目的是**屏蔽各种硬件和操作系统的内存访问差异，以实现让 Java 程序在各种平台下都能达到一致的内存访问效果**。

### 2. 主内存与工作内存

JMM 规定：
- 所有变量都存储在**主内存**（Main Memory）中
- 每个线程有自己的**工作内存**（Working Memory）
- 线程对变量的所有操作都必须在工作内存中进行，不能直接读写主内存
- 不同线程之间也无法直接访问对方工作内存中的变量
- 线程间变量值的传递需要通过主内存来完成

```
线程1 → 工作内存1 → 主内存 ← 工作内存2 ← 线程2
```

工作内存是 JMM 的一个抽象概念，并不真实存在。它涵盖了缓存、写缓冲区、寄存器以及其他的硬件和编译器优化。

### 3. 内存交互操作

JMM 定义了 8 种原子操作来完成主内存和工作内存的交互：

1. **lock（锁定）**：作用于主内存变量，把变量标记为一条线程独占
2. **unlock（解锁）**：作用于主内存变量，释放锁定的变量
3. **read（读取）**：作用于主内存变量，把变量值从主内存传输到工作内存
4. **load（载入）**：作用于工作内存变量，把 read 来的值放入工作内存的变量副本
5. **use（使用）**：作用于工作内存变量，把变量值传递给执行引擎
6. **assign（赋值）**：作用于工作内存变量，把从执行引擎收到的值赋给变量
7. **store（存储）**：作用于工作内存变量，把变量值传送到主内存
8. **write（写入）**：作用于主内存变量，把 store 来的值放入主内存的变量中

执行顺序：
- 读取：read → load → use
- 写入：assign → store → write

### 4. JMM 的三大特性

JMM 围绕原子性、可见性、有序性建立。

**（1）原子性（Atomicity）**
- JMM 保证了 read、load、use、assign、store、write 这些基本操作的原子性
- 更大范围的原子性需要 synchronized 或 Lock
- 原子操作：synchronized、Lock、Atomic 原子类

**（2）可见性（Visibility）**
- 一个线程修改了共享变量，其他线程能立即看到
- volatile 保证可见性
- synchronized 保证可见性（解锁前刷回主内存）
- final 也有可见性（final 字段初始化后其他线程可见）

**（3）有序性（Ordering）**
- 禁止指令重排序
- volatile 保证有序性（内存屏障）
- synchronized 保证有序性（锁的语义）
- happens-before 原则保证有序性

### 5. 指令重排序

为了提高性能，编译器和处理器可能会对指令进行重排序。

**重排序的类型**：
1. 编译器优化的重排序
2. 指令级并行的重排序
3. 内存系统的重排序

单线程下，重排序不会影响结果（as-if-serial 语义）。
多线程下，重排序可能导致可见性和有序性问题。

**答案解析**:

JMM 是 Java 并发的基础理论，理解 JMM 有助于理解各种并发问题。

JMM 的核心是主内存和工作内存的抽象。所有变量都在主内存，每个线程有自己的工作内存，操作都在工作内存中进行，通过主内存同步。

JMM 定义了 8 种内存交互操作，了解一下就行，不用全背。

更重要的是 JMM 的三大特性：原子性、可见性、有序性。各种并发工具都是为了保证这三个特性。

volatile 保证可见性和有序性，synchronized 保证三个特性。

**扩展问题**:
- 什么是 JMM？
- 主内存和工作内存的区别？
- JMM 的三大特性？
- 什么是指令重排序？
- volatile 在 JMM 中如何保证可见性？

---

## Q15: 什么是 happens-before 原则

**考察点**: happens-before的概念、8条规则

**难度**: 困难

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 什么是 happens-before

**happens-before 原则**是 JMM 中定义的两项操作之间的偏序关系。

如果操作 A happens-before 操作 B，那么 A 操作的结果对 B 操作是可见的。

注意：happens-before 不是说 A 一定在 B 之前执行，而是说 A 的结果对 B 可见。如果 A 的结果对 B 没有影响，重排序是允许的。

### 2. 8 条基本规则

#### （1）程序次序规则（Program Order Rule）
在一个线程内，按照代码顺序，书写在前面的操作 happens-before 书写在后面的操作。

注意：是在单线程内。

#### （2）管程锁定规则（Monitor Lock Rule）
对一个锁的 unlock 操作 happens-before 于后面对这个锁的 lock 操作。

即：前一个线程解锁了，后一个线程加锁时，能看到前一个线程的修改。

#### （3）volatile 变量规则（Volatile Variable Rule）
对一个 volatile 变量的写操作 happens-before 于后面对这个变量的读操作。

即：写了 volatile 变量后，其他线程读这个变量时，能看到最新值。

#### （4）线程启动规则（Thread Start Rule）
Thread 对象的 start() 方法 happens-before 此线程的每一个动作。

即：主线程启动子线程前的修改，子线程能看到。

#### （5）线程终止规则（Thread Termination Rule）
线程中的所有操作都 happens-before 于对此线程的终止检测。

即：子线程执行完了，主线程 join() 返回后，能看到子线程的所有修改。

#### （6）线程中断规则（Thread Interruption Rule）
对线程 interrupt() 方法的调用 happens-before 于被中断线程的代码检测到中断事件的发生。

#### （7）对象终结规则（Finalizer Rule）
一个对象的初始化完成（构造函数执行结束）happens-before 于它的 finalize() 方法的开始。

#### （8）传递性（Transitivity）
如果 A happens-before B，B happens-before C，那么 A happens-before C。

### 3. 为什么需要 happens-before

JMM 是一个弱内存模型，它不保证所有操作都是有序可见的。

如果没有 happens-before 原则，我们就无法确定两个操作之间的顺序和可见性，写并发程序就无从下手。

有了 happens-before 原则，我们就可以通过这些规则来判断：在什么情况下，一个线程的修改对另一个线程是可见的。

### 4. 举例

```java
int a = 0;
volatile boolean flag = false;

// 线程1
a = 1;        // 操作A
flag = true;  // 操作B

// 线程2
if (flag) {   // 操作C
    System.out.println(a); // 操作D
}
```

分析：
- 程序次序规则：A happens-before B，C happens-before D
- volatile 规则：B happens-before C
- 传递性：A happens-before D

所以线程 2 看到 flag 为 true 时，a 一定是 1。

这就是 volatile 的内存语义的体现。

**答案解析**:

happens-before 原则是 JMM 中的重要概念，也是面试难点。

简单说：如果 A happens-before B，那么 A 的结果对 B 可见。

8 条规则中，最常考的是：
1. 程序次序规则（单线程内前面的 happens-before 后面的）
2. 管程锁定规则（unlock happens-before lock）
3. volatile 变量规则（写 happens-before 读）
4. 传递性

理解了 happens-before，就能更好地理解 volatile、synchronized 等的内存语义。

happens-before 不是时间上的先后，而是结果可见性。A happens-before B 不代表 A 一定在 B 之前执行，而是说 A 的结果对 B 可见。

**扩展问题**:
- 什么是 happens-before 原则？
- 有哪些 happens-before 规则？
- volatile 变量规则是什么？
- 管程锁定规则是什么？
- happens-before 和时间上的先后有什么区别？

---

## Q16: 并发集合（ConcurrentHashMap/CopyOnWriteArrayList）

**考察点**: 并发集合的实现原理、适用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. ConcurrentHashMap

**作用**：线程安全的 HashMap，高性能。

**JDK7 实现**：分段锁（Segment）
- 把 HashMap 分成 16 个 Segment
- 每个 Segment 有自己的锁
- 不同 Segment 之间可以并发操作
- 同一个 Segment 内还是串行

**JDK8 实现**：CAS + synchronized
- 结构和 HashMap 一样：数组 + 链表 + 红黑树
- 没有元素时用 CAS 插入
- 有元素时用 synchronized 锁住头节点
- 锁的粒度是桶级别，比分段锁更细

**特点**：
- 线程安全
- 高并发、高性能
- key 和 value 都不能为 null
- 弱一致性迭代器（fail-safe）
- size 计算用 CounterCell 分散计数

**适用场景**：多线程环境下的 Map。

### 2. CopyOnWriteArrayList

**作用**：线程安全的 ArrayList，读多写少场景。

**原理**：写时复制（Copy-On-Write）。
- 读操作：完全无锁，直接读取数组
- 写操作：复制一份新数组，在新数组上修改，修改完后把引用指向新数组
- 写操作加锁（ReentrantLock），防止并发写

```java
public boolean add(E e) {
    final ReentrantLock lock = this.lock;
    lock.lock();
    try {
        Object[] elements = getArray();
        int len = elements.length;
        Object[] newElements = Arrays.copyOf(elements, len + 1); // 复制
        newElements[len] = e;
        setArray(newElements); // 替换引用
        return true;
    } finally {
        lock.unlock();
    }
}
```

**特点**：
- 读操作无锁，性能极高
- 写操作需要复制数组，性能差
- 内存占用大（写时复制）
- 弱一致性（读到的可能是旧数据）
- 迭代安全，不会抛 ConcurrentModificationException

**适用场景**：
- 读多写少
- 读性能要求高
- 对数据实时性要求不高
- 比如：配置信息、白名单、黑名单

### 3. 其他并发集合

**CopyOnWriteArraySet**：
- 基于 CopyOnWriteArrayList 实现
- 线程安全的 Set
- 同样读多写少场景

**ConcurrentSkipListMap**：
- 线程安全的有序 Map
- 基于跳表实现
- 替代 TreeMap 的并发版本

**ConcurrentSkipListSet**：
- 线程安全的有序 Set
- 基于 ConcurrentSkipListMap

**BlockingQueue**：
- 阻塞队列
- 生产者消费者模式常用
- 实现类：ArrayBlockingQueue、LinkedBlockingQueue、SynchronousQueue 等

**ConcurrentLinkedQueue**：
- 非阻塞的并发队列
- 基于 CAS
- 高并发性能好

### 4. 并发集合总结

| 集合 | 普通版本 | 并发版本 | 特点 |
|------|---------|---------|------|
| Map | HashMap | ConcurrentHashMap | CAS + synchronized，高并发 |
| List | ArrayList | CopyOnWriteArrayList | 写时复制，读多写少 |
| Set | HashSet | CopyOnWriteArraySet | 基于COWArrayList |
| 有序Map | TreeMap | ConcurrentSkipListMap | 跳表实现 |
| 有序Set | TreeSet | ConcurrentSkipListSet | 基于SkipListMap |
| 队列 | - | ArrayBlockingQueue | 有界阻塞队列 |
| 队列 | - | LinkedBlockingQueue | 无界阻塞队列 |

**答案解析**:

并发集合是 JUC 的重要组成部分，也是面试常考点。

最常考的两个：ConcurrentHashMap 和 CopyOnWriteArrayList。

ConcurrentHashMap 是并发版的 HashMap，JDK8 用 CAS + synchronized 实现，性能很好。

CopyOnWriteArrayList 是并发版的 ArrayList，用写时复制实现。读无锁，写复制，适合读多写少。

CopyOnWrite 的核心思想：读写分离，读不加锁，写加锁并复制。优点是读性能高，缺点是内存占用大，数据弱一致性。

实际开发中，根据场景选择合适的并发集合。

**扩展问题**:
- ConcurrentHashMap 的实现原理？
- CopyOnWriteArrayList 的原理？
- CopyOnWriteArrayList 的优缺点？
- 有哪些线程安全的集合？
- 并发集合和同步集合（Collections.synchronizedXxx）的区别？

---

## Q17: 原子类（AtomicInteger）的实现原理

**考察点**: 原子类的原理、CAS、应用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 什么是原子类

原子类是 JUC 提供的一组原子操作类，可以保证对单个变量的操作是原子性的。

**分类**：

**基本类型**：
- AtomicInteger
- AtomicLong
- AtomicBoolean

**引用类型**：
- AtomicReference
- AtomicStampedReference（带版本号，解决ABA）
- AtomicMarkableReference（带标记位）

**数组类型**：
- AtomicIntegerArray
- AtomicLongArray
- AtomicReferenceArray

**对象属性更新器**：
- AtomicIntegerFieldUpdater
- AtomicLongFieldUpdater
- AtomicReferenceFieldUpdater

**累加器（JDK8新增）**：
- LongAdder
- DoubleAdder
- LongAccumulator
- DoubleAccumulator

### 2. AtomicInteger 的原理

AtomicInteger 基于 **CAS + 自旋**实现。

**核心代码**（简化版）：
```java
public class AtomicInteger extends Number implements java.io.Serializable {
    private volatile int value; // volatile保证可见性
    
    // 自增并返回新值
    public final int incrementAndGet() {
        return unsafe.getAndAddInt(this, valueOffset, 1) + 1;
    }
    
    // Unsafe中的方法
    public final int getAndAddInt(Object o, long offset, int delta) {
        int v;
        do {
            v = getIntVolatile(o, offset); // 读取当前值
        } while (!compareAndSwapInt(o, offset, v, v + delta)); // CAS尝试更新
        return v;
    }
}
```

**流程**：
1. 读取变量的当前值
2. 用 CAS 尝试更新
3. 如果成功，返回
4. 如果失败（被其他线程改了），重新读取当前值，再 CAS
5. 循环直到成功（自旋）

### 3. 为什么能保证原子性

- CAS 是 CPU 级别的原子指令，由硬件保证原子性
- volatile 保证变量的可见性
- 自旋保证最终一定能成功（无锁的情况下）

### 4. ABA 问题

CAS 有 ABA 问题，AtomicInteger 也有。

如果业务场景对 ABA 敏感，可以用 **AtomicStampedReference**，它不仅比较引用，还比较版本号。

```java
AtomicStampedReference<Integer> ref = new AtomicStampedReference<>(1, 0);
ref.compareAndSet(1, 2, 0, 1); // 预期引用、新引用、预期版本、新版本
```

### 5. LongAdder（JDK8 新增）

AtomicLong 在高并发下性能不好，因为所有线程都竞争同一个变量，CAS 失败率高。

**LongAdder** 解决了这个问题：
- 把一个变量拆成多个 Cell
- 不同线程更新不同的 Cell，减少竞争
- 最终求和时把所有 Cell 加起来
- 空间换时间

LongAdder 适合高并发下的统计计数场景，性能比 AtomicLong 好很多。

但 LongAdder 不是精确的，在并发更新时 sum() 可能不是最新值。

### 6. 原子类的使用场景

- 计数器
- 序列号生成
- 并发统计
- 简单的无锁算法

**答案解析**:

原子类是 JUC 中比较基础的工具，也是面试常考题。

AtomicInteger 的原理：CAS + 自旋 + volatile。
- volatile 保证可见性
- CAS 保证原子性
- 自旋保证最终成功

原子类是乐观锁的实现，竞争不激烈时性能很好。但竞争激烈时，CAS 不断重试，性能下降。

高并发计数场景，推荐用 LongAdder，它通过分散计数减少竞争，性能更好。

ABA 问题也是常考点，如果对 ABA 敏感，用 AtomicStampedReference。

**扩展问题**:
- AtomicInteger 的原理？
- 原子类有哪些分类？
- CAS 的 ABA 问题如何解决？
- LongAdder 和 AtomicLong 的区别？
- 原子类和 synchronized 的性能对比？

---

## Q18: 线程的生命周期和状态转换

**考察点**: 线程的6种状态、转换关系

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 线程的 6 种状态

Java 线程有 6 种状态，定义在 Thread.State 枚举中：

#### （1）NEW（新建）
- 线程对象已经创建，但还没有调用 start() 方法
- 还没开始执行

#### （2）RUNNABLE（可运行/运行）
- 线程已经调用了 start() 方法
- 包括两种子状态：
  - **Ready（就绪）**：等待 CPU 调度
  - **Running（运行中）**：正在执行
- Java 没有区分这两种状态，统一叫 RUNNABLE

#### （3）BLOCKED（阻塞）
- 线程在等待获取锁（synchronized 或 Lock）
- 被阻塞在同步块或同步方法外

#### （4）WAITING（等待）
- 线程在等待另一个线程的特定操作
- 进入等待状态的方法：
  - Object.wait() （无超时）
  - Thread.join() （无超时）
  - LockSupport.park()
- 没有时间限制，直到被唤醒

#### （5）TIMED_WAITING（计时等待）
- 线程在等待，但有时间限制
- 进入计时等待的方法：
  - Thread.sleep()
  - Object.wait(long)
  - Thread.join(long)
  - LockSupport.parkNanos()
  - LockSupport.parkUntil()
- 时间到了自动唤醒

#### （6）TERMINATED（终止）
- 线程执行完毕
- 或者因为异常退出了 run() 方法
- 线程结束，不能再 start

### 2. 状态转换图

```
        start()                获取到锁
NEW ──────────→ RUNNABLE ←───────────── BLOCKED
                 ↓  ↑                  wait()
                 ↓  ↑ notify/notifyAll
                 ↓  ↑
                 ↓  ↑ 时间到/唤醒
              WAITING
                 ↑
                 | sleep/wait(timeout)/join(timeout)
                 |
           TIMED_WAITING
          
RUNNABLE 执行完 → TERMINATED
```

### 3. 几个方法的区别

**wait() 和 sleep()**：
- wait 是 Object 的方法，sleep 是 Thread 的方法
- wait 释放锁，sleep 不释放锁
- wait 需要在同步块中调用，sleep 不需要

**wait() 和 await()**：
- wait 是 Object 的，用在 synchronized 中
- await 是 Condition 的，用在 Lock 中

**sleep() 和 yield()**：
- sleep 让线程暂停指定时间，进入 TIMED_WAITING
- yield 让线程让出 CPU，但还是 RUNNABLE 状态，可能马上又被调度
- sleep 一定会进入等待，yield 只是让出一下

**join()**：
- 等待另一个线程执行完成
- 底层是 wait 实现的

### 4. 注意事项

- 一个线程只能调用一次 start()，多次调用会抛 IllegalThreadStateException
- 线程结束后不能重新启动
- BLOCKED 和 WAITING 的区别：
  - BLOCKED：等锁
  - WAITING：等通知/等其他线程完成

**答案解析**:

线程的生命周期是基础面试题，必须掌握 6 种状态和它们之间的转换。

6 种状态：NEW、RUNNABLE、BLOCKED、WAITING、TIMED_WAITING、TERMINATED。

RUNNABLE 包括就绪和运行两种状态，Java 没有细分。

BLOCKED 是等待锁，WAITING 是无期限等待，TIMED_WAITING 是有时间的等待。

状态转换的触发方法要记住：
- start()：NEW → RUNNABLE
- wait()：RUNNABLE → WAITING
- notify()：WAITING → BLOCKED/RUNNABLE
- sleep()：RUNNABLE → TIMED_WAITING
- 抢锁失败：RUNNABLE → BLOCKED
- 抢到锁：BLOCKED → RUNNABLE
- 执行完：RUNNABLE → TERMINATED

**扩展问题**:
- 线程有哪几种状态？
- RUNNABLE 和 Running 的区别？
- BLOCKED 和 WAITING 的区别？
- WAITING 和 TIMED_WAITING 的区别？
- start() 和 run() 的区别？

---

## Q19: 什么是守护线程

**考察点**: 守护线程的概念、作用、和用户线程的区别

**难度**: 简单

**频率**: ⭐⭐⭐

**标准答案**:

### 1. 什么是守护线程

Java 线程分为两种：
- **用户线程（User Thread）**：普通线程，默认创建的都是用户线程
- **守护线程（Daemon Thread）**：后台服务线程，为其他线程提供服务

守护线程的特点：
- JVM 中如果所有用户线程都结束了，守护线程会被自动终止，JVM 退出
- 不管守护线程有没有执行完
- 守护线程是"后台"的，JVM 不关心它有没有做完

### 2. 设置守护线程

```java
Thread thread = new Thread(() -> {
    // 守护线程的任务
});
thread.setDaemon(true); // 设置为守护线程，必须在start()之前调用
thread.start();
```

注意：
- `setDaemon(true)` 必须在 `start()` 之前调用，否则抛 IllegalThreadStateException
- 线程默认继承创建它的线程的守护状态（主线程是用户线程，所以默认创建的都是用户线程）
- 可以用 `isDaemon()` 方法判断是不是守护线程

### 3. 守护线程的用途

守护线程用于后台支持任务：
- **GC 垃圾回收线程**：JVM 的 GC 线程就是守护线程
- **后台监控线程**：监控内存、线程状态等
- **心跳检测**：定时发送心跳
- **定时任务线程**：如果用户线程都结束了，定时任务也没必要继续了

### 4. 注意事项

（1）**守护线程中 finally 不一定执行**
因为 JVM 退出时，守护线程会被直接终止，不会等待它执行完，finally 可能没机会执行。

```java
Thread t = new Thread(() -> {
    try {
        // 做事情
    } finally {
        // 守护线程被终止时，这里可能不会执行
    }
});
t.setDaemon(true);
```

（2）**不要在守护线程中做重要的业务逻辑**
因为它随时可能被终止。

（3）**main 线程是用户线程**
主线程默认是用户线程。

### 5. 用户线程和守护线程的区别

| 特性 | 用户线程 | 守护线程 |
|------|---------|---------|
| 作用 | 业务逻辑 | 后台服务 |
| JVM退出 | 所有用户线程结束，JVM才退出 | 不影响JVM退出 |
| 默认 | 默认创建的是用户线程 | 需要手动设置 |
| finally | 会执行完 | 可能不执行 |
| 重要性 | 高 | 低 |

**答案解析**:

守护线程是一个比较简单的知识点，但也会被问到。

核心点：守护线程是后台线程，为其他线程服务。所有用户线程结束后，JVM 就退出，守护线程会被自动终止。

最典型的守护线程是 GC 线程。

注意点：
1. setDaemon 必须在 start 之前调用
2. 守护线程的 finally 不一定执行
3. 不要在守护线程中做重要的业务

**扩展问题**:
- 什么是守护线程？
- 守护线程和用户线程的区别？
- 如何设置守护线程？
- 守护线程有什么用？
- 守护线程的 finally 一定会执行吗？

---

## Q20: 如何优雅地停止线程

**考察点**: 停止线程的正确方式、interrupt机制

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 不正确的方式

#### （1）stop() 方法（已废弃）

`Thread.stop()` 方法已经被废弃了，因为它不安全。

- stop 会直接终止线程，释放所有锁
- 可能导致对象状态不一致（写到一半被终止了）
- 可能导致数据损坏

#### （2）suspend() 和 resume()（已废弃）

- suspend 挂起线程，resume 恢复
- 容易导致死锁（suspend 不释放锁）
- 已废弃

### 2. 正确的方式：interrupt 中断机制

Java 提供了**中断机制**来优雅地停止线程。

**原理**：
- 每个线程有一个中断标记位
- 其他线程调用该线程的 interrupt() 方法设置标记位
- 被中断的线程自己检查中断标记，决定如何响应
- 是一种"协作式"的停止，不是强制停止

**三个核心方法**：

1. **interrupt()**：设置中断标记为 true
   - 实例方法
   - 调用后，线程的中断状态设为 true

2. **isInterrupted()**：检查中断标记
   - 实例方法
   - 返回中断状态，不清除标记

3. **interrupted()**：检查并清除中断标记
   - 静态方法
   - 返回当前线程的中断状态，然后清除标记（设为 false）

### 3. 中断的响应方式

线程被中断后，如何响应取决于线程当前的状态。

#### （1）线程处于正常运行状态

线程需要自己检查中断标记：

```java
Thread thread = new Thread(() -> {
    while (!Thread.currentThread().isInterrupted()) {
        // 正常执行任务
    }
    System.out.println("线程被中断了，优雅退出");
});
```

线程在循环中检查中断标记，如果被中断了，就退出循环，结束线程。

#### （2）线程处于阻塞状态（sleep/wait/join）

如果线程调用了 sleep、wait、join 等方法处于阻塞状态，被中断时会：
- 抛出 InterruptedException
- 清除中断标记（设为 false）

```java
Thread thread = new Thread(() -> {
    try {
        while (!Thread.currentThread().isInterrupted()) {
            Thread.sleep(1000);
            // 做事情
        }
    } catch (InterruptedException e) {
        // 被中断了，抛出异常
        // 注意：异常抛出后中断标记被清除了
        System.out.println("线程被中断");
        // 可以选择恢复中断标记
        Thread.currentThread().interrupt();
    }
});
```

**最佳实践**：
- 捕获 InterruptedException 后，要么处理，要么重新设置中断标记
- 不要吞掉中断（catch了什么也不做）

### 4. 用 volatile 标记位

也可以用一个 volatile 变量作为停止标记：

```java
public class MyThread extends Thread {
    private volatile boolean stop = false;
    
    @Override
    public void run() {
        while (!stop) {
            // 做事情
        }
    }
    
    public void stopThread() {
        stop = true;
    }
}
```

但这种方式有个问题：如果线程处于阻塞状态（sleep/wait），就无法及时响应停止。

所以**优先使用 interrupt 机制**。

### 5. 总结

**不要用 stop、suspend、resume**，这些方法已废弃，不安全。

**推荐用 interrupt 机制**：
- 调用 interrupt() 设置中断标记
- 线程自己检查中断标记，决定如何退出
- 阻塞时会抛 InterruptedException，捕获后处理

**优雅停止的原则**：
- 给线程一个机会做完清理工作
- 不要强制终止
- 协作式停止

**答案解析**:

如何优雅地停止线程是经典面试题。

stop() 方法已废弃，因为它不安全，会导致数据不一致。

正确的方式是使用 interrupt 中断机制。这是一种协作式的停止：发起方设置中断标记，被中断方自己检查并决定如何响应。

interrupt 的三个方法要分清：
- interrupt()：设置中断标记
- isInterrupted()：检查标记，不清除
- interrupted()：检查标记，并清除

线程处于正常运行状态时，需要自己检查中断标记。
线程处于阻塞状态时（sleep/wait/join），会抛 InterruptedException 并清除标记。

捕获 InterruptedException 后，不要吞掉异常，要么处理，要么重新设置中断状态。

**扩展问题**:
- 如何优雅地停止线程？
- 为什么 stop() 方法被废弃了？
- interrupt() 方法的作用？
- isInterrupted() 和 interrupted() 的区别？
- 线程处于 sleep 状态时如何停止？

---

## Reference

1. 方腾飞、魏鹏、程晓明. *Java并发编程的艺术*. 机械工业出版社, 2015
2. 美团技术团队. *Java并发编程——从基础到进阶*. https://tech.meituan.com, 访问时间：2026-07-28
3. OpenJDK. *java.util.concurrent 包源码*. http://openjdk.java.net, 访问时间：2026-07-28
4. 牛客网. *Java并发编程面试题精选*. https://www.nowcoder.com, 访问时间：2026-07-28
5. Oracle. *Java Concurrency Tutorial*. https://docs.oracle.com/javase/tutorial/essential/concurrency/, 访问时间：2026-07-28

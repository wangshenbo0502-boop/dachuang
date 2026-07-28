---
title: "Java集合框架面试题（20题）"
category: "面试题"
type: "Java后端"
difficulty: "中等"
tags: ["Java集合", "HashMap", "ArrayList", "ConcurrentHashMap", "红黑树"]
source: ["Java集合框架源码分析", "美团技术团队博客", "牛客网Java面试题库"]
last_update: "2026-07-28"
---

# Java集合框架面试题（20题）

> 本文档涵盖Java集合框架的核心知识点，包括List、Set、Map三大体系的实现原理、源码分析、线程安全等重点内容，是Java后端面试的重中之重。

---

## Q1: ArrayList 和 LinkedList 的区别

**考察点**: 数组和链表的特性、随机访问效率、插入删除效率

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

ArrayList 和 LinkedList 都是 List 接口的实现类，但底层数据结构不同，导致特性差异很大。

### 1. 底层数据结构

**ArrayList**：
- 底层是 **Object 数组**（动态数组）
- 初始容量为 10（JDK8）
- 扩容时变为原来的 1.5 倍

```java
// JDK8 ArrayList 源码
private static final int DEFAULT_CAPACITY = 10;
transient Object[] elementData;
```

**LinkedList**：
- 底层是**双向链表**
- 每个节点包含 item、prev、next 三个属性
- 没有初始容量和扩容的概念

```java
// JDK8 LinkedList 源码
private static class Node<E> {
    E item;
    Node<E> next;
    Node<E> prev;
}
```

### 2. 性能对比

| 操作 | ArrayList | LinkedList |
|------|-----------|------------|
| 随机访问（get） | O(1)，通过数组下标直接访问 | O(n)，需要遍历链表 |
| 头部插入（addFirst） | O(n)，需要移动元素 | O(1)，直接修改指针 |
| 尾部插入（addLast） | O(1)，尾部直接加（不扩容时） | O(1)，直接修改指针 |
| 中间插入（add(index)） | O(n)，需要移动元素 | O(n)，需要先定位（然后O(1)插入） |
| 删除（remove） | O(n)，需要移动元素 | O(n)，需要先定位 |
| 内存占用 | 少，只存数据 | 多，每个节点需要存prev和next |

### 3. 线程安全

两者都是**线程不安全**的。

### 4. 适用场景

**ArrayList**：
- 频繁随机访问元素
- 尾部插入和删除较多
- 内存空间相对紧张

**LinkedList**：
- 频繁在头部或中间插入删除
- 需要实现栈、队列等数据结构

**答案解析**:

这道题的核心是理解数组和链表两种数据结构的特性差异。

数组的特点是内存连续，支持随机访问（O(1)），但插入删除需要移动元素（O(n)）。链表的特点是内存不连续，插入删除只需要修改指针（O(1)，如果已经定位到节点），但随机访问需要遍历（O(n)）。

需要注意的是，LinkedList 的中间插入虽然插入操作本身是 O(1)，但定位到指定位置需要 O(n) 的时间，所以整体还是 O(n)。而且实际测试中，ArrayList 的中间插入在很多场景下比 LinkedList 还要快，因为数组的移动是整块内存操作，效率很高，而链表的遍历很慢。

**扩展问题**:
- ArrayList 的扩容机制是什么？
- ArrayList 为什么用 transient 修饰 elementData？
- LinkedList 可以作为队列使用吗？有哪些方法？
- 实际开发中 ArrayList 和 LinkedList 怎么选择？
- 为什么说 ArrayList 中间插入可能比 LinkedList 快？

---

## Q2: HashMap 的底层原理和实现

**考察点**: HashMap的数据结构、put/get流程、哈希冲突解决

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 数据结构（JDK8）

HashMap 底层是**数组 + 链表 + 红黑树**。

- **数组（Node[] table）**：也叫哈希桶数组，是 HashMap 的主体
- **链表**：解决哈希冲突，相同哈希值的元素以链表形式存储
- **红黑树**：当链表长度超过阈值（8）且数组长度大于64时，链表转为红黑树，提高查找效率

```java
// JDK8 HashMap 核心结构
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    V value;
    Node<K,V> next;
}

transient Node<K,V>[] table; // 哈希桶数组
```

### 2. 存储原理

**计算桶位置**：
```java
// 1. 计算key的hash值
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}

// 2. 计算数组下标（等价于 hash % table.length）
int index = (table.length - 1) & hash;
```

为什么用 `&` 而不是 `%`？因为位运算比取模运算效率高，而且只有当数组长度是 2 的幂时，`(n-1) & hash` 才等价于 `hash % n`。

### 3. put 方法流程

1. 计算 key 的 hash 值，确定桶位置
2. 如果数组为空，先扩容（初始容量16）
3. 如果该桶位置没有元素，直接创建新节点放入
4. 如果有元素：
   - key 相同（hash相同且equals为true），覆盖旧值
   - 节点是红黑树节点，按红黑树方式插入
   - 节点是链表节点，遍历链表尾插法插入
5. 插入后，如果链表长度 > 8 且数组长度 < 64，先扩容
6. 插入后，如果链表长度 > 8 且数组长度 >= 64，链表转红黑树
7. size 增加，如果超过阈值（容量 * 加载因子），触发扩容

### 4. get 方法流程

1. 计算 key 的 hash 值，确定桶位置
2. 桶位置为空，返回 null
3. 桶位置第一个元素就是目标，直接返回
4. 如果是红黑树，按红黑树方式查找
5. 如果是链表，遍历链表查找

### 5. 重要参数

- **初始容量**：16（必须是2的幂）
- **加载因子**：0.75
- **树化阈值**：8
- **树退化阈值**：6
- **最小树化容量**：64

**答案解析**:

HashMap 是面试最高频的考点，必须深入理解。

JDK8 对 HashMap 做了重大改进：引入红黑树，当链表过长时转为红黑树，将查找时间复杂度从 O(n) 降到 O(logn)。

哈希值的计算用了扰动函数：`h ^ (h >>> 16)`，目的是让高位也参与到下标计算中，减少哈希冲突。因为数组长度一般比较小，只有低位参与计算，高位不参与的话容易导致哈希冲突。

HashMap 的容量必须是 2 的幂，这是为了用位运算代替取模运算，提高效率。

**扩展问题**:
- HashMap 为什么用红黑树而不是 AVL 树？
- HashMap 的 hash 函数为什么要右移16位？
- HashMap 为什么容量必须是2的幂？
- HashMap 为什么加载因子是0.75？
- JDK7 和 JDK8 的 HashMap 有什么区别？

---

## Q3: HashMap 和 HashTable 的区别

**考察点**: 线程安全、null键值、性能、继承关系

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 核心区别对比

| 特性 | HashMap | HashTable |
|------|---------|-----------|
| 线程安全 | 不安全 | 安全（synchronized） |
| 效率 | 高 | 低 |
| null键 | 允许一个null键 | 不允许null键 |
| null值 | 允许多个null值 | 不允许null值 |
| 初始容量 | 16 | 11 |
| 扩容方式 | 变为2倍 | 变为2倍+1 |
| 父类 | AbstractMap | Dictionary（已废弃） |
| 迭代方式 | Iterator（fail-fast） | Enumeration + Iterator |

### 2. 线程安全

- **HashMap**：线程不安全，多线程环境下可能出现问题（如JDK7的死循环、JDK8的数据覆盖）
- **HashTable**：几乎所有方法都加了 `synchronized`，线程安全，但性能差

```java
// HashTable 源码，方法都加了 synchronized
public synchronized V put(K key, V value) { ... }
public synchronized V get(Object key) { ... }
public synchronized int size() { ... }
```

### 3. null 键和 null 值

```java
// HashMap 允许 null 键和 null 值
HashMap<String, String> map = new HashMap<>();
map.put(null, "a"); // 可以
map.put("b", null); // 可以

// HashTable 不允许
Hashtable<String, String> table = new Hashtable<>();
// table.put(null, "a"); // 抛 NullPointerException
// table.put("b", null); // 抛 NullPointerException
```

HashMap 的 null 键存在下标为 0 的桶中。

### 4. 推荐使用

- 单线程环境：用 **HashMap**
- 多线程环境：用 **ConcurrentHashMap**（不用 HashTable，效率太低）

**答案解析**:

HashMap 和 HashTable 的区别是经典面试题。HashTable 是一个遗留类，已经不推荐使用了，多线程环境推荐使用 ConcurrentHashMap。

HashTable 效率低的原因是它锁住了整个哈希表，所有操作都要竞争同一把锁。而 ConcurrentHashMap 使用了分段锁（JDK7）或 CAS + synchronized（JDK8），并发性能更好。

HashMap 允许 null 键和 null 值，而 HashTable 不允许，这是设计上的差异。HashMap 的 null 键会被放在下标为 0 的位置（因为 null 的 hash 值是 0）。

**扩展问题**:
- HashTable 为什么不允许 null 键和 null 值？
- ConcurrentHashMap 和 HashTable 的区别？
- 多线程环境下如何实现线程安全的 Map？
- HashMap 在多线程下会有什么问题？
- HashTable 的扩容为什么是 2 倍 + 1？

---

## Q4: ConcurrentHashMap 的实现原理

**考察点**: JDK7分段锁、JDK8的CAS+synchronized、size计算

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. JDK7 的实现：分段锁

JDK7 中 ConcurrentHashMap 底层是 **Segment 数组 + HashEntry 数组 + 链表**。

- **Segment**：继承自 ReentrantLock，每个 Segment 是一个独立的哈希表，有自己的锁
- 默认有 **16 个 Segment**，理论上最多支持 16 个线程并发写
- 不同 Segment 之间的操作不会互相干扰

```
ConcurrentHashMap
├── Segment[0]
│   └── HashEntry[] + 链表
├── Segment[1]
│   └── HashEntry[] + 链表
├── ...
└── Segment[15]
    └── HashEntry[] + 链表
```

**put 流程**：
1. 计算 key 的 hash 值，确定 Segment 位置
2. 获取该 Segment 的锁（ReentrantLock）
3. 在对应的 HashEntry 数组中插入元素
4. 释放锁

**缺点**：
- 分段数固定（默认16），不够灵活
- 同一个 Segment 内还是只能有一个线程写

### 2. JDK8 的实现：CAS + synchronized

JDK8 对 ConcurrentHashMap 做了重大改造，底层结构和 HashMap 类似：**Node 数组 + 链表 + 红黑树**。

不再使用分段锁，而是用 **CAS + synchronized** 保证线程安全。

**put 流程**：
1. 计算 key 的 hash 值，确定桶位置
2. 如果数组为空，用 CAS 初始化数组
3. 如果该桶位置为 null，用 CAS 尝试放入新节点
   - 成功：直接返回
   - 失败：说明有并发，进入下一步
4. 如果头节点的 hash == MOVED（-1），说明正在扩容，当前线程帮助扩容
5. 否则，用 **synchronized** 锁住头节点
6. 遍历链表或红黑树，插入或更新节点
7. 插入后，如果链表长度 > 8 且数组长度 >= 64，转为红黑树
8. size 增加，检查是否需要扩容

**synchronized 锁的是头节点**，不是整个数组，所以锁的粒度更细，并发度更高。

### 3. size 计算

JDK8 中 size 的计算比较巧妙：

- 使用 **baseCount** + **CounterCell[]** 数组来统计元素个数
- 没有并发竞争时，直接用 CAS 更新 baseCount
- 有竞争时，不同线程更新不同的 CounterCell
- 计算 size 时，baseCount + 所有 CounterCell 的值

这是一种**空间换时间**的策略，避免了所有线程竞争一个变量。

**答案解析**:

ConcurrentHashMap 是面试高频考点，特别是 JDK7 和 JDK8 的实现差异。

JDK7 使用分段锁，将整个哈希表分成多个段，每个段有自己的锁，不同段之间可以并发操作。但分段数是固定的，而且同一个段内还是串行的。

JDK8 放弃了分段锁的设计，改用 CAS + synchronized，锁的粒度是每个桶的头节点，并发度更高。当没有冲突时用 CAS 无锁操作，有冲突时用 synchronized 加锁。synchronized 在 JDK8 中已经做了很多优化（偏向锁、轻量级锁、重量级锁），性能并不比 ReentrantLock 差。

size 的计算也很有特色，使用 CounterCell 数组分散计数，避免了并发竞争。

**扩展问题**:
- JDK7 和 JDK8 的 ConcurrentHashMap 有什么区别？
- ConcurrentHashMap 的 size 是怎么计算的？
- ConcurrentHashMap 为什么不允许 null 键和 null 值？
- ConcurrentHashMap 的扩容过程是什么样的？
- ConcurrentHashMap 和 Hashtable 哪个效率高？为什么？

---

## Q5: HashMap 的扩容机制

**考察点**: 扩容触发条件、扩容过程、重新哈希、JDK7和JDK8的区别

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 扩容触发条件

当 HashMap 中元素个数 size > 阈值（threshold）时，触发扩容。

```
threshold = capacity * loadFactor
```

- capacity：数组容量，初始为 16
- loadFactor：加载因子，默认 0.75
- threshold：扩容阈值，初始为 16 * 0.75 = 12

### 2. 扩容过程

扩容就是创建一个新的数组，容量是原来的 **2 倍**，然后将旧数组的元素重新计算位置，放到新数组中。

### 3. JDK7 的扩容（头插法）

JDK7 扩容时使用**头插法**转移元素，会导致链表顺序反转。

```java
// JDK7 扩容转移元素（简化版）
void transfer(Entry[] newTable) {
    for (Entry<K,V> e : table) {
        while(null != e) {
            Entry<K,V> next = e.next;
            int i = indexFor(e.hash, newTable.length);
            e.next = newTable[i]; // 头插法
            newTable[i] = e;
            e = next;
        }
    }
}
```

**问题**：多线程环境下，头插法可能导致**死循环**（链表形成环）。

### 4. JDK8 的扩容（尾插法）

JDK8 扩容时使用**尾插法**，不会反转链表顺序。

而且 JDK8 有一个优化：**不需要重新计算 hash 值**。

因为容量是 2 倍扩容（n → 2n），元素在新数组中的位置只有两种可能：
- 原位置（hash 的新增高位是 0）
- 原位置 + oldCap（hash 的新增高位是 1）

```java
// JDK8 扩容的巧妙之处
if ((e.hash & oldCap) == 0) {
    // 高位为0，留在原位置
    loTail.next = e;
    loTail = e;
} else {
    // 高位为1，移到新位置（原位置 + oldCap）
    hiTail.next = e;
    hiTail = e;
}
```

这样只需要看 hash 值的新增那一位是 0 还是 1，就能确定新位置，不需要重新计算 hash。

### 5. 扩容为什么是 2 倍？

1. 保证容量始终是 2 的幂，可以用位运算代替取模
2. 扩容后元素位置要么不变，要么移动 oldCap 个位置，分布更均匀

**答案解析**:

HashMap 的扩容机制是面试高频考点。扩容的目的是为了减少哈希冲突，提高查找效率。

JDK7 和 JDK8 的扩容有很大区别：
- JDK7 用头插法，多线程下可能死循环
- JDK8 用尾插法，不会死循环，但多线程下可能有数据覆盖等问题

JDK8 的扩容优化很巧妙，利用了 2 倍扩容的特性，不需要重新计算 hash 值，只需要看新增的那一位是 0 还是 1。这也是为什么 HashMap 容量必须是 2 的幂的原因之一。

扩容是一个比较耗时的操作，因为需要重新计算所有元素的位置。如果能预估元素数量，最好在创建 HashMap 时指定初始容量，避免频繁扩容。

**扩展问题**:
- 为什么 HashMap 的加载因子是 0.75？
- HashMap 扩容时元素位置如何确定？
- JDK7 的 HashMap 扩容为什么会导致死循环？
- 初始化 HashMap 时指定初始容量有什么好处？
- 已知要存 1000 个元素，HashMap 初始容量设多少合适？

---

## Q6: HashMap 为什么线程不安全

**考察点**: 多线程下HashMap的问题、JDK7死循环、JDK8数据覆盖

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

HashMap 是线程不安全的，在多线程环境下可能出现各种问题。

### 1. JDK7 中的问题：死循环（链表成环）

JDK7 的 HashMap 在扩容时使用**头插法**转移元素，多线程并发扩容可能导致链表形成环形链表，后续 get 操作会进入死循环。

**场景**：
1. 两个线程同时 put，都触发扩容
2. 线程1 开始扩容，遍历链表，刚记录下 e 和 next
3. 线程2 抢占 CPU，完成了扩容（链表反转）
4. 线程1 恢复执行，继续按之前的指针转移
5. 最终导致链表形成环

结果：调用 get 方法遍历链表时，永远走不出来，CPU 占用 100%。

### 2. JDK8 中的问题：数据覆盖

JDK8 改用尾插法，解决了死循环问题，但仍然有其他线程安全问题。

**场景1：put 时数据覆盖**

```java
final V putVal(int hash, K key, V value, ...) {
    // ...
    if ((p = tab[i = (n - 1) & hash]) == null) {
        // 如果该位置为空，直接插入
        tab[i] = newNode(hash, key, value, null);
    }
    // ...
}
```

两个线程同时判断某位置为空，都执行插入操作，其中一个的数据会被覆盖。

**场景2：size++ 不准确**

```java
++modCount;
if (++size > threshold)
    resize();
```

`++size` 不是原子操作，多线程下可能丢失更新，导致 size 计算不准确。

**场景3：可能丢数据**

多个线程同时操作同一个链表，可能导致数据丢失。

### 3. 总结

| 版本 | 主要问题 |
|------|---------|
| JDK7 | 扩容时死循环、数据覆盖 |
| JDK8 | 数据覆盖、size不准确、数据丢失 |

### 4. 多线程环境下的解决方案

- **Collections.synchronizedMap(map)**：包装一层，所有方法加 synchronized（性能差）
- **Hashtable**：全表锁（性能差）
- **ConcurrentHashMap**：分段锁/CAS + synchronized（推荐，性能好）

**答案解析**:

HashMap 线程不安全是面试常考点。需要区分 JDK7 和 JDK8 的不同问题。

JDK7 最著名的问题是扩容死循环，这是因为头插法 + 并发扩容导致的。JDK8 改用尾插法解决了这个问题，但仍然有其他线程安全问题，比如数据覆盖。

根本原因是 HashMap 的所有操作都没有加锁，多个线程同时修改时会出现竞态条件。

在多线程环境下，一定要使用 ConcurrentHashMap，不要用 HashMap。即使 JDK8 的 HashMap 不会死循环了，也仍然是线程不安全的。

**扩展问题**:
- JDK7 的 HashMap 死循环是怎么形成的？
- JDK8 的 HashMap 还会死循环吗？为什么？
- 多线程环境下用什么代替 HashMap？
- ConcurrentHashMap 是怎么保证线程安全的？
- Collections.synchronizedMap 和 Hashtable 有什么区别？

---

## Q7: ConcurrentHashMap 和 Hashtable 的区别

**考察点**: 锁的粒度、实现方式、性能对比

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 核心区别对比

| 特性 | ConcurrentHashMap | Hashtable |
|------|-------------------|-----------|
| 线程安全 | 安全 | 安全 |
| 锁的实现 | CAS + synchronized（JDK8）、分段锁（JDK7） | synchronized |
| 锁的粒度 | 桶级别（细） | 整个表（粗） |
| 效率 | 高 | 低 |
| null键 | 不允许 | 不允许 |
| null值 | 不允许 | 不允许 |
| 底层结构 | 数组+链表+红黑树（JDK8） | 数组+链表 |
| 迭代方式 | fail-safe（弱一致性） | fail-fast（JDK8也有fail-fast） |

### 2. 锁的粒度对比

**Hashtable**：
- 一把锁锁整个哈希表
- 所有操作都竞争同一把锁
- 并发度 = 1，同一时间只能有一个线程操作

```java
public synchronized V put(K key, V value) { ... }
public synchronized V get(Object key) { ... }
```

**ConcurrentHashMap（JDK8）**：
- 锁的粒度是每个桶的头节点
- 不同桶之间的操作互不干扰
- 并发度 = 数组长度（理论上）
- 没有竞争时用 CAS，有竞争时用 synchronized

### 3. 性能对比

ConcurrentHashMap 的性能远高于 Hashtable，因为：
1. 锁的粒度更细，不同桶可以并发操作
2. 读操作几乎无锁（volatile + CAS）
3. 没有竞争时用 CAS 无锁操作

Hashtable 因为锁粒度太大，在高并发场景下性能很差，已经不推荐使用了。

### 4. 迭代器的区别

- **Hashtable**：迭代器是 fail-fast 的，遍历过程中如果 map 被修改会抛出 ConcurrentModificationException
- **ConcurrentHashMap**：迭代器是弱一致性的（fail-safe），遍历过程中可以修改，不会抛异常，但遍历的数据可能不是最新的

**答案解析**:

ConcurrentHashMap 和 Hashtable 都是线程安全的 Map，但实现方式和性能差异很大。

Hashtable 是 Java 早期的实现，使用全表锁，效率很低，基本已经废弃了。ConcurrentHashMap 是更现代的实现，通过更细粒度的锁来提高并发性能。

JDK8 的 ConcurrentHashMap 用 synchronized 而不是 ReentrantLock，原因是：
1. synchronized 在 JDK8 中已经做了很多优化，性能不逊于 ReentrantLock
2. synchronized 是 JVM 层面的，后续还会持续优化
3. 减少内存开销（不需要每个节点都维护一个锁对象）

两者都不允许 null 键和 null 值，这是因为在并发环境下，无法区分是 key 不存在返回 null，还是值就是 null。

**扩展问题**:
- ConcurrentHashMap 为什么不允许 null 值？
- Hashtable 和 Collections.synchronizedMap 哪个效率高？
- ConcurrentHashMap 的迭代器是 fail-safe 吗？
- ConcurrentHashMap 的 size 计算和 Hashtable 有什么不同？
- 为什么 JDK8 用 synchronized 代替 ReentrantLock？

---

## Q8: HashSet 的底层实现

**考察点**: HashSet和HashMap的关系、add方法原理

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 底层实现

**HashSet 底层就是 HashMap**！

HashSet 的所有操作都是基于 HashMap 实现的，只是只使用 key，value 是一个固定的 Object 对象。

```java
// HashSet 源码
public class HashSet<E> extends AbstractSet<E> {
    private transient HashMap<E,Object> map;
    
    // 固定的value对象
    private static final Object PRESENT = new Object();
    
    public HashSet() {
        map = new HashMap<>();
    }
}
```

### 2. add 方法

```java
public boolean add(E e) {
    return map.put(e, PRESENT) == null;
}
```

- 将元素作为 key 存入 HashMap
- value 固定是 PRESENT 对象
- 如果 put 返回 null，说明添加成功（key 不存在）
- 如果 put 返回旧值，说明添加失败（key 已存在）

这也是为什么 HashSet 元素不重复的原因——HashMap 的 key 不能重复。

### 3. 其他方法

```java
public boolean remove(Object o) {
    return map.remove(o) == PRESENT;
}

public boolean contains(Object o) {
    return map.containsKey(o);
}

public int size() {
    return map.size();
}
```

几乎所有方法都是调用 HashMap 的对应方法。

### 4. 特点

- 元素无序（不保证插入顺序）
- 元素不重复
- 允许 null 元素
- 线程不安全
- 底层 HashMap

**答案解析**:

HashSet 的底层实现非常简单，就是用 HashMap 来存储元素，元素作为 key，value 是一个固定的 Object。这是典型的复用代码的设计。

因为基于 HashMap，所以 HashSet 的很多特性和 HashMap 是一致的：
- 不保证有序
- 允许 null（HashMap 允许一个 null 键）
- 线程不安全
- 初始容量16，加载因子0.75

HashSet 的 add 方法返回值表示是否添加成功，如果元素已存在返回 false，这也是利用了 HashMap 的 put 方法返回旧值的特性。

**扩展问题**:
- HashSet 为什么能去重？
- TreeSet 的底层实现是什么？
- LinkedHashSet 的底层实现是什么？
- HashSet 怎么保证元素不重复？
- HashSet 和 TreeSet 的区别？

---

## Q9: TreeMap 和 HashMap 的区别

**考察点**: 数据结构、有序性、性能、适用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 核心区别对比

| 特性 | HashMap | TreeMap |
|------|---------|---------|
| 底层结构 | 数组+链表+红黑树 | 红黑树 |
| 有序性 | 无序 | 有序（key排序） |
| 查找时间 | O(1) 平均 | O(logn) |
| 空间占用 | 大（数组+链表） | 小（只有树节点） |
| 比较方式 | equals + hashCode | Comparable / Comparator |
| 父接口 | Map | NavigableMap → SortedMap → Map |
| null键 | 允许一个 | 不允许（比较会抛异常） |
| 适用场景 | 快速查找 | 有序遍历、范围查找 |

### 2. 有序性

**HashMap**：无序，不保证元素的顺序，也不保证顺序随时间不变。

**TreeMap**：有序，按照 key 的自然顺序或自定义比较器排序。

```java
// 默认自然排序
TreeMap<Integer, String> map = new TreeMap<>();
map.put(3, "c");
map.put(1, "a");
map.put(2, "b");
// 遍历顺序：1=a, 2=b, 3=c

// 自定义比较器
TreeMap<String, String> map2 = new TreeMap<>(new Comparator<String>() {
    @Override
    public int compare(String o1, String o2) {
        return o2.compareTo(o1); // 倒序
    }
});
```

### 3. TreeMap 的特有方法

因为实现了 NavigableMap 接口，TreeMap 有很多有序操作的方法：

```java
treeMap.firstKey(); // 第一个key
treeMap.lastKey(); // 最后一个key
treeMap.headMap(toKey); // 小于toKey的子map
treeMap.tailMap(fromKey); // 大于等于fromKey的子map
treeMap.subMap(fromKey, toKey); // 区间子map
treeMap.ceilingKey(key); // 大于等于key的最小key
treeMap.floorKey(key); // 小于等于key的最大key
```

### 4. 性能对比

- **HashMap**：平均查找时间 O(1)，最坏 O(logn)（JDK8红黑树）
- **TreeMap**：查找、插入、删除都是 O(logn)

HashMap 查找更快，但 TreeMap 支持有序操作和范围查找。

**答案解析**:

HashMap 和 TreeMap 是 Map 接口的两个重要实现，各有优缺点。

HashMap 基于哈希表，查找速度快，是最常用的 Map 实现。TreeMap 基于红黑树，虽然查找速度不如 HashMap，但它是有序的，支持范围查找等有序操作。

选择使用哪个取决于具体场景：
- 只需要快速查找：用 HashMap
- 需要有序遍历或范围查询：用 TreeMap

TreeMap 的 key 必须实现 Comparable 接口，或者在构造时传入 Comparator，否则会抛出 ClassCastException。这也是 TreeMap 不允许 null 键的原因——null 无法比较。

**扩展问题**:
- TreeMap 是怎么实现有序的？
- TreeMap 的 key 可以是自定义对象吗？需要什么条件？
- TreeMap 和 LinkedHashMap 的区别？
- 红黑树的特点是什么？
- 什么场景下用 TreeMap 而不是 HashMap？

---

## Q10: List、Set、Map 的区别

**考察点**: 三大集合体系的特点和区别

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 三大集合体系

Java 集合框架主要分为三大体系：**List**、**Set**、**Map**。

### 2. List（列表）

**特点**：
- 有序（存储顺序和取出顺序一致）
- 可重复
- 有索引，可以通过索引访问元素

**常用实现类**：
- **ArrayList**：数组实现，查询快，增删慢，线程不安全
- **LinkedList**：链表实现，增删快，查询慢，线程不安全
- **Vector**：数组实现，线程安全（synchronized），效率低，已过时

**常用方法**：
```java
list.add(index, element); // 指定位置添加
list.get(index); // 获取指定位置元素
list.remove(index); // 删除指定位置元素
list.indexOf(obj); // 查找元素位置
```

### 3. Set（集合）

**特点**：
- 无序（HashSet无序，TreeSet有序，LinkedHashSet有序）
- 不可重复
- 没有索引

**常用实现类**：
- **HashSet**：HashMap实现，无序，去重，线程不安全
- **LinkedHashSet**：LinkedHashMap实现，有序（插入顺序），去重
- **TreeSet**：TreeMap实现，有序（排序），去重

**常用方法**：
```java
set.add(element); // 添加
set.contains(obj); // 是否包含
set.remove(obj); // 删除
```

### 4. Map（映射）

**特点**：
- 键值对存储（key-value）
- key 不可重复，value 可重复
- 一个 key 对应一个 value

**常用实现类**：
- **HashMap**：数组+链表+红黑树，无序，线程不安全
- **LinkedHashMap**：HashMap + 双向链表，有序
- **TreeMap**：红黑树，有序
- **Hashtable**：数组+链表，线程安全，已过时
- **ConcurrentHashMap**：线程安全，高性能

**常用方法**：
```java
map.put(key, value); // 添加
map.get(key); // 获取
map.remove(key); // 删除
map.containsKey(key); // 是否包含key
map.keySet(); // 获取所有key
map.values(); // 获取所有value
map.entrySet(); // 获取所有键值对
```

### 5. 对比总结

| 特性 | List | Set | Map |
|------|------|-----|-----|
| 元素有序 | 是 | 不一定 | 不一定 |
| 元素可重复 | 是 | 否 | key否，value是 |
| 有索引 | 是 | 否 | 无索引，用key访问 |
| 存储方式 | 单个元素 | 单个元素 | 键值对 |
| 遍历方式 | fori、增强for、迭代器 | 增强for、迭代器 | keySet、entrySet |

**答案解析**:

List、Set、Map 是 Java 集合框架的三大核心接口，各有特点。

List 和 Set 都继承自 Collection 接口，存储的是单个元素。List 有序可重复，Set 无序不可重复。

Map 是独立的接口，存储的是键值对。Map 和 Set 关系密切：HashSet 底层是 HashMap，TreeSet 底层是 TreeMap，本质上 Set 就是只使用 key 的 Map。

选择使用哪种集合取决于具体需求：
- 需要按索引访问：用 List
- 需要去重：用 Set
- 需要键值对映射：用 Map

**扩展问题**:
- Collection 和 Collections 的区别？
- Set 和 List 遍历方式有什么不同？
- 为什么 Map 不继承 Collection？
- 如何遍历 Map？有几种方式？
- 集合和数组的区别？怎么转换？

---

## Q11: ArrayList 的扩容机制

**考察点**: 初始容量、扩容时机、扩容倍数、Arrays.copyOf

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 初始容量

**JDK7**：创建 ArrayList 时直接初始化为容量 10 的数组。

**JDK8**：创建 ArrayList 时初始化为空数组（DEFAULTCAPACITY_EMPTY_ELEMENTDATA），第一次添加元素时才初始化为容量 10 的数组（懒加载）。

```java
// JDK8 ArrayList 源码
private static final int DEFAULT_CAPACITY = 10;
private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};

public ArrayList() {
    this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}
```

JDK8 这样做是为了节省内存，如果创建了 ArrayList 但一直不用，就不会分配数组空间。

### 2. 扩容时机

当添加元素时，如果元素个数超过当前数组容量，触发扩容。

```java
public boolean add(E e) {
    ensureCapacityInternal(size + 1); // 确保容量足够
    elementData[size++] = e;
    return true;
}
```

### 3. 扩容过程

1. 计算新容量：**新容量 = 旧容量 + 旧容量 / 2**（即 1.5 倍）
2. 创建新数组，容量为新容量
3. 将旧数组的元素复制到新数组（Arrays.copyOf）
4. 旧数组被 GC 回收

```java
// JDK8 扩容核心代码
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1); // 1.5倍
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

### 4. 扩容为什么是 1.5 倍？

- 1.5 倍是空间和时间的权衡
- 太小（如1.2倍）：扩容频繁，性能差
- 太大（如2倍）：空间浪费多
- 1.5 倍既能减少扩容次数，又不会太浪费空间

### 5. 优化建议

如果能预估元素数量，建议在创建 ArrayList 时指定初始容量，避免频繁扩容：

```java
ArrayList<String> list = new ArrayList<>(1000); // 指定初始容量
```

**答案解析**:

ArrayList 的扩容机制是基础面试题。核心要点是：初始容量 10，扩容 1.5 倍，底层用 Arrays.copyOf 复制数组。

JDK7 和 JDK8 的区别在于初始化时机：JDK7 立即初始化容量为 10 的数组，JDK8 延迟到第一次添加时才初始化。

`oldCapacity + (oldCapacity >> 1)` 等价于 `oldCapacity * 1.5`，用位运算比乘法效率更高。

扩容是一个比较耗时的操作，因为需要创建新数组并复制所有元素。在大数据量场景下，合理设置初始容量可以显著提升性能。

**扩展问题**:
- JDK7 和 JDK8 的 ArrayList 初始化有什么区别？
- ArrayList 扩容为什么是 1.5 倍而不是 2 倍？
- Arrays.copyOf 和 System.arraycopy 的区别？
- ArrayList 为什么用 transient 修饰 elementData？
- 如何实现 ArrayList 的缩容？

---

## Q12: fail-fast 和 fail-safe 的区别

**考察点**: 快速失败、安全失败、ConcurrentModificationException

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. fail-fast（快速失败）

**定义**：在用迭代器遍历集合时，如果集合的结构被修改（增加、删除元素），会立即抛出 **ConcurrentModificationException**。

**原理**：
- 集合中有一个 `modCount` 变量，记录集合被修改的次数
- 迭代器创建时，记录 `expectedModCount = modCount`
- 每次迭代时，检查 `modCount == expectedModCount`
- 如果不等，说明集合被修改了，抛出异常

```java
// ArrayList.Itr 迭代器源码
int expectedModCount = modCount;

public E next() {
    checkForComodification();
    // ...
}

final void checkForComodification() {
    if (modCount != expectedModCount)
        throw new ConcurrentModificationException();
}
```

**常见的 fail-fast 集合**：
- ArrayList、LinkedList、HashSet、HashMap 等

**示例**：
```java
ArrayList<String> list = new ArrayList<>();
list.add("a");
list.add("b");

for (String s : list) {
    if ("a".equals(s)) {
        list.remove(s); // 抛 ConcurrentModificationException
    }
}
```

注意：增强 for 循环底层就是迭代器。

### 2. fail-safe（安全失败）

**定义**：遍历的是集合的一个副本，集合的修改不会影响遍历，不会抛出异常。

**原理**：
- 遍历的是原集合的拷贝
- 原集合的修改不影响遍历
- 缺点：不能保证遍历到最新的数据

**常见的 fail-safe 集合**（java.util.concurrent 包下）：
- ConcurrentHashMap、CopyOnWriteArrayList 等

**示例**：
```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("a");
list.add("b");

for (String s : list) {
    if ("a".equals(s)) {
        list.remove(s); // 不会抛异常
    }
}
```

### 3. 对比总结

| 特性 | fail-fast | fail-safe |
|------|-----------|-----------|
| 异常 | 抛 ConcurrentModificationException | 不抛异常 |
| 遍历对象 | 原集合 | 集合副本 |
| 数据一致性 | 实时一致 | 弱一致性 |
| 内存占用 | 少 | 多（需要复制） |
| 性能 | 高 | 低 |
| 代表类 | ArrayList、HashMap | ConcurrentHashMap、CopyOnWriteArrayList |

**答案解析**:

fail-fast 和 fail-safe 是集合遍历的两种策略。

fail-fast 是 Java 集合框架的默认机制，它通过 modCount 来检测并发修改。它不是为了防止并发修改，而是为了快速发现问题，避免出现不可预期的行为。

fail-safe 是并发集合的特性，它通过拷贝集合来避免并发修改异常，但代价是内存占用增加，而且不能保证遍历到最新数据（弱一致性）。

需要注意的是，fail-fast 不是绝对的，它是"尽力而为"的检测。如果修改和遍历的时机刚好错开，可能不会检测到。所以不能依赖 fail-fast 来做并发控制。

在迭代时删除元素，正确的做法是使用迭代器的 remove 方法，而不是集合的 remove 方法。

**扩展问题**:
- 如何在遍历 List 时安全地删除元素？
- fail-fast 是绝对可靠的吗？为什么？
- CopyOnWriteArrayList 是怎么实现 fail-safe 的？
- modCount 是线程安全的吗？
- 为什么迭代器的 remove 方法就不会抛异常？

---

## Q13: Iterator 和 ListIterator 的区别

**考察点**: 两种迭代器的功能差异

**难度**: 简单

**频率**: ⭐⭐⭐

**标准答案**:

### 1. Iterator

Iterator 是所有集合都有的迭代器，用于遍历集合。

**方法**：
```java
boolean hasNext(); // 是否有下一个元素
E next(); // 返回下一个元素
void remove(); // 删除刚返回的元素
```

**特点**：
- 只能**单向**遍历（从前往后）
- 只能删除元素，不能添加和修改
- 所有 Collection 体系的集合都支持

```java
ArrayList<String> list = new ArrayList<>(Arrays.asList("a", "b", "c"));
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String s = it.next();
    if ("a".equals(s)) {
        it.remove(); // 安全删除
    }
}
```

### 2. ListIterator

ListIterator 是 List 特有的迭代器，功能更强大。

**方法**：
```java
// 正向遍历
boolean hasNext();
E next();
int nextIndex();

// 反向遍历
boolean hasPrevious();
E previous();
int previousIndex();

// 修改操作
void add(E e); // 添加元素
void set(E e); // 修改元素
void remove(); // 删除元素
```

**特点**：
- 可以**双向**遍历（向前和向后）
- 可以添加、修改、删除元素
- 可以获取当前位置（索引）
- 只有 List 体系的集合支持

```java
ArrayList<String> list = new ArrayList<>(Arrays.asList("a", "b", "c"));
ListIterator<String> it = list.listIterator();

// 正向遍历
while (it.hasNext()) {
    System.out.println(it.next());
}

// 反向遍历
while (it.hasPrevious()) {
    System.out.println(it.previous());
}
```

### 3. 对比总结

| 特性 | Iterator | ListIterator |
|------|----------|--------------|
| 遍历方向 | 只能向前 | 双向（向前+向后） |
| 添加元素 | 不可以 | 可以（add） |
| 修改元素 | 不可以 | 可以（set） |
| 删除元素 | 可以 | 可以 |
| 获取索引 | 不可以 | 可以（nextIndex/previousIndex） |
| 适用范围 | 所有Collection | 只有List |
| 获取方式 | iterator() | listIterator() |

**答案解析**:

Iterator 是最基础的迭代器，所有 Collection 集合都有。ListIterator 是 List 特有的，功能更丰富。

ListIterator 继承自 Iterator，在它的基础上增加了反向遍历、添加、修改、获取索引等功能。

两种迭代器都可以在遍历时安全删除元素（用迭代器自己的 remove 方法），不会触发 fail-fast 机制。

**扩展问题**:
- 迭代器和普通 for 循环遍历有什么区别？
- 为什么 Iterator 只有 remove 没有 add？
- ListIterator 的 add 方法把元素加到哪里？
- 增强 for 循环和迭代器的关系？
- 遍历 ArrayList 用哪种方式最快？

---

## Q14: HashMap 在 JDK1.7 和 1.8 的区别

**考察点**: 数据结构、插入方式、扩容、哈希计算等

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 核心区别对比

| 特性 | JDK7 | JDK8 |
|------|------|------|
| 底层结构 | 数组 + 链表 | 数组 + 链表 + 红黑树 |
| 插入方式 | 头插法 | 尾插法 |
| 扩容时元素位置 | 重新计算hash | hash & oldCap 判断 |
| 扩容死循环 | 可能 | 不会 |
| 哈希扰动 | 4次位运算 + 5次异或 | 1次位运算 + 1次异或 |
| 初始容量 | 16（创建时初始化） | 16（第一次put时初始化） |

### 2. 数据结构

**JDK7**：只有数组 + 链表，链表过长时查找效率低（O(n)）。

**JDK8**：引入红黑树，当链表长度 > 8 且数组长度 >= 64 时，链表转为红黑树，查找效率提升到 O(logn)。

为什么是 8？根据泊松分布，链表长度达到 8 的概率非常低（约千万分之六），所以正常情况下不会树化。

### 3. 插入方式

**JDK7**：头插法（新元素插到链表头部）。
- 优点：不需要遍历到链表尾部，插入快
- 缺点：扩容时会反转链表顺序，多线程下可能死循环

**JDK8**：尾插法（新元素插到链表尾部）。
- 优点：不会反转链表顺序，不会死循环
- 缺点：需要遍历到链表尾部

### 4. 扩容时的元素位置计算

**JDK7**：重新计算 hash 值，重新计算下标。
```java
int i = indexFor(e.hash, newCapacity);
```

**JDK8**：不需要重新计算 hash，只需要看 hash & oldCap 的结果：
- 结果为 0：位置不变
- 结果为 1：新位置 = 旧位置 + oldCap

```java
if ((e.hash & oldCap) == 0) {
    // 留在原位置
} else {
    // 移到 oldCap + 原位置
}
```

这样更高效，而且元素分布更均匀。

### 5. 哈希函数

**JDK7**：扰动函数比较复杂，4次位运算 + 5次异或。
```java
final int hash(Object k) {
    int h = 0;
    h ^= k.hashCode();
    h ^= (h >>> 20) ^ (h >>> 12);
    return h ^ (h >>> 7) ^ (h >>> 4);
}
```

**JDK8**：简化了扰动函数，1次位运算 + 1次异或。
```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

JDK8 简化的原因是引入了红黑树，即使哈希冲突多一点，查找效率也不会太差。

**答案解析**:

JDK8 对 HashMap 做了重大优化，是面试高频考点。

最主要的变化是引入了红黑树，解决了链表过长导致查找效率低的问题。当链表长度超过 8 且数组长度超过 64 时，链表转为红黑树，将查找时间复杂度从 O(n) 降到 O(logn)。

插入方式从头插法改成尾插法，解决了多线程扩容时的死循环问题。虽然 HashMap 本来就不应该在多线程下使用，但改了之后更安全。

扩容时的位置计算也做了优化，利用 2 倍扩容的特性，不需要重新计算 hash，只需要看新增的那一位。

**扩展问题**:
- JDK8 的 HashMap 为什么引入红黑树？
- 链表转红黑树的阈值为什么是 8？
- 红黑树什么时候退化为链表？阈值为什么是 6？
- JDK8 的 HashMap 是线程安全的吗？
- JDK8 的 HashMap 性能提升在哪里？

---

## Q15: 红黑树的特点和插入过程

**考察点**: 红黑树的性质、旋转、变色、插入操作

**难度**: 困难

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 红黑树的定义

红黑树是一种**自平衡的二叉搜索树**，通过颜色约束来保证树的大致平衡，从而保证查找、插入、删除的时间复杂度都是 O(logn)。

### 2. 红黑树的五大性质

1. **每个节点要么是红色，要么是黑色**
2. **根节点是黑色**
3. **每个叶子节点（NIL节点，空节点）是黑色**
4. **红色节点的两个子节点都是黑色**（不能有连续的红节点）
5. **从任意节点到其每个叶子节点的所有路径都包含相同数目的黑色节点**（黑高相同）

这些性质保证了红黑树的高度大约是 2log(n)，从而保证了 O(logn) 的时间复杂度。

### 3. 红黑树的基本操作

#### （1）变色

改变节点的颜色（红变黑或黑变红）。

#### （2）左旋

以某个节点为支点向左旋转。

```
    p                pr
   / \              /  \
  pl  pr    →     p    rr
     / \         / \
    rl  rr      pl  rl
```

#### （3）右旋

以某个节点为支点向右旋转。

```
     p             pl
    / \           /  \
   pl  pr   →    ll   p
  / \                 / \
 ll  lr              lr  pr
```

### 4. 插入过程

红黑树的插入分为两步：
1. 按二叉搜索树的方式插入节点（新节点默认是红色）
2. 调整（变色+旋转），使树重新满足红黑树性质

**插入后可能的情况**（设新节点为 N，父节点为 P，叔叔节点为 U，祖父节点为 G）：

**情况1：新节点是根节点**
- 直接染成黑色

**情况2：父节点是黑色**
- 不需要调整，性质没有被破坏

**情况3：父节点是红色，叔叔节点也是红色**
- 父节点变黑
- 叔叔节点变黑
- 祖父节点变红
- 将祖父节点作为新节点，继续向上调整

**情况4：父节点是红色，叔叔节点是黑色，新节点是父节点的右孩子**
- 以父节点为支点左旋
- 转化为情况5

**情况5：父节点是红色，叔叔节点是黑色，新节点是父节点的左孩子**
- 父节点变黑
- 祖父节点变红
- 以祖父节点为支点右旋

**答案解析**:

红黑树是比较难的数据结构，面试中一般不会要求写代码，但需要理解原理和过程。

红黑树的核心是通过颜色约束来保持平衡，它不是严格平衡的（不像 AVL 树那样高度差不超过 1），但保证了最长路径不超过最短路径的 2 倍，所以时间复杂度是 O(logn)。

插入操作的五种情况中，情况3需要向上递归调整，其他情况调整后就完成了。

红黑树在 Java 中有很多应用：
- HashMap（JDK8）
- TreeMap
- TreeSet
- JUC 中的 ConcurrentSkipListMap 等

选择红黑树而不是 AVL 树的原因是：红黑树的插入删除需要的旋转次数更少，更适合频繁修改的场景。

**扩展问题**:
- 红黑树和 AVL 树的区别？
- 红黑树的时间复杂度是多少？为什么？
- 红黑树的最长路径和最短路径有什么关系？
- HashMap 为什么用红黑树而不是 AVL 树？
- 红黑树的删除过程了解吗？

---

## Q16: LinkedHashMap 的实现和应用场景

**考察点**: LinkedHashMap的数据结构、有序性、LRU缓存实现

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 底层结构

LinkedHashMap 继承自 HashMap，在 HashMap 的基础上增加了一条**双向链表**，用来维护元素的顺序。

```
HashMap结构（数组+链表+红黑树） + 双向链表（维护顺序）
```

LinkedHashMap 的每个节点（Entry）继承自 HashMap.Node，增加了 before 和 after 两个指针，用来连接双向链表。

```java
// LinkedHashMap.Entry 源码
static class Entry<K,V> extends HashMap.Node<K,V> {
    Entry<K,V> before, after; // 双向链表指针
}
```

### 2. 两种顺序

LinkedHashMap 支持两种顺序：

**（1）插入顺序（默认）**
- 按照元素插入的顺序排列
- 访问元素不改变顺序

```java
LinkedHashMap<String, Integer> map = new LinkedHashMap<>();
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);
// 遍历顺序：a=1, b=2, c=3
```

**（2）访问顺序**
- 按照元素最后一次访问的时间排序（最近访问的在最后）
- 通过构造函数的 accessOrder 参数控制

```java
// accessOrder = true 表示访问顺序
LinkedHashMap<String, Integer> map = new LinkedHashMap<>(16, 0.75f, true);
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);

map.get("a"); // 访问a
// 遍历顺序：b=2, c=3, a=1（a被访问后移到最后）
```

### 3. 实现原理

访问元素时（get 方法），如果是访问顺序模式，会将被访问的节点移到双向链表的尾部。

```java
// LinkedHashMap 的 afterNodeAccess 方法
void afterNodeAccess(Node<K,V> e) {
    // 将节点e移到链表尾部
}
```

这是一个回调方法，HashMap 的 get 方法中会调用它。

### 4. 应用场景：LRU 缓存

LinkedHashMap 可以很方便地实现 **LRU（最近最少使用）缓存**。

```java
public class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private int capacity;
    
    public LRUCache(int capacity) {
        // accessOrder=true：访问顺序
        super(capacity, 0.75f, true);
        this.capacity = capacity;
    }
    
    // 重写这个方法，返回true时会移除最老的元素
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
}
```

原理：
- 访问顺序模式下，最近访问的元素在链表尾部
- 最久未访问的元素在链表头部
- 当元素数量超过容量时，移除头部元素

**答案解析**:

LinkedHashMap 是 HashMap 的子类，在 HashMap 的基础上增加了双向链表来维护顺序。它既保留了 HashMap 的快速查找特性，又能保证有序。

默认是插入顺序，如果设置 accessOrder 为 true，则是访问顺序。访问顺序是实现 LRU 缓存的基础。

removeEldestEntry 方法默认返回 false，如果重写它返回 size() > capacity，就能在元素超过容量时自动移除最老的元素，这就是 LRU 缓存的实现原理。

LinkedHashMap 的性能比 HashMap 略低，因为需要维护双向链表，但比 TreeMap 高。

**扩展问题**:
- LinkedHashMap 和 TreeMap 的有序性有什么区别？
- 如何用 LinkedHashMap 实现 LRU 缓存？
- LinkedHashMap 是线程安全的吗？
- LinkedHashMap 的双向链表和 HashMap 的链表有什么区别？
- accessOrder 模式下，put 已存在的 key 会改变顺序吗？

---

## Q17: WeakHashMap 的使用场景

**考察点**: 弱引用、WeakHashMap的原理、缓存场景

**难度**: 中等

**频率**: ⭐⭐⭐

**标准答案**:

### 1. 什么是 WeakHashMap

WeakHashMap 是一种特殊的 Map，它的 key 是**弱引用**（WeakReference），当 key 没有强引用时，下次 GC 就会被回收。

### 2. 实现原理

WeakHashMap 的 Entry 继承自 WeakReference，并且 Reference 的 referent 就是 key。

```java
// WeakHashMap.Entry 源码（简化）
private static class Entry<K,V> extends WeakReference<Object> implements Map.Entry<K,V> {
    V value;
    int hash;
    Entry<K,V> next;
    
    Entry(Object key, V value, ReferenceQueue<Object> queue, int hash, Entry<K,V> next) {
        super(key, queue); // key是弱引用
        this.value = value;
        this.hash = hash;
        this.next = next;
    }
}
```

当 key 没有强引用时，GC 会回收 key 对象，并将 Entry 放入引用队列（ReferenceQueue）。

每次操作 WeakHashMap 时（如 get、put、size 等），都会检查引用队列，将已经被回收的 Entry 从 Map 中移除。

### 3. 与 HashMap 的区别

| 特性 | HashMap | WeakHashMap |
|------|---------|-------------|
| key的引用类型 | 强引用 | 弱引用 |
| key被GC回收 | 不会 | 会（没有强引用时） |
| 用途 | 通用Map | 特殊场景缓存 |
| key的equals | 重写equals和hashCode | 用==比较（对象身份） |

注意：WeakHashMap 的 key 是基于对象身份比较的（==），不是基于 equals 方法。因为 key 被回收后，equals 比较就没有意义了。

### 4. 使用场景

**场景1：缓存**

当你需要缓存一些数据，但又不想因为缓存导致内存溢出时，可以用 WeakHashMap。当内存不足时，这些缓存会被 GC 回收。

但更常用的是软引用（SoftReference）实现的缓存，因为软引用是内存不足时才回收，而弱引用是每次 GC 都回收。

**场景2：监听器/回调注册**

在观察者模式中，如果监听器不需要显式注销，可以用 WeakHashMap，这样当监听器对象被回收后，自动从 Map 中移除，避免内存泄漏。

**场景3：元数据存储**

给某个对象附加一些元数据，但又不想修改该对象的类，而且当该对象被回收时，元数据也应该一起被回收。

```java
WeakHashMap<SomeObject, Metadata> metadataMap = new WeakHashMap<>();
```

**答案解析**:

WeakHashMap 利用了弱引用的特性：只要 GC 发生，弱引用对象就会被回收。这使得 WeakHashMap 适合存储那些可以被随时回收的数据。

WeakHashMap 的工作机制：
1. Entry 的 key 是弱引用
2. 当 key 没有强引用时，GC 回收 key
3. Entry 被放入引用队列
4. 下次操作 WeakHashMap 时，清理这些过期的 Entry

需要注意的是，WeakHashMap 的 value 是强引用，所以不要让 value 强引用 key，否则会导致 key 无法被回收。

ThreadLocalMap 和 WeakHashMap 有点类似，ThreadLocalMap 的 key 也是弱引用，但 ThreadLocalMap 不是 Map 接口的实现。

**扩展问题**:
- WeakHashMap 和 HashMap 的区别？
- WeakHashMap 的 key 为什么要用弱引用？
- WeakHashMap 的 value 是强引用还是弱引用？
- ThreadLocalMap 和 WeakHashMap 的异同？
- 软引用和弱引用的使用场景有什么区别？

---

## Q18: 集合工具类 Collections 的常用方法

**考察点**: Collections工具类的常用功能

**难度**: 简单

**频率**: ⭐⭐⭐

**标准答案**:

`Collections` 是 java.util 包下的一个工具类，专门用来操作 Collection 体系的集合。

### 1. 排序操作

```java
// 自然排序（元素必须实现Comparable）
Collections.sort(list);

// 自定义比较器排序
Collections.sort(list, new Comparator<String>() {
    @Override
    public int compare(String o1, String o2) {
        return o1.compareTo(o2);
    }
});

// 反转顺序
Collections.reverse(list);

// 随机打乱
Collections.shuffle(list);

// 交换两个位置的元素
Collections.swap(list, 0, 1);

// 旋转（向右移动n位）
Collections.rotate(list, 2);
```

### 2. 查找替换

```java
// 二分查找（必须先排序）
int index = Collections.binarySearch(list, "a");

// 最大值/最小值
String max = Collections.max(list);
String min = Collections.min(list);

// 自定义比较器的最大值
String max = Collections.max(list, comparator);

// 替换所有
Collections.replaceAll(list, "old", "new");

// 填充
Collections.fill(list, "fill");

// 出现次数
int count = Collections.frequency(list, "a");
```

### 3. 线程安全集合

将非线程安全的集合包装成线程安全的：

```java
List<String> syncList = Collections.synchronizedList(new ArrayList<>());
Set<String> syncSet = Collections.synchronizedSet(new HashSet<>());
Map<String, String> syncMap = Collections.synchronizedMap(new HashMap<>());
```

原理：包装一层，所有方法加 synchronized。但性能不如 JUC 下的并发集合，不推荐在高并发场景使用。

### 4. 不可变集合

将集合变成不可修改的：

```java
List<String> unmodList = Collections.unmodifiableList(list);
Set<String> unmodSet = Collections.unmodifiableSet(set);
Map<String, String> unmodMap = Collections.unmodifiableMap(map);
```

如果尝试修改，会抛出 UnsupportedOperationException。

### 5. 其他

```java
// 返回空集合（避免null）
List<String> emptyList = Collections.emptyList();
Map<String, String> emptyMap = Collections.emptyMap();

// 返回只有一个元素的集合
Set<String> singleton = Collections.singleton("a");

// 复制（目标集合长度必须>=源集合）
Collections.copy(destList, srcList);

// 批量添加
Collections.addAll(list, "a", "b", "c");
```

**答案解析**:

Collections 是一个工具类，提供了很多操作集合的静态方法。注意和 Collection 接口区分：
- Collection：是集合的顶级接口
- Collections：是操作集合的工具类

常用的几类方法：
1. 排序相关：sort、reverse、shuffle、swap
2. 查找相关：binarySearch、max、min、frequency
3. 线程安全：synchronizedXxx
4. 不可变：unmodifiableXxx
5. 其他：emptyXxx、singleton、addAll

需要注意的是，Collections.synchronizedList 等方法虽然能让集合变成线程安全的，但性能较差，因为是全表锁。高并发场景推荐使用 JUC 包下的并发集合。

**扩展问题**:
- Collection 和 Collections 的区别？
- Collections.synchronizedList 和 ConcurrentLinkedQueue 的区别？
- 不可变集合有什么用？
- Collections.emptyList() 和 new ArrayList() 有什么区别？
- 还有哪些类似的工具类？

---

## Q19: 如何实现线程安全的 List

**考察点**: 线程安全List的实现方式、各自的优缺点

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

Java 中实现线程安全的 List 有多种方式，各有优缺点。

### 1. Vector

Vector 是 JDK 最早的线程安全 List。

**特点**：
- 几乎所有方法都加了 synchronized
- 线程安全，但性能差
- 初始容量 10，扩容 2 倍
- 已过时，不推荐使用

```java
Vector<String> vector = new Vector<>();
```

### 2. Collections.synchronizedList

用 Collections 工具类包装 ArrayList。

**特点**：
- 包装一层，所有方法加 synchronized
- 线程安全，性能差（和 Vector 差不多）
- 迭代时需要手动加锁

```java
List<String> list = Collections.synchronizedList(new ArrayList<>());

// 迭代时需要手动加锁，否则可能并发修改异常
synchronized (list) {
    for (String s : list) {
        // ...
    }
}
```

### 3. CopyOnWriteArrayList（推荐在读多写少场景使用）

JUC 包下的并发 List，**写时复制**。

**特点**：
- 读操作无锁，性能高
- 写操作时复制一份新数组，修改后替换原数组
- 线程安全
- 数据最终一致性，不是实时一致
- 适合读多写少的场景

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
```

**原理**：
```java
public boolean add(E e) {
    final ReentrantLock lock = this.lock;
    lock.lock();
    try {
        Object[] elements = getArray();
        int len = elements.length;
        Object[] newElements = Arrays.copyOf(elements, len + 1); // 复制数组
        newElements[len] = e;
        setArray(newElements); // 替换原数组
        return true;
    } finally {
        lock.unlock();
    }
}
```

**优点**：
- 读操作完全无锁，性能很高
- 迭代安全，不会抛并发修改异常

**缺点**：
- 写操作需要复制数组，内存占用大
- 写操作性能差
- 数据不是实时一致的（弱一致性）

### 4. 对比总结

| 方式 | 线程安全 | 读性能 | 写性能 | 内存占用 | 一致性 | 适用场景 |
|------|---------|--------|--------|---------|--------|---------|
| Vector | 是 | 低（加锁） | 低（加锁） | 正常 | 强一致 | 已过时 |
| Collections.synchronizedList | 是 | 低（加锁） | 低（加锁） | 正常 | 强一致 | 已过时 |
| CopyOnWriteArrayList | 是 | 高（无锁） | 低（复制数组） | 高（写时复制） | 弱一致 | 读多写少 |

**答案解析**:

实现线程安全的 List 主要有三种方式，其中 CopyOnWriteArrayList 是最常考的。

CopyOnWriteArrayList 的核心思想是**写时复制**：读操作完全不加锁，直接读取；写操作时，先复制一份新数组，在新数组上修改，修改完后将引用指向新数组。

这种方式的优点是读性能极高，适合读多写少的场景。缺点是写操作开销大，而且数据是弱一致性的（读操作可能读到旧数据）。

CopyOnWriteArrayList 的迭代器是 fail-safe 的，遍历过程中集合被修改不会抛异常。

**扩展问题**:
- CopyOnWriteArrayList 的实现原理？
- CopyOnWriteArrayList 的优缺点？
- CopyOnWriteArrayList 为什么适合读多写少？
- Vector 和 ArrayList 的区别？
- 有哪些线程安全的 Set？

---

## Q20: Comparable 和 Comparator 的区别

**考察点**: 两种比较器的区别、使用场景

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. Comparable（内部比较器）

Comparable 是一个接口，定义在 java.lang 包下。

```java
public interface Comparable<T> {
    public int compareTo(T o);
}
```

**特点**：
- 让类本身具有比较能力
- 需要让**类实现 Comparable 接口**
- 只有一个 compareTo 方法
- 称为"内部比较器"
- 只能有一种比较规则

```java
public class Person implements Comparable<Person> {
    private String name;
    private int age;
    
    @Override
    public int compareTo(Person o) {
        // 返回负数：this < o
        // 返回0：this == o
        // 返回正数：this > o
        return this.age - o.age; // 按年龄排序
    }
}

// 使用
Collections.sort(list); // 自动按compareTo排序
```

### 2. Comparator（外部比较器）

Comparator 也是一个接口，定义在 java.util 包下。

```java
public interface Comparator<T> {
    int compare(T o1, T o2);
}
```

**特点**：
- 作为独立的比较器，在外部实现
- 不需要修改类本身
- 可以有多个比较器，多种比较规则
- 称为"外部比较器"
- 策略模式的体现

```java
// 按年龄排序
Comparator<Person> ageComparator = new Comparator<Person>() {
    @Override
    public int compare(Person o1, Person o2) {
        return o1.getAge() - o2.getAge();
    }
};

// 按姓名排序
Comparator<Person> nameComparator = new Comparator<Person>() {
    @Override
    public int compare(Person o1, Person o2) {
        return o1.getName().compareTo(o2.getName());
    }
};

// 使用
Collections.sort(list, ageComparator); // 按年龄排
Collections.sort(list, nameComparator); // 按姓名排
```

### 3. 对比总结

| 特性 | Comparable | Comparator |
|------|-----------|------------|
| 位置 | java.lang | java.util |
| 方法 | compareTo(T o) | compare(T o1, T o2) |
| 实现方式 | 类自己实现 | 独立实现 |
| 比较规则 | 只能有一种 | 可以有多种 |
| 修改类 | 需要修改类 | 不需要修改类 |
| 别称 | 内部比较器 | 外部比较器 |
| 使用 | Collections.sort(list) | Collections.sort(list, comparator) |

### 4. 典型应用

- **Comparable**：String、Integer 等包装类都实现了 Comparable，所以可以直接排序
- **Comparator**：TreeMap、TreeSet 的构造函数可以传入 Comparator 指定排序规则

**答案解析**:

Comparable 和 Comparator 都是用来比较对象的接口，但使用方式不同。

Comparable 是让类本身具有比较能力，是"内部比较器"。如果一个类实现了 Comparable，就说明它的对象可以比较大小，可以直接用 Collections.sort() 排序。

Comparator 是独立的比较器，是"外部比较器"。它不需要修改类本身，可以灵活地定义多种比较规则。这是策略模式的典型应用。

选择哪个？
- 如果类只有一种默认的比较方式，用 Comparable
- 如果有多种比较方式，或者不能修改类，用 Comparator

**扩展问题**:
- compareTo 方法返回值代表什么？
- TreeMap 的 key 需要实现 Comparable 吗？
- 什么是策略模式？和 Comparator 有什么关系？
- Comparator 接口有哪些默认方法（JDK8）？
- 比较两个对象相等用 ==、equals、compareTo 有什么区别？

---

## Reference

1. 美团技术团队. *Java 8系列之重新认识HashMap*. https://tech.meituan.com/2016/06/24/java-hashmap.html, 访问时间：2026-07-28
2. OpenJDK. *java.util 包源码*. http://openjdk.java.net, 访问时间：2026-07-28
3. 牛客网. *Java集合面试题精选*. https://www.nowcoder.com, 访问时间：2026-07-28
4. 方腾飞. *Java并发编程的艺术*. 机械工业出版社, 2015
5. Oracle. *Java Collections Framework Documentation*. https://docs.oracle.com/javase/8/docs/technotes/guides/collections/, 访问时间：2026-07-28

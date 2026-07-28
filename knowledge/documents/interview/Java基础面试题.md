---
title: "Java基础面试题（20题）"
category: "面试题"
type: "Java后端"
difficulty: "中等"
tags: ["Java基础", "面向对象", "异常处理", "反射", "注解"]
source: ["Java核心技术卷I", "阿里巴巴Java开发手册", "牛客网Java面试题库"]
last_update: "2026-07-28"
---

# Java基础面试题（20题）

> 本文档涵盖Java后端开发中最核心的基础知识，包括面向对象、核心API、异常处理、反射、注解等核心知识点，适合初中级Java工程师面试必备。

---

## Q1: == 和 equals 的区别

**考察点**: 基本数据类型与引用类型的比较方式、Object类的equals方法、String类的equals重写

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

`==` 和 `equals` 是Java中两种不同的比较方式，主要区别如下：

### 1. == 运算符
- **基本数据类型**（byte、short、int、long、float、double、char、boolean）：比较的是**值**是否相等
- **引用数据类型**：比较的是**堆内存地址**（即两个引用是否指向同一个对象）

```java
int a = 10;
int b = 10;
System.out.println(a == b); // true，比较值

String s1 = new String("hello");
String s2 = new String("hello");
System.out.println(s1 == s2); // false，比较内存地址
```

### 2. equals 方法
- `equals` 是 `Object` 类中的方法，默认实现与 `==` 相同（比较内存地址）
- 很多类（如 String、Integer、Date等）会**重写** `equals` 方法**，改为比较对象的内容是否相等
- 自定义类如果不重写 `equals`，则默认使用 Object 类的实现，即比较地址

```java
String s1 = new String("hello");
String s2 = new String("hello");
System.out.println(s1.equals(s2)); // true，String重写了equals，比较内容

class Person {
    String name;
}
Person p1 = new Person();
Person p2 = new Person();
p1.name = "张三";
p2.name = "张三";
System.out.println(p1.equals(p2)); // false，没有重写equals，默认比较地址
```

### 3. String 类的特殊情况
```java
String s1 = "hello";
String s2 = "hello";
System.out.println(s1 == s2); // true，字符串常量池，指向同一对象
```

**答案解析**:

这道题的核心在于理解Java中数据类型的分类以及 Object 类中 equals 方法的默认行为。`==` 是运算符，对于基本类型比较值，引用类型比较地址；`equals` 是方法，默认比较地址，但可以被重写来比较内容。

String 类之所以重写 equals，是因为对于字符串来说，我们更关心的是内容是否相同，而不是是否为同一个对象。在实际开发中，比较对象内容相等性时，应该使用 equals 方法而不是 ==。

此外，还需要注意 String 常量池的概念：当使用字面量创建字符串时，JVM 会先在字符串常量池中查找，如果存在则直接返回引用，否则创建并放入池中。这也是为什么 `s1 == s2` 用字面量创建时返回 true 的原因。

**扩展问题**:
- 为什么重写 equals 时必须重写 hashCode？
- String 类的 intern() 方法有什么作用？
- 如何正确地重写 equals 方法？需要遵循哪些约定？
- Integer 的缓存机制是什么？`Integer a = 127; Integer b = 127; a == b` 的结果是什么？

---

## Q2: hashCode 和 equals 的关系

**考察点**: hashCode方法、equals方法、HashMap底层原理、哈希冲突

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 基本概念
- **hashCode()**：返回对象的哈希码值（int类型），用于确定对象在哈希表中的存储位置
- **equals()**：用于判断两个对象是否相等

### 2. 两者的关系约定

根据 Java 官方规范，hashCode 和 equals 之间有以下约定：

**（1）如果两个对象通过 equals 比较相等（equals 返回 true），那么它们的 hashCode 一定相等。

**（2）如果两个对象 hashCode 相等，它们的 equals 不一定返回 true（可能发生哈希冲突）。

**（3）如果两个对象 equals 不相等，它们的 hashCode 可以相等（哈希冲突），但最好不相等，以提高哈希表性能。

### 3. 为什么重写 equals 必须重写 hashCode？

如果只重写 equals 不重写 hashCode，会导致在使用 HashMap、HashSet 等基于哈希表的集合时出现问题：

```java
class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Person)) return false;
        Person p = (Person) obj;
        return this.name.equals(p.name) && this.age == p.age;
    }
    // 没有重写 hashCode
}

public class Test {
    public static void main(String[] args) {
        Person p1 = new Person("张三", 20);
        Person p2 = new Person("张三", 20);
        
        System.out.println(p1.equals(p2)); // true
        
        HashSet<Person> set = new HashSet<>();
        set.add(p1);
        set.add(p2);
        System.out.println(set.size()); // 2，而不是预期的1！
    }
}
```

**原因分析**：HashSet 添加元素时，先计算 hashCode 确定存储位置，如果该位置没有元素直接放入；如果有元素，再用 equals 比较。由于没有重写 hashCode，p1 和 p2 的 hashCode 不同（Object 默认的实现，基于内存地址），会被存到不同的桶中，导致重复元素。

### 4. 如何正确重写 hashCode？

```java
@Override
public int hashCode() {
    int result = 17;
    result = 31 * result + name.hashCode();
    result = 31 * result + age;
    return result;
}
```

**答案解析**:

hashCode 和 equals 的关系是 Java 集合框架的基础，也是面试高频题。核心在于理解哈希表的工作原理：先通过 hashCode 定位到桶（数组下标），再通过 equals 在链表/红黑树中查找元素。

31 这个数字的选择有两个原因：
1. 31 是质数，可以减少哈希冲突
2. `31 * i` 可以被 JVM 优化为 `(i << 5) - i`，计算效率更高

重写 hashCode 的标准范式是：选择一个非零质数（通常是17）作为初始值，然后对每个参与 equals 比较的字段，计算其哈希值并累加到结果中。

**扩展问题**:
- HashMap 中如何解决哈希冲突？
- 为什么 HashMap 中计算桶位置要用 `(n-1) & hash 而不是取模运算？
- 两个对象 hashCode 相同，equals 不同，在 HashMap 中如何存储？
- 为什么 String、Integer 等包装类适合作为 HashMap 的 key？

---

## Q3: String、StringBuffer、StringBuilder 的区别

**考察点**: 字符串不可变性、线程安全、性能对比

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 三者的核心区别

| 特性 | String | StringBuffer | StringBuilder |
|------|--------|--------------|---------------|
| 可变性 | 不可变（final修饰char数组） | 可变 | 可变 |
| 线程安全 | 安全（不可变对象天然安全） | 安全（synchronized） | 不安全 |
| 性能 | 低（每次修改创建新对象） | 中 | 高 |
| 适用场景 | 字符串不经常修改 | 多线程环境 | 单线程环境 |

### 2. String 的不可变性

```java
String s = "hello";
s = s + " world";
// 实际上创建了新的String对象，s指向新对象
```

String 不可变的原因：
- 底层 `char[] value` 被 `final` 修饰（JDK9及以后是 `byte[] value`）
- String 类被 `final` 修饰，不能被继承修改
- 所有修改操作（如 substring、concat、replace）都会返回新的 String 对象

### 3. StringBuffer 和 StringBuilder

两者都继承自 `AbstractStringBuilder`，底层都是可变的 char 数组（初始容量16，扩容时变为原来的2倍+2。

**StringBuffer**：
- 几乎所有方法都加了 `synchronized` 关键字
- 线程安全，但性能较低
- 适合多线程环境下使用

**StringBuilder**：
- 没有 synchronized 修饰
- 线程不安全，但性能高
- 适合单线程环境下使用（推荐）

### 4. 性能对比

```java
// String 拼接（性能差，产生大量临时对象）
String s = "";
for (int i = 0; i < 10000; i++) {
    s += i; // 每次循环创建新对象
}

// StringBuilder 拼接（性能好）
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);
}
String result = sb.toString();
```

**答案解析**:

这道题考察对Java字符串处理的深入理解。String 的不可变性是 Java 中非常重要的设计，它保证了：
1. 字符串常量池可以复用
2. 线程安全
3. 可以作为 HashMap 的 key（因为不可变，hashCode 可以缓存

StringBuffer 和 StringBuilder 的区别主要在于线程安全性。在单线程环境下，优先使用 StringBuilder 以获得更好的性能。

需要注意的是，Java 编译器对字符串拼接做了优化：`String s = "a" + "b" + "c";` 会在编译期直接优化为 `"abc"`，而运行时的字符串拼接（如变量参与）则会被优化为 StringBuilder 的 append 操作。

**扩展问题**:
- String 为什么要设计成不可变的？有什么好处？
- String 字符串常量池在 JDK1.7 和 1.8 有什么变化？
- StringBuffer 和 StringBuilder 的扩容机制是什么？
- 什么是字符串常量池？intern() 方法的作用？
- JDK9 中 String 的底层实现为什么从 char[] 改成了 byte[]？

---

## Q4: final 关键字的用法

**考察点**: final修饰类、方法、变量的不同作用

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

`final` 关键字可以修饰**类**、**方法**和**变量**，表示"最终的"、"不可改变的"。

### 1. final 修饰类

被 final 修饰的类**不能被继承**，即没有子类。

```java
public final class String {
    // ...
}
// 报错：Cannot inherit from final 'java.lang.String'
// class MyString extends String {}
```

常见的 final 类：String、System、Math 等。

### 2. final 修饰方法

被 final 修饰的方法**不能被重写**（Override）。

```java
public class Parent {
    public final void method() {
        System.out.println("final method");
    }
}

public class Child extends Parent {
    // 编译错误：Cannot override the final method from Parent
    // public void method() {}
}
```

注意：private 方法隐式地是 final 的，因为子类无法访问，自然无法重写。

### 3. final 修饰变量

被 final 修饰的变量**只能赋值一次**，赋值后不可改变。

**（1）修饰成员变量**

必须在声明时或构造方法中赋值：
```java
public class Test {
    final int a = 10; // 声明时赋值
    final int b;
    
    public Test() {
        b = 20; // 构造方法中赋值
    }
}
```

**（2）修饰局部变量**

使用前必须赋值：
```java
public void method() {
    final int x = 10;
    // x = 20; // 编译错误
}
```

**（3）修饰引用类型变量**

引用不可变（指向的对象地址不可变），但对象的内容可以变：
```java
final Person p = new Person("张三");
p.setName("李四"); // 可以，对象内容可变
// p = new Person("王五"); // 不可以，引用不可变
```

### 4. final 与 static final 配合使用（常量）

```java
public static final double PI = 3.1415926;
```

**答案解析**:

final 关键字体现了Java的设计哲学：**不可变性**。不可变对象有很多好处：线程安全、可以被缓存、安全性等。

需要特别注意：
- final 修饰基本类型：值不可变
- final 修饰引用类型：引用不可变（地址不可变），但对象内容可变

final 方法比非 final 方法执行效率略高，因为不需要动态绑定，可以在编译期确定调用哪个方法。

**扩展问题**:
- final 和 finally、finalize 有什么区别？
- 被 final 修饰的数组，数组元素可以修改吗？
- final 变量和普通变量在编译时有什么区别？
- 为什么局部内部类和匿名内部类为什么只能访问 final 的局部变量？

---

## Q5: static 关键字的作用

**考察点**: static修饰变量、方法、代码块、内部类

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

`static` 关键字表示"静态的"，可以修饰**变量**、**方法**、**代码块**和**内部类**。

### 1. static 修饰变量（静态变量/类变量）

- 属于**类**，不属于对象
- 所有对象共享一份
- 在类加载时初始化，只初始化一次
- 可以通过 `类名.变量名` 直接访问

```java
public class Person {
    static int count; // 静态变量
    String name; // 实例变量
}

Person.count = 0; // 通过类名访问
```

### 2. static 修饰方法（静态方法/类方法）

- 属于类，不属于对象
- 可以通过 `类名.方法名` 直接调用
- 静态方法中**不能访问实例变量和实例方法**（因为没有this）
- 静态方法中**不能使用 this 和 super**

```java
public class MathUtil {
    public static int add(int a, int b) {
        return a + b;
    }
}

int sum = MathUtil.add(1, 2); // 通过类名调用
```

### 3. static 修饰代码块（静态代码块）

- 在**类加载时执行**，只执行一次
- 用于初始化静态变量
- 静态代码块**不能访问实例变量

```java
public class Test {
    static int count;
    static {
        count = 100;
        System.out.println("静态代码块执行");
    }
}
```

### 4. static 修饰内部类（静态内部类）

- 静态内部类不依赖外部类对象
- 可以直接创建静态内部类对象
- 只能访问外部类的静态成员

```java
public class Outer {
    static class Inner {
        // ...
    }
}

Outer.Inner inner = new Outer.Inner(); // 不需要外部类对象
```

### 5. 执行顺序

```java
public class Test {
    static {
        System.out.println("静态代码块");
    }
    
    {
        System.out.println("构造代码块");
    }
    
    public Test() {
        System.out.println("构造方法");
    }
    
    public static void main(String[] args) {
        new Test();
        new Test();
    }
}
```

输出：
```
静态代码块
构造代码块
构造方法
构造代码块
构造方法
```

**答案解析**:

static 关键字的核心是**属于类而不属于对象。静态成员在内存中只有一份，被所有对象共享。

静态方法不能访问非静态成员，因为静态方法可以在没有对象的情况下调用，而非静态成员必须通过对象才能访问。

静态代码块常用于类加载时做一些初始化工作，比如加载驱动、读取配置文件等。

**扩展问题**:
- 静态变量和实例变量的区别？
- 为什么 main 方法是 static 的？
- 静态内部类和非静态内部类的区别？
- 静态方法能不能被重写吗？为什么？
- 类加载的过程是什么？静态变量什么时候初始化？

---

## Q6: 接口和抽象类的区别

**考察点**: 接口与抽象类的语法区别、设计层面的区别

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 语法层面的区别

| 特性 | 抽象类（abstract class） | 接口（interface） |
|------|------------------------|-----------------|
| 关键字 | abstract class | interface |
| 构造方法 | 有构造方法 | 没有构造方法 |
| 成员变量 | 可以有各种变量 | 只能是 public static final 常量 |
| 方法 | 可以有抽象方法和具体方法 | JDK8前只有抽象方法，JDK8后可有默认方法和静态方法，JDK9后可有私有方法 |
| 继承 | 单继承（一个类只能继承一个抽象类） | 多实现（一个类可以实现多个接口） |
| 访问修饰符 | 可以是 public、protected、default | 只能是 public |

### 2. 抽象类

```java
abstract class Animal {
    String name; // 成员变量
    
    Animal(String name) { // 构造方法
        this.name = name;
    }
    
    abstract void eat(); // 抽象方法
    
    void sleep() { // 普通方法
        System.out.println(name + "睡觉");
    }
}
```

### 3. 接口

```java
interface Flyable {
    // 常量（默认 public static final）
    int MAX_SPEED = 100;
    
    // 抽象方法（默认 public abstract）
    void fly();
    
    // JDK8：默认方法
    default void defaultMethod() {
        System.out.println("默认方法");
    }
    
    // JDK8：静态方法
    static void staticMethod() {
        System.out.println("静态方法");
    }
    
    // JDK9：私有方法
    // private void privateMethod() {}
}
```

### 4. 设计层面的区别

- **抽象类**：表示"is-a"关系，是对事物的抽象，是模板式设计
- **接口**：表示"like-a"关系，是对行为的抽象，是契约式设计

例如：
- 猫是动物（is-a）→ 抽象类 Animal
- 猫会跑（has-a能力）→ 接口 Runnable

**答案解析**:

接口和抽象类是Java面向对象的两个核心概念，也是面试必考题。

从语法上看，JDK8以后接口的功能越来越强大（默认方法、静态方法），但两者的本质区别在于设计理念：
- 抽象类是**模板设计**，提供了通用实现，子类继承后可以复用代码
- 接口是**契约设计**，定义了行为规范，实现类必须遵守契约

选择使用场景：
- 当需要共享代码或状态时，用抽象类
- 当只定义行为规范，允许多重继承时，用接口

**扩展问题**:
- JDK8 为什么要引入默认方法？
- 接口可以继承接口吗？抽象类可以实现接口吗？
- 一个类可以实现多个接口，如果两个接口有同名默认方法怎么办？
- 抽象类能被实例化吗？为什么？
- 接口和抽象类哪个更推荐使用哪个？为什么？

---

## Q7: Java 的四大引用类型

**考察点**: 强引用、软引用、弱引用、虚引用的区别和使用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

Java 有四种引用类型，强度从高到低依次为：**强引用**、**软引用**、**弱引用**、**虚引用**。

### 1. 强引用（Strong Reference）

- 最常见的引用，如 `Object obj = new Object();`
- 只要强引用存在，垃圾回收器**永远不会回收**被引用的对象
- 内存不足时，JVM 宁愿抛出 OOM 也不回收

```java
Object obj = new Object(); // 强引用
obj = null; // 取消强引用，对象可被回收
```

### 2. 软引用（Soft Reference）

- 使用 `SoftReference` 类实现
- 内存**内存不足时**才会被回收
- 适合实现内存敏感的高速缓存

```java
SoftReference<Object> softRef = new SoftReference<>(new Object());
Object obj = softRef.get(); // 获取对象
```

应用场景：图片缓存、网页缓存等内存敏感的缓存

### 3. 弱引用（Weak Reference）

- 使用 `WeakReference` 类实现
- 只要发生 GC 时就会被回收**（不管内存是否足够
- 生命周期比软引用更短

```java
WeakReference<Object> weakRef = new WeakReference<>(new Object());
Object obj = weakRef.get(); // 可能为null
```

应用场景：WeakHashMap、ThreadLocal

### 4. 虚引用（Phantom Reference）

- 使用 `PhantomReference` 类实现
- **get() 方法**永远返回 null
- 必须和引用队列（ReferenceQueue）联合使用
- 对象被回收前会收到系统通知

```java
ReferenceQueue<Object> queue = new ReferenceQueue<>();
PhantomReference<Object> phantomRef = new PhantomReference<>(new Object(), queue);
```

应用场景：管理堆外内存（如NIO中的DirectByteBuffer

### 5. 对比总结

| 引用类型 | 回收时机 | 用途 | 生存时间 |
|---------|---------|------|---------|
| 强引用 | 从不回收 | 一般对象引用 | JVM停止 |
| 软引用 | 内存不足时 | 内存敏感缓存 | 内存不足前 |
| 弱引用 | GC时 | 弱缓存、WeakHashMap | GC前 |
| 虚引用 | 对象回收时 | 堆外内存管理 | 对象回收前 |

**答案解析**:

四大引用类型是JVM垃圾回收的重要概念，不同引用类型决定了对象的不同的回收策略。

强引用是默认的引用类型，我们平时写的代码几乎都是强引用。软引用和弱引用都可以用来实现缓存，但软引用在内存不足才回收，弱引用只要GC就回收。

虚引用比较特殊，它不影响对象的生命周期，只是用来在对象被回收时收到通知，常用于管理堆外内存。

ThreadLocal 中使用了弱引用来防止内存泄漏：ThreadLocalMap 中的 key 是弱引用，当 ThreadLocal 没有强引用时，key 会被 GC 回收，这样 entry 的 key 变成 null，后续可以被清理。

**扩展问题**:
- ThreadLocal 为什么用弱引用？
- WeakHashMap 的实现原理？
- 软引用和弱引用的使用场景有什么区别？
- 引用队列（ReferenceQueue）的作用是什么？
- 如何用软引用实现一个简单的缓存？

---

## Q8: 重载和重写的区别

**考察点**: 方法重载、方法重写、多态

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 重载（Overload）

**定义**：同一个类中，方法名相同，**参数列表不同**（参数类型、个数、顺序不同）。

```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public double add(double a, double b) { // 参数类型不同
        return a + b;
    }
    
    public int add(int a, int b, int c) { // 参数个数不同
        return a + b + c;
    }
}
```

**特点**：
- 发生在**同一个类**中
- 方法名相同，参数列表不同
- 返回值可以不同
- 与返回值类型无关（只看方法名和参数列表
- 编译期确定（编译时多态

### 2. 重写（Override）

**定义**：子类对父类的方法进行重新实现，方法名、参数列表、返回值类型必须相同。

```java
class Animal {
    public void eat() {
        System.out.println("动物吃东西");
    }
}

class Cat extends Animal {
    @Override
    public void eat() { // 重写父类方法
        System.out.println("猫吃鱼");
    }
}
```

**重写的规则**：
- 方法名、参数列表、返回值类型必须相同（协变返回类型除外）
- 访问权限**不能比父类更严格
- 不能抛出比父类更宽泛的异常
- 父类方法不能是 final、static 的方法不能被重写
- 运行期确定（运行时多态）

### 3. 对比总结

| 特性 | 重载（Overload） | 重写（Override） |
|------|----------------|-----------------|
| 发生位置 | 同一个类 | 父子类之间 |
| 方法名 | 相同 | 相同 |
| 参数列表 | 必须不同 | 必须相同 |
| 返回值 | 可以不同 | 必须相同（或协变） |
| 多态类型 | 编译时多态 | 运行时多态 |
| 调用时机 | 编译期确定 | 运行期确定 |

**答案解析**:

重载和重写是Java多态的两种表现形式。重载是编译时多态，在编译期就能确定调用哪个方法；重写是运行时多态，在运行时根据对象的实际类型确定调用哪个方法。

重写是面向对象编程的核心特性之一，体现了"一个接口，多个实现的设计思想。

注意：方法重载看的是参数列表，与返回值无关。只有返回值不同不能构成重载。

**扩展问题**:
- 构造方法可以重载吗？可以重写吗？
- 静态方法可以重写吗？为什么？
- 什么是多态？多态的前提条件是什么？
- 方法重载的匹配优先级是什么？
- 私有方法可以被重写吗？

---

## Q9: Java 的基本数据类型和包装类

**考察点**: 8种基本数据类型、包装类、自动装箱拆箱、缓存机制

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 八种基本数据类型

| 类型 | 字节数 | 位数 | 默认值 | 包装类 | 取值范围 |
|------|--------|------|--------|--------|---------|
| byte | 1 | 8 | 0 | Byte | -128 ~ 127 |
| short | 2 | 16 | 0 | Short | -32768 ~ 32767 |
| int | 4 | 32 | 0 | Integer | -2^31 ~ 2^31-1 |
| long | 8 | 64 | 0L | Long | -2^63 ~ 2^63-1 |
| float | 4 | 32 | 0.0f | Float | -3.403E38 ~ 3.403E38 |
| double | 8 | 64 | 0.0d | Double | -1.798E308 ~ 1.798E308 |
| char | 2 | 16 | '\u0000' | Character | 0 ~ 65535 |
| boolean | 1 | 1 | false | Boolean | true/false |

### 2. 包装类的作用

- 基本数据类型不是对象，包装类让基本类型具有对象的特性
- 集合（如 ArrayList）只能存对象，需要包装类
- 包装类提供了很多实用方法（如类型转换）

### 3. 自动装箱和拆箱

**自动装箱**：基本类型 → 包装类
```java
Integer i = 10; // 自动装箱，相当于 Integer i = Integer.valueOf(10);
```

**自动拆箱**：包装类 → 基本类型
```java
int a = i; // 自动拆箱，相当于 int a = i.intValue();
```

### 4. 包装类的缓存机制

Integer、Short、Byte、Character、Long 都有缓存机制：

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b); // true，缓存范围内

Integer c = 128;
Integer d = 128;
System.out.println(c == d); // false，超出缓存范围
```

Integer 缓存范围：**-128 ~ 127**（可通过 JVM 参数调整上限。

**答案解析**:

基本数据类型和包装类是Java的基础知识点。包装类的设计体现了Java面向对象的特性，但为了性能考虑，保留了基本数据类型。

自动装箱和拆箱是语法糖，底层调用的是 valueOf() 和 xxxValue() 方法。

缓存机制是面试常考点：Integer 缓存了 -128 到 127 之间的整数，所以在这个范围内用 == 比较返回 true，超出范围返回 false。比较包装类的值应该用 equals 方法。

**扩展问题**:
- int 和 Integer 的区别？
- 自动装箱和拆箱的原理是什么？
- Integer 的缓存范围是多少？可以修改吗？
- 包装类的 valueOf() 方法和构造方法有什么区别？
- 为什么要有包装类？

---

## Q10: 什么是值传递和引用传递

**考察点**: Java参数传递机制、基本类型和引用类型的传递区别

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 基本概念

**值传递（Pass by Value）**：将实际参数值的副本传入方法，方法内对参数的修改不会影响原变量。

**引用传递（Pass by Reference）**：将实际参数的内存地址传入方法，方法内对参数的修改会影响原变量。

### 2. Java 只有值传递

**Java 中只有值传递，没有引用传递！**

#### （1）基本类型参数传递

```java
public static void change(int a) {
    a = 100;
}

public static void main(String[] args) {
    int x = 10;
    change(x);
    System.out.println(x); // 10，值没有改变
}
```

传递的是 x 的值的副本，方法内修改不影响原变量。

#### （2）引用类型参数传递

```java
public static void change(Person p) {
    p.setName("李四");
}

public static void main(String[] args) {
    Person person = new Person("张三");
    change(person);
    System.out.println(person.getName()); // 李四，对象内容改变了
}
```

**为什么内容变了？因为传递的是**引用的值（地址）的副本，两个引用指向同一个对象，通过引用修改对象内容会影响原对象。但引用本身是值传递。

再看一个例子：
```java
public static void change(Person p) {
    p = new Person("李四"); // p指向新对象
}

public static void main(String[] args) {
    Person person = new Person("张三");
    change(person);
    System.out.println(person.getName()); // 张三，原引用没变
}
```

如果是引用传递，person 应该指向新对象，但实际上没有，说明是值传递。

### 3. 总结

- Java 只有**值传递**
- 基本类型：传递值的副本，修改不影响原变量
- 引用类型：传递引用（地址）的副本，修改对象内容会影响原对象，但修改引用本身不影响原引用

**答案解析**:

这是一个经典的面试题，很多人会混淆。关键在于理解：Java 传递的是副本，无论是基本类型还是引用类型，都是值传递。

对于引用类型，传递的是引用的值（内存地址），所以方法内可以通过这个地址修改对象的内容，但不能改变原引用指向的对象。

String 作为参数传递时，因为 String 是不可变的，所以方法内修改 String 不会影响原 String，这点要特别注意。

**扩展问题**:
- String 作为参数传递，方法内修改会影响原字符串吗？为什么？
- 数组作为参数传递是值传递吗？
- 如何在方法内修改基本类型参数的值？
- C++ 有引用传递吗？和 Java 有什么不同？
- Java 为什么设计成只有值传递？

---

## Q11: 深拷贝和浅拷贝的区别

**考察点**: 对象拷贝、Cloneable接口、序列化拷贝

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 基本概念

**浅拷贝（Shallow Copy）**：
- 只复制对象本身和对象中的基本类型成员变量
- 引用类型成员变量只复制引用，不复制引用指向的对象
- 拷贝前后的对象共享同一个引用类型成员

**深拷贝（Deep Copy）**：
- 复制对象本身及所有引用类型成员变量指向的对象
- 拷贝前后的对象完全独立，互不影响

### 2. 浅拷贝示例

```java
class Address {
    String city;
    public Address(String city) {
        this.city = city;
    }
}

class Person implements Cloneable {
    String name;
    int age;
    Address address; // 引用类型
    
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone(); // 默认浅拷贝
    }
}

public class Test {
    public static void main(String[] args) throws Exception {
        Person p1 = new Person();
        p1.name = "张三";
        p1.age = 20;
        p1.address = new Address("北京");
        
        Person p2 = (Person) p1.clone();
        
        System.out.println(p1.address == p2.address); // true，同一个对象
        p2.address.city = "上海";
        System.out.println(p1.address.city); // 上海，p1也被影响了
    }
}
```

### 3. 深拷贝实现方式

#### 方式一：手动实现深拷贝

```java
@Override
protected Object clone() throws CloneNotSupportedException {
    Person p = (Person) super.clone();
    p.address = new Address(this.address.city); // 手动复制引用类型成员
    return p;
}
```

#### 方式二：序列化实现深拷贝

```java
public Person deepClone() throws Exception {
    // 序列化
    ByteArrayOutputStream bos = new ByteArrayOutputStream();
    ObjectOutputStream oos = new ObjectOutputStream(bos);
    oos.writeObject(this);
    
    // 反序列化
    ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
    ObjectInputStream ois = new ObjectInputStream(bis);
    return (Person) ois.readObject();
}
```

### 4. 对比总结

| 特性 | 浅拷贝 | 深拷贝 |
|------|--------|--------|
| 基本类型 | 复制值 | 复制值 |
| 引用类型 | 复制引用 | 复制对象 |
| 性能 | 快 | 慢 |
| 实现 | 默认clone() | 手动实现/序列化 |
| 对象间影响 | 引用成员相互影响 | 完全独立 |

**答案解析**:

浅拷贝和深拷贝的区别在于对引用类型成员变量的处理方式。浅拷贝只复制引用，深拷贝复制引用指向的对象。

Java 中的 Object.clone() 方法默认是浅拷贝。要实现深拷贝，需要重写 clone 方法，手动复制引用类型成员，或者使用序列化的方式。

Cloneable 接口是一个标记接口，没有任何方法，只是用来标记该类可以被克隆。如果不实现 Cloneable 接口调用 clone() 会抛出 CloneNotSupportedException。

**扩展问题**:
- Cloneable 接口有什么方法？为什么是标记接口还有哪些？
- 为什么不推荐使用 clone() 方法？有什么替代方案？
- 序列化实现深拷贝需要注意什么？
- 什么是拷贝构造函数？
- ArrayList 的 clone() 是深拷贝还是浅拷贝？

---

## Q12: this 和 super 的区别

**考察点**: this关键字、super关键字、构造方法调用

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. this 关键字

`this` 代表**当前对象**的引用。

**用法**：

（1）调用本类的成员变量
```java
public void setName(String name) {
    this.name = name; // this.name 是成员变量，name 是参数
}
```

（2）调用本类的成员方法
```java
public void method1() {
    this.method2(); // 调用本类方法
}
```

（3）调用本类的构造方法
```java
public Person() {
    this("张三", 20); // 调用本类其他构造方法，必须在第一行
}

public Person(String name, int age) {
    this.name = name;
    this.age = age;
}
```

（4）返回当前对象
```java
public Person getInstance() {
    return this;
}
```

### 2. super 关键字

`super` 代表**父类对象**的引用。

**用法**：

（1）调用父类的成员变量
```java
public void print() {
    System.out.println(super.name); // 父类的name
}
```

（2）调用父类的成员方法
```java
public void eat() {
    super.eat(); // 调用父类方法
    System.out.println("猫吃鱼");
}
```

（3）调用父类的构造方法
```java
public Cat() {
    super(); // 调用父类构造方法，必须在第一行
    // 子类构造方法默认第一行有super()
}
```

### 3. 对比总结

| 特性 | this | super |
|------|------|-------|
| 代表对象 | 当前对象 | 父类对象 |
| 访问成员 | 本类成员 | 父类成员 |
| 调用构造 | 本类构造 | 父类构造 |
| 本质 | 对象引用 | 父类引用 |
| 静态方法 | 不能用 | 不能用 |

### 4. 注意事项

- this() 和 super() 都必须在构造方法的第一行，所以不能同时出现
- 子类构造方法默认第一行有 super()，如果父类没有无参构造会报错
- this 和 super 都不能在静态方法中使用

**答案解析**:

this 和 super 都是对象的引用，this 指向当前对象，super 指向父类对象。它们主要用于区分同名的成员变量或方法，以及调用构造方法。

构造方法中，this() 调用本类其他构造方法，super() 调用父类构造方法。两者都必须在第一行，所以不能同时使用。

子类构造方法默认第一行有 super()，调用父类的无参构造。如果父类没有无参构造，子类必须显式调用父类的有参构造。

**扩展问题**:
- this 和 super 为什么不能在静态方法中使用？
- 构造方法中可以同时有 this() 和 super() 吗？为什么？
- 子类实例化过程是什么样的？
- 父类没有无参构造方法，子类怎么办？
- this 可以是 null 吗？

---

## Q13: Java 的访问修饰符

**考察点**: public、protected、default、private的访问权限

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

Java 有四种访问修饰符，访问权限从大到小：

### 1. 四种访问修饰符

| 修饰符 | 本类 | 同包 | 子类（不同包） | 其他包 |
|--------|------|------|-------------|--------|
| public | ✓ | ✓ | ✓ | ✓ |
| protected | ✓ | ✓ | ✓ | ✗ |
| default（默认/包访问权限） | ✓ | ✓ | ✗ | ✗ |
| private | ✓ | ✗ | ✗ | ✗ |

### 2. 详细说明

#### （1）private（私有的）

- 只能在**本类**中访问
- 修饰成员变量和成员方法
- 最严格的访问权限

```java
public class Person {
    private String name; // 私有变量
    
    private void method() { // 私有方法
        // ...
    }
}
```

#### （2）default（默认的/包访问权限）

- 不写修饰符就是 default
- 只能在**本类和同包**下访问
- 也叫包访问权限

```java
class Person { // 类也可以是default
    String name; // 默认访问权限
}
```

#### （3）protected（受保护的）

- 本类、同包、**子类（不同包也可以）**都能访问
- 主要用于继承中，让子类访问父类成员

```java
public class Person {
    protected String name;
}
```

#### （4）public（公共的）

- 任何地方都能访问
- 最宽松的访问权限

```java
public class Person {
    public String name;
}
```

### 3. 类的访问修饰符

- 外部类只能用 **public** 或 **default**
- 内部类可以用四种修饰符

**答案解析**:

访问修饰符是Java封装特性的体现，通过控制访问权限来隐藏实现细节，只暴露必要的接口。

设计原则：尽量使用最小权限原则，能 private 就 private，减少耦合。

成员变量一般都设为 private，通过 getter/setter 方法访问，这是 JavaBean 的规范。

**扩展问题**:
- 接口的成员变量和方法默认是什么访问权限？
- 抽象类的抽象方法可以是 private 吗？
- 为什么外部类不能用 private 和 protected？
- 内部类可以用 private 吗？有什么用？
- 如何理解封装和访问修饰符的关系？

---

## Q14: 什么是多态

**考察点**: 多态的概念、前提条件、向上转型、向下转型

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 多态的概念

**多态（Polymorphism）**：同一个行为具有多个不同表现形式或形态的能力。即同一个方法调用，由于对象不同可能会有不同的行为。

### 2. 多态的三个必要条件

1. **继承**：必须有继承关系（或实现接口）
2. **重写**：子类重写父类方法
3. **向上转型**：父类引用指向子类对象

```java
// 父类
class Animal {
    public void eat() {
        System.out.println("动物吃东西");
    }
}

// 子类1
class Cat extends Animal {
    @Override
    public void eat() {
        System.out.println("猫吃鱼");
    }
}

// 子类2
class Dog extends Animal {
    @Override
    public void eat() {
        System.out.println("狗吃肉");
    }
}

public class Test {
    public static void main(String[] args) {
        Animal animal1 = new Cat(); // 向上转型
        Animal animal2 = new Dog();
        
        animal1.eat(); // 猫吃鱼
        animal2.eat(); // 狗吃肉
    }
}
```

### 3. 向上转型和向下转型

**向上转型**（自动转型）：
- 父类引用指向子类对象
- 自动转换，不需要强转
- 只能调用父类方法，不能调用子类特有方法

```java
Animal animal = new Cat(); // 向上转型
animal.eat(); // 可以，父类方法
// animal.catchMouse(); // 不行，子类特有方法
```

**向下转型**（强制转型）：
- 子类引用指向父类对象（实际上是子类对象）
- 需要强转
- 可以调用子类特有方法

```java
Animal animal = new Cat();
Cat cat = (Cat) animal; // 向下转型
cat.catchMouse(); // 可以调用子类特有方法
```

**类型判断**：
```java
if (animal instanceof Cat) {
    Cat cat = (Cat) animal;
}
```

### 4. 多态的好处

- 提高代码的可扩展性
- 提高代码的可维护性
- 降低耦合度

**答案解析**:

多态是面向对象三大特性之一（封装、继承、多态）。多态的本质是：**编译看左边，运行看右边**。

编译时看父类，运行时看子类。编译时检查父类有没有这个方法，运行时执行子类重写的方法。

多态的实现机制是动态绑定（晚期绑定）：在运行时根据对象的实际类型确定调用哪个方法。

成员变量没有多态性，成员变量看的是引用类型，不是对象类型。

**扩展问题**:
- 多态的实现原理是什么？（虚方法表）
- 静态方法有多态吗？为什么？
- 成员变量有多态吗？为什么？
- 构造方法中调用重写方法会怎么样？
- 什么是动态绑定和静态绑定？

---

## Q15: 什么是内部类，有哪几种

**考察点**: 内部类的分类和特点

**难度**: 中等

**频率**: ⭐⭐⭐

**标准答案**:

**内部类（Inner Class）**：定义在另一个类内部的类。

### 1. 成员内部类

定义在类的成员位置。

```java
public class Outer {
    private int num = 10;
    
    // 成员内部类
    class Inner {
        public void method() {
            System.out.println(num); // 可以访问外部类的私有成员
        }
    }
}

// 使用方式
Outer outer = new Outer();
Outer.Inner inner = outer.new Inner();
inner.method();
```

特点：
- 可以访问外部类的所有成员（包括私有）
- 不能定义静态成员（除了静态常量）
- 依赖外部类对象

### 2. 静态内部类

用 static 修饰的内部类。

```java
public class Outer {
    private static int num = 10;
    
    // 静态内部类
    static class Inner {
        public void method() {
            System.out.println(num); // 只能访问外部类的静态成员
        }
    }
}

// 使用方式
Outer.Inner inner = new Outer.Inner(); // 不需要外部类对象
inner.method();
```

特点：
- 不依赖外部类对象
- 只能访问外部类的静态成员
- 可以定义静态成员

### 3. 局部内部类

定义在方法内部的类。

```java
public class Outer {
    public void method() {
        final int a = 10; // JDK8  final可以不写，但实际上是final的
        
        // 局部内部类
        class Inner {
            public void print() {
                System.out.println(a); // 只能访问final的局部变量
            }
        }
        
        Inner inner = new Inner();
        inner.print();
    }
}
```

特点：
- 只在方法内部可见
- 只能访问 final 的局部变量（JDK8 隐式 final）
- 不能有访问修饰符

### 4. 匿名内部类

没有名字的内部类，通常用来简化代码。

```java
public class Test {
    public static void main(String[] args) {
        // 匿名内部类
        new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("匿名内部类");
            }
        }).start();
    }
}
```

特点：
- 没有类名
- 必须继承一个类或实现一个接口
- 只能使用一次
- 不能定义构造方法

**答案解析**:

内部类是Java中一个比较重要但容易被忽略的知识点。四种内部类各有特点：

成员内部类和静态内部类的区别在于是否依赖外部类对象。成员内部类持有外部类的引用（Outer.this），所以可以访问外部类的所有成员。

局部内部类和匿名内部类都只能访问 final 的局部变量，这是因为生命周期的问题：局部变量在方法结束后就销毁了，而内部类对象可能还活着，所以内部类持有局部变量的副本，为了保证数据一致性，局部变量必须是 final 的。

**扩展问题**:
- 为什么局部内部类访问局部变量为什么必须是 final 的？
- 成员内部类和静态内部类的区别？
- 匿名内部类有什么应用场景？
- 内部类和外部类的访问权限有什么特点？
- 内部类生成的 class 文件名字是什么样的？

---

## Q16: 异常体系（Error 和 Exception，受检异常和非受检异常）

**考察点**: Java异常体系结构、Error和Exception的区别、受检异常和非受检异常

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 异常体系结构

```
Throwable
├── Error（错误）
│   ├── StackOverflowError
│   ├── OutOfMemoryError
│   └── ...
└── Exception（异常）
    ├── RuntimeException（运行时异常/非受检异常）
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ClassCastException
    │   └── ...
    └── 其他Exception（受检异常）
        ├── IOException
        ├── SQLException
        └── ...
```

### 2. Error 和 Exception 的区别

**Error**：
- 系统级别的错误，程序无法处理
- 一般是 JVM 抛出的，如 StackOverflowError、OutOfMemoryError
- 不需要捕获，捕获了也无法恢复

**Exception**：
- 程序级别的异常，可以处理
- 分为运行时异常和受检异常
- 可以通过 try-catch 捕获处理

### 3. 受检异常和非受检异常

**受检异常（Checked Exception）**：
- 编译时必须处理（捕获或抛出）
- 除了 RuntimeException 及其子类都是受检异常
- 如 IOException、SQLException、FileNotFoundException

```java
// 必须处理，否则编译不通过
public void method() throws IOException {
    FileInputStream fis = new FileInputStream("test.txt");
}
```

**非受检异常（Unchecked Exception / RuntimeException）**：
- 编译时不要求处理
- RuntimeException 及其子类
- 如 NullPointerException、ArrayIndexOutOfBoundsException、ClassCastException

```java
// 可以不处理，编译能通过，但运行时可能抛出
public void method() {
    String s = null;
    s.length(); // NullPointerException
}
```

### 4. 常见异常

**RuntimeException 子类**：
- NullPointerException：空指针异常
- ArrayIndexOutOfBoundsException：数组下标越界
- ClassCastException：类型转换异常
- IllegalArgumentException：非法参数异常
- ArithmeticException：算术异常（除零）
- NumberFormatException：数字格式异常

**受检异常**：
- IOException：IO异常
- SQLException：SQL异常
- FileNotFoundException：文件不存在
- ClassNotFoundException：类找不到

**答案解析**:

异常体系是Java中处理错误的机制。Throwable 是所有异常和错误的父类。

Error 是系统级错误，程序无法处理；Exception 是程序级异常，可以处理。

受检异常和非受检异常的区别在于编译时是否要求处理。受检异常必须在编译时处理（try-catch或throws），非受检异常不要求。

设计受检异常的目的是强制开发者处理可能发生的异常，提高程序的健壮性。但过度使用受检异常会导致代码繁琐。

**扩展问题**:
- 运行时异常和受检异常的区别？
- 常见的运行时异常有哪些？
- 异常处理的方式有哪些？
- throw 和 throws 的区别？
- 为什么说受检异常是Java的一个糟糕设计？

---

## Q17: try-catch-finally 执行顺序

**考察点**: 异常处理流程、finally的执行时机、return对finally的影响

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 基本执行顺序

```java
try {
    // 可能出现异常的代码
} catch (Exception e) {
    // 捕获异常，处理异常
} finally {
    // 无论是否发生异常，都会执行
}
```

**执行流程**：
1. 先执行 try 块中的代码
2. 如果没有异常，跳过 catch，执行 finally
3. 如果有异常，匹配 catch，执行 finally
4. finally 总是执行（除非 JVM 退出）

### 2. finally 中的 return

```java
public static int test() {
    int a = 10;
    try {
        return a;
    } catch (Exception e) {
        a = 20;
        return a;
    } finally {
        a = 30;
        // return a; // 不建议在finally中return
    }
}
// 返回 10
```

**解析**：
- try 中的 return 会先把返回值保存起来
- 然后执行 finally
- finally 修改的是局部变量，不影响已经保存的返回值
- 如果 finally 中有 return，会覆盖 try 中的 return

### 3. finally 不执行的情况

```java
try {
    System.out.println("try");
    System.exit(0); // JVM退出
} finally {
    System.out.println("finally"); // 不会执行
}
```

只有一种情况 finally 不执行：**调用 System.exit(0) 退出 JVM。

### 4. 多个 catch 块

```java
try {
    // ...
} catch (NullPointerException e) {
    // 先匹配子类异常
} catch (Exception e) {
    // 后匹配父类异常
} finally {
    // ...
}
```

**注意**：
- 多个 catch 块，**子类在前，父类在后
- 只会执行第一个匹配的 catch

**答案解析**:

try-catch-finally 是Java异常处理的基本结构。finally 块的特点是无论是否发生异常都会执行，通常用来释放资源（关闭流、关闭数据库连接等）。

关于 finally 和 return 的关系是面试常考点：
1. try 中 return 时，会先把返回值暂存起来
2. 然后执行 finally
3. 最后返回暂存的值
4. 如果 finally 中也有 return，会覆盖 try 中的 return

不建议在 finally 中写 return，会导致逻辑混乱。

**扩展问题**:
- finally 中的代码一定会执行吗？什么情况下不执行？
- try 中有 return，finally 还执行吗？在 return 前还是后？
- finally 中修改返回值会影响结果吗？
- try-catch-finally 中，catch 里有 return，finally 还执行吗？
- 为什么不建议在 finally 中写 return？

---

## Q18: final、finally、finalize 的区别

**考察点**: 三个相似名称的不同含义和用途

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

这三个是完全不同的概念，只是名字相似。

### 1. final

**修饰符**，可以修饰类、方法、变量。

- 修饰类：类不能被继承
- 修饰方法：方法不能被重写
- 修饰变量：变量只能赋值一次，是常量

```java
final int a = 10; // final变量
final class A {} // final类
final void method() {} // final方法
```

### 2. finally

**异常处理的一部分**，总是执行。

```java
try {
    // 可能异常的代码
} catch (Exception e) {
    // 处理异常
} finally {
    // 总是执行，释放资源
}
```

### 3. finalize

**Object 类的一个方法**，在垃圾回收前调用。

```java
@Override
protected void finalize() throws Throwable {
    // 对象被回收前调用
    super.finalize();
}
```

特点：
- 每个对象只能被调用一次
- 不保证一定执行（JVM可能不执行GC）
- 不推荐使用，JDK9 已废弃

**答案解析**:

这三个名字相似但完全不同：
- final 是修饰符，用于限制
- finally 是异常处理的一部分，用于保证代码一定执行
- finalize 是 Object 类的方法，用于垃圾回收前的清理

finalize 方法已经不推荐使用了，因为它执行时间不确定，甚至可能不执行，而且会影响GC效率。资源释放推荐使用 try-with-resources。

**扩展问题**:
- finalize() 方法为什么被废弃？
- 如何正确释放资源？
- finally 和 try-with-resources 的区别？
- finalize() 方法的执行过程是什么样的？
- 一个对象的 finalize 被调用后一定会被回收吗？

---

## Q19: Java 反射机制及应用场景

**考察点**: 反射的概念、原理、常用API、应用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

### 1. 什么是反射

**反射（Reflection）**：在运行状态中，对于任意一个类，都能够知道这个类的所有属性和方法；对于任意一个对象，都能够调用它的任意方法和属性。这种动态获取信息以及动态调用对象方法的功能称为Java语言的反射机制。

### 2. 获取 Class 对象的三种方式

```java
// 方式1：类名.class
Class<?> clazz1 = String.class;

// 方式2：对象.getClass()
String s = "hello";
Class<?> clazz2 = s.getClass();

// 方式3：Class.forName("全类名")
Class<?> clazz3 = Class.forName("java.lang.String");
```

### 3. 反射的常用操作

#### （1）获取构造方法并创建对象

```java
Class<?> clazz = Person.class;

// 获取无参构造
Constructor<?> constructor = clazz.getConstructor();
Object obj = constructor.newInstance();

// 获取有参构造
Constructor<?> constructor2 = clazz.getConstructor(String.class, int.class);
Object obj2 = constructor2.newInstance("张三", 20);
```

#### （2）获取并操作成员变量

```java
Field nameField = clazz.getDeclaredField("name");
nameField.setAccessible(true); // 暴力反射，访问私有
nameField.set(obj, "李四"); // 设置值
String name = (String) nameField.get(obj); // 获取值
```

#### （3）获取并调用方法

```java
Method method = clazz.getMethod("setName", String.class);
method.invoke(obj, "王五"); // 调用方法
```

### 4. 反射的应用场景

1. **Spring 等框架**：IOC 容器、依赖注入、AOP
2. **JDBC**：加载驱动 `Class.forName("com.mysql.cj.jdbc.Driver")
3. **注解**：注解解析
4. **动态代理**：JDK 动态代理
5. **序列化/反序列化**：JSON 解析（Jackson、Gson）
6. **单元测试**：JUnit
7. **热部署**：运行时加载类

### 5. 反射的优缺点

**优点**：
- 动态性，运行时确定类和方法
- 提高代码灵活性和扩展性

**缺点**：
- 性能差，比直接调用慢很多
- 破坏封装性，可以访问私有成员
- 安全性问题，类型安全检查在编译期无法进行

**答案解析**:

反射是Java的一个高级特性，也是很多框架的基础。Spring 的 IOC、AOP 都用到了反射。

反射的原理是：类加载时会在方法区生成一个 Class 对象，包含类的所有信息。反射就是通过这个 Class 对象来获取类的信息并操作。

`Class.forName() 会触发类加载并执行静态代码块。`.class 不会触发初始化。getField() 和 getDeclaredField() 的区别：前者只能获取 public 的，后者可以获取所有声明的（包括私有），但不能获取父类的。

反射性能差的原因：需要动态解析、安全检查、方法调用开销大等。

**扩展问题**:
- 反射为什么慢？如何优化反射性能？
- Class.forName() 和类名.class 的区别？
- getField() 和 getDeclaredField() 的区别？
- 什么是暴力反射？
- 反射和面向对象的封装性矛盾吗？

---

## Q20: 注解的原理和自定义注解

**考察点**: 注解的概念、元注解、自定义注解、注解解析

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

### 1. 什么是注解

**注解（Annotation）**：Java 代码中的特殊标记，可以在编译、类加载、运行时被读取，并执行相应的处理。

注解不影响程序逻辑，只是提供信息。

### 2. 元注解

元注解是用来修饰注解的注解，有四个：

#### （1）@Target

指定注解可以用在什么地方：
- ElementType.TYPE：类、接口
- ElementType.FIELD：成员变量
- ElementType.METHOD：方法
- ElementType.PARAMETER：参数
- ElementType.CONSTRUCTOR：构造方法
- ElementType.LOCAL_VARIABLE：局部变量

#### （2）@Retention

指定注解的生命周期：
- RetentionPolicy.SOURCE：源码阶段，编译时丢弃
- RetentionPolicy.CLASS：类加载阶段，类加载时丢弃（默认）
- RetentionPolicy.RUNTIME：运行时保留，可以反射读取

#### （3）@Documented

指定注解是否生成在 javadoc 中。

#### （4）@Inherited

指定注解是否可以被子类继承。

### 3. 自定义注解

```java
// 自定义注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface MyAnnotation {
    // 属性
    String value() default "";
    int count() default 0;
    String[] names() default {};
}
```

**使用自定义注解**：
```java
public class Test {
    @MyAnnotation(value = "test", count = 5)
    public void method() {
        // ...
    }
}
```

### 4. 注解解析

通过反射读取注解信息：

```java
public class AnnotationParser {
    public static void main(String[] args) throws Exception {
        Class<?> clazz = Test.class;
        Method method = clazz.getMethod("method");
        
        if (method.isAnnotationPresent(MyAnnotation.class)) {
            MyAnnotation annotation = method.getAnnotation(MyAnnotation.class);
            System.out.println(annotation.value());
            System.out.println(annotation.count());
        }
    }
}
```

### 5. 注解的应用场景

1. **Spring 框架**：@Autowired、@Service、@Controller 等
2. **JUnit**：@Test
3. **ButterKnife**：@BindView
4. **自定义注解 + AOP**：实现日志、权限校验等
5. **编译期检查**：@Override、@Deprecated、@SuppressWarnings

**答案解析**:

注解是Java 5引入的重要特性，它本质上是一种标记，可以给代码添加元数据。注解本身不影响代码执行，需要通过解析器来读取和处理。

元注解有四个：@Target、@Retention、@Documented、@Inherited。其中最常用的是前两个。

自定义注解的语法和接口很像，用 @interface 定义，属性看起来像方法。属性类型只能是基本类型、String、枚举、注解、Class、以上类型的数组。

注解的解析是通过反射实现的，所以自定义注解一般要设置 @Retention(RetentionPolicy.RUNTIME)。

Spring 中大量使用了注解，比如 @Component、@Autowired、@RequestMapping 等，都是通过反射读取注解信息来实现功能的。

**扩展问题**:
- 注解的本质是什么？
- 元注解有哪些？各有什么作用？
- @Retention 三个阶段的区别？
- 注解和注释的区别？
- 如何实现一个自定义注解 + AOP 的日志功能？

---

## Reference

1. Oracle. *The Java™ Tutorials - Object-Oriented Programming Concepts*. https://docs.oracle.com/javase/tutorial/java/concepts/, 访问时间：2026-07-28
2. 周志明. *深入理解Java虚拟机：JVM高级特性与最佳实践（第3版）*. 机械工业出版社, 2019
3. 牛客网. *Java面试题精选*. https://www.nowcoder.com, 访问时间：2026-07-28
4. 阿里巴巴. *阿里巴巴Java开发手册（嵩山版）*. 电子工业出版社, 2020
5. Cay S. Horstmann. *Java核心技术卷I：基础知识（原书第11版）*. 机械工业出版社, 2020

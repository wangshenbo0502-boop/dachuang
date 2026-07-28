---
title: Python后端开发工程师面试题
type: interview_questions
role: Python后端开发工程师
version: "2026.07"
---

# Python后端开发工程师面试题

## 技术考察重点

- Python 基础语法与数据结构
- 内存管理与垃圾回收机制
- 并发编程（多线程/多进程/协程/GIL）
- 装饰器与闭包
- Django / FastAPI 框架原理
- ORM 与数据库优化
- 高级特性（迭代器/生成器/上下文管理器）
- 常用设计模式与最佳实践

## 高频面试题

### Q1: Python 的 GIL 是什么？对多线程有什么影响？CPU 密集型和 IO 密集型怎么选？

- **类别**: 并发编程
- **难度**: 中等
- **频率**: 极高

<details>
<summary>答题要点</summary>

**GIL（全局解释器锁）**：
- CPython 解释器中的一把互斥锁，确保同一时刻只有一个线程执行 Python 字节码
- 设计初衷：简化内存管理，避免多线程下引用计数的线程安全问题
- GIL 是 CPython 的特性，Jython、PyPy 等没有 GIL

**对多线程的影响**：
- **CPU 密集型**：多线程无法利用多核，因为 GIL 导致同一时刻只有一个线程在跑 CPU，线程切换还有开销，反而比单线程慢
- **IO 密集型**：多线程有效果，因为 IO 等待时 GIL 会被释放，其他线程可以执行

**CPU 密集型 vs IO 密集型选型**：

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| CPU 密集型 | 多进程（multiprocessing） | 每个进程有独立的 GIL，能利用多核 |
| IO 密集型 | 多线程 / 协程（asyncio） | IO 等待时 GIL 释放，协程开销更小 |

**GIL 释放时机**：
- 遇到 IO 操作（文件读写、网络请求）时主动释放
- 计时轮询：Python 3.2+ 每 15ms 检查一次，当前线程主动让出 GIL
- 遇到 `time.sleep()` 也会释放

**怎么绕过 GIL**：
- 用多进程（multiprocessing）
- C 扩展：在 C 代码中释放 GIL（如 NumPy、Cython）
- 使用 PyPy / Jython 等无 GIL 解释器

</details>

---

### Q2: 装饰器原理和实现？带参数的装饰器？类装饰器？

- **类别**: Python高级特性
- **难度**: 中等
- **频率**: 极高

<details>
<summary>答题要点</summary>

**装饰器原理**：
- 本质是一个高阶函数，接收被装饰的函数作为参数，返回一个包装后的新函数
- 利用 Python 函数是一等公民的特性
- 语法糖 `@decorator` 等价于 `func = decorator(func)`

**简单装饰器**：
```python
def decorator(func):
    def wrapper(*args, **kwargs):
        # 前置操作
        result = func(*args, **kwargs)
        # 后置操作
        return result
    return wrapper
```

**带参数的装饰器**：
- 实际上是"装饰器工厂"，先接收参数返回真正的装饰器，再装饰函数
- `@decorator(arg)` 等价于 `func = decorator(arg)(func)`

```python
def decorator(arg):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            # 使用 arg
            return func(*args, **kwargs)
        return wrapper
    return real_decorator
```

**类装饰器**：
- 类实现 `__call__` 方法，实例可以像函数一样被调用
- `@ClassDecorator` 等价于 `func = ClassDecorator(func)`

```python
class Decorator:
    def __init__(self, func):
        self.func = func
    def __call__(self, *args, **kwargs):
        # 前置操作
        result = self.func(*args, **kwargs)
        # 后置操作
        return result
```

**functools.wraps**：
- 装饰器会丢失原函数的元信息（函数名、文档字符串等）
- 用 `@functools.wraps(func)` 装饰 wrapper，保留原函数元信息

**常见应用场景**：日志记录、性能统计、权限校验、缓存、重试机制。

</details>

---

### Q3: 列表和元组的区别？底层实现？

- **类别**: 数据结构
- **难度**: 简单
- **频率**: 极高

<details>
<summary>答题要点</summary>

**主要区别**：

| 对比维度 | list（列表） | tuple（元组） |
|---------|-------------|--------------|
| 可变性 | 可变（增删改） | 不可变 |
| 语法 | `[]` | `()` |
| 内存占用 | 较大（预留空间） | 较小（固定大小） |
| 性能 | 稍慢 | 稍快 |
| 哈希 | 不可哈希（不能做 dict key） | 可哈希（元素都可哈希时） |
| 适用场景 | 动态数据集合 | 固定数据、函数多返回值、字典键 |

**底层实现**：
- 都是连续存储的数组结构（CPython 中是 PyObject* 数组）
- list 是动态数组，有容量机制，扩容时重新分配内存
- tuple 是固定大小数组，创建后不可变，内存直接确定

**list 扩容机制**：
- 当 append 导致元素数超过容量时触发扩容
- 扩容公式：`new_allocated = (size_t)newsize + (newsize >> 3) + (newsize < 9 ? 3 : 6)`
- 大约扩容 1.125 倍（加上少量常数）

**tuple 的优势**：
- 不可变，线程安全
- 可以作为字典的 key
- Python 会缓存小的 tuple（小整数池类似），创建更快
- 支持拆包：`a, b = (1, 2)`

**注意**：tuple 的不可变是指引用不可变，如果 tuple 里有 list 等可变对象，list 的内容还是可以变的。

</details>

---

### Q4: 字典底层实现？Python 3.7+ 字典有序是怎么实现的？

- **类别**: 数据结构
- **难度**: 较难
- **频率**: 高

<details>
<summary>答题要点</summary>

**底层结构（哈希表）**：
- Python dict 基于哈希表实现，平均 O(1) 的查找/插入/删除

**Python 3.6 之前**：
- 直接用哈希表存储 entry（hash + key + value）
- 内存不紧凑，浪费空间
- 无序（插入顺序不保留）

**Python 3.6+ 新实现**：
- 两个数组：`indices`（哈希索引数组）+ `entries`（实际存储数组）
- `indices` 存 entry 在 entries 中的索引
- `entries` 按插入顺序存储键值对，紧凑排列

```
indices:  [None, 1, None, 0, None, 2, None]  (哈希映射)
entries:  [(h0, k0, v0), (h1, k1, v1), (h2, k2, v2)]  (按插入顺序)
```

**为什么有序**：entries 数组按插入顺序排列，遍历时按 entries 顺序输出，所以保留插入顺序。

**优势**：
- 更节省内存（entries 紧凑，没有空槽）
- 遍历更快（按 entries 顺序遍历，不用跳空槽）
- 保留插入顺序（3.7 正式成为语言规范）

**哈希冲突解决**：开放寻址法（探测序列），不是链地址法。

**扩容机制**：
- 装载因子超过 2/3 时扩容为原来的 2 倍
- 扩容后重新哈希所有元素

**Python 3.11 优化**：进一步优化了字典的内存布局和哈希表性能。

</details>

---

### Q5: Python 的垃圾回收机制？引用计数 + 标记清除 + 分代回收？

- **类别**: 内存管理
- **难度**: 较难
- **频率**: 极高

<details>
<summary>答题要点</summary>

Python GC 采用**引用计数为主，标记-清除和分代回收为辅**的策略。

**1. 引用计数（Reference Counting）**：
- 每个对象维护一个 `ob_refcnt` 引用计数
- 引用 +1：对象被赋值、作为参数传入、放入容器等
- 引用 -1：del 删除、离开作用域、从容器移除等
- 引用计数为 0 时，对象立即被回收
- 优点：实时性高，实现简单
- 缺点：循环引用无法回收，每次加减计数有开销

**2. 标记-清除（Mark-Sweep）**：
- 解决循环引用问题
- 只关注容器对象（list、dict、tuple、实例等），因为只有它们可能产生循环引用
- 从根对象（全局变量、栈上引用）出发，标记所有可达对象
- 清除阶段：遍历所有容器对象，未标记的就是垃圾，回收
- 过程中需要 STW（Stop The World）

**3. 分代回收（Generational GC）**：
- 基于"弱分代假说"：大多数对象生命周期很短
- 分三代：0 代（年轻代）、1 代（中年代）、2 代（老年代）
- 对象创建后放在 0 代，经历一次 GC 存活后升到下一代
- 代越年轻，GC 越频繁；代越老，GC 越少
- 触发条件：每代对象数达到阈值时触发对应代的 GC
  - 0 代：700 个对象触发 0 代 GC
  - 1 代：0 代 GC 10 次后触发 1 代 GC
  - 2 代：1 代 GC 10 次后触发 2 代 GC

**gc 模块**：
- `gc.enable()` / `gc.disable()` 开关
- `gc.collect()` 手动触发
- `gc.get_threshold()` 查看各代阈值

**del 关键字**：只是减少引用计数，不一定立即回收（除非引用计数归零）。

</details>

---

### Q6: 迭代器和生成器的区别？yield 原理？

- **类别**: Python高级特性
- **难度**: 中等
- **频率**: 高

<details>
<summary>答题要点</summary>

**迭代器（Iterator）**：
- 实现了 `__iter__()` 和 `__next__()` 方法的对象
- `__iter__()` 返回自身
- `__next__()` 返回下一个元素，没有了抛出 `StopIteration`
- 只能迭代一次，用完即止
- 惰性计算，节省内存

**可迭代对象（Iterable）**：
- 实现了 `__iter__()` 方法的对象（list、dict、tuple 等）
- `iter()` 函数可以把它转为迭代器

**生成器（Generator）**：
- 是一种特殊的迭代器，写法更简洁
- 两种创建方式：
  1. 生成器函数：函数中用 `yield` 关键字
  2. 生成器表达式：`(x for x in range(10))`

**yield 原理**：
- 函数执行到 `yield` 时暂停，返回值给调用者，并保存当前执行状态
- 下次调用 `next()` 时，从暂停位置继续执行
- 函数结束或遇到 `return` 时抛出 `StopIteration`
- 本质：生成器对象维护了一个帧对象（frame），保存了代码位置和局部变量

**yield from**：
- Python 3.3 引入
- 可以委托另一个生成器，自动处理迭代和异常传递
- `yield from gen` 等价于 `for item in gen: yield item`（但还能传递值和异常）

**生成器的优势**：
- 惰性求值，大数据量下节省内存
- 代码简洁，可读性好
- 协程的基础（asyncio 底层基于生成器 + yield from）

</details>

---

### Q7: *args 和 **kwargs 的用法？

- **类别**: Python基础
- **难度**: 简单
- **频率**: 高

<details>
<summary>答题要点</summary>

**`*args`**：
- 收集所有位置参数为一个元组（tuple）
- args 只是约定名，可以改成其他名字
- 用于不确定参数个数的函数

```python
def func(*args):
    print(args)  # 元组

func(1, 2, 3)  # (1, 2, 3)
```

**`**kwargs`**：
- 收集所有关键字参数为一个字典（dict）
- kwargs 也是约定名
- 用于不确定关键字参数的函数

```python
def func(**kwargs):
    print(kwargs)  # 字典

func(a=1, b=2)  # {'a': 1, 'b': 2}
```

**组合使用**：
```python
def func(*args, **kwargs):
    # args 收集位置参数，kwargs 收集关键字参数
    pass
```

**解包用法**：
- `*` 可以解包列表/元组为位置参数
- `**` 可以解包字典为关键字参数

```python
args = [1, 2, 3]
kwargs = {'a': 1, 'b': 2}
func(*args, **kwargs)  # 等价于 func(1, 2, 3, a=1, b=2)
```

**参数顺序**（从左到右）：
位置参数 → `*args` → 默认参数 → `**kwargs`

```python
def func(a, b, *args, c=1, **kwargs):
    pass
```

**常见应用**：装饰器中透传参数、调用可变参数的函数、子类调用父类构造方法。

</details>

---

### Q8: Python 的内存管理？小整数池、字符串驻留？

- **类别**: 内存管理
- **难度**: 中等
- **频率**: 高

<details>
<summary>答题要点</summary>

**内存管理机制**：
- 内存池（PyMalloc）：小内存（< 512 字节）用内存池分配，减少系统调用
- 大内存：直接用 malloc/free
- 垃圾回收：引用计数 + 标记清除 + 分代回收

**小整数池（Small Integer Caching）**：
- CPython 缓存了 -5 到 256 之间的整数
- 这些整数对象在解释器启动时就创建好了，全局共享
- 范围内的相同整数是同一个对象，`is` 比较返回 True
- 超过范围的整数每次都是新对象

```python
a = 256
b = 256
a is b  # True

c = 257
d = 257
c is d  # False（交互式下，脚本模式可能被优化为同一个）
```

**字符串驻留（String Interning）**：
- 相同的字符串字面量只存一份，节省内存
- 驻留条件（一般情况）：
  - 只包含字母、数字、下划线的字符串
  - 编译期确定的字符串字面量
  - 长度为 0 或 1 的字符串
- `sys.intern()` 可以手动驻留任意字符串

```python
a = 'hello'
b = 'hello'
a is b  # True

c = 'hello!'
d = 'hello!'
c is d  # 可能 False（含特殊字符，不驻留）
```

**注意**：`is` 比较的是对象身份（内存地址），`==` 比较的是值是否相等。日常比较字符串和数字用 `==`，不要用 `is`。

**内存池分层**：
- arena（256KB）→ pool（4KB）→ block（大小不一，8 的倍数）
- 小对象从内存池中分配，减少碎片

</details>

---

### Q9: Django 和 Flask/FastAPI 的区别？FastAPI 为什么快？

- **类别**: Web框架
- **难度**: 中等
- **频率**: 极高

<details>
<summary>答题要点</summary>

**框架对比**：

| 对比维度 | Django | Flask | FastAPI |
|---------|--------|-------|---------|
| 类型 | 全栈框架（大而全） | 微框架（轻量） | 异步高性能框架 |
| 特点 | 自带 ORM、Admin、Form、Auth | 核心简单，插件丰富 | 类型提示、自动文档、异步原生支持 |
| 适用 | 中大型项目、快速开发 | 小型项目、灵活定制 | 高并发 API、微服务 |
| 异步 | Django 3.1+ 支持异步视图 | 不原生支持 | 原生 async/await |
| 性能 | 中等 | 中等 | 高性能（接近 Node/Go） |

**Django 特点**：
- MTV 架构（Model-Template-View）
- Django ORM：强大的对象关系映射
- Django Admin：自动生成后台管理
- 自带认证、权限、Session、CSRF 防护
- 约定优于配置

**Flask 特点**：
- 微核心，只提供路由、模板、请求响应
- 扩展丰富：Flask-SQLAlchemy、Flask-Login 等
- 灵活度高，按需组装
- 适合快速原型和小项目

**FastAPI 为什么快**：
1. **异步支持**：原生基于 asyncio，Starlette 框架，ASGI 接口，高并发 IO 密集型场景性能好
2. **类型提示驱动**：基于 Python 类型提示（type hints），Pydantic 做数据校验，高效
3. **Starlette 高性能**：底层是 Starlette（ASGI 框架），Uvicorn 做 ASGI 服务器
4. **Pydantic 数据验证**：用 C 扩展（pydantic-core 用 Rust 写的），验证速度快
5. **自动生成文档**：基于 OpenAPI/Swagger UI，开发效率高
6. **并发模型**：async/await 协程，比线程开销小得多

**性能对比**：FastAPI > Flask ≈ Django（同步模式），但具体取决于场景和数据库瓶颈。

</details>

---

### Q10: Django 的 ORM 原理？N+1 问题怎么解决？

- **类别**: Django
- **难度**: 中等
- **频率**: 高

<details>
<summary>答题要点</summary>

**ORM 原理**：
- 模型类映射数据库表，类属性映射字段，实例映射行
- 底层基于 `QuerySet`，惰性求值（不真正执行 SQL，直到需要数据时才查询）
- 支持链式调用：`filter().exclude().order_by()`，每次返回新的 QuerySet
- 执行时机：迭代、切片（步长）、len()、list()、bool 判断等

**QuerySet 底层**：
- 每个 QuerySet 维护一个 query 对象，保存 SQL 构建信息
- 实际查询时调用数据库游标执行 SQL，结果转为模型实例

**N+1 问题**：
- 查询一个列表（1 次 SQL），然后遍历每条记录访问关联对象，每条又触发 1 次 SQL
- 总共 1 + N 次查询，性能差

**解决 N+1 问题**：

1. **select_related**（一对多的一、一对一）：
   - JOIN 查询，一次 SQL 把关联对象查出来
   - 只支持外键和一对一关系（正向）
   ```python
   Book.objects.select_related('publisher').all()
   ```

2. **prefetch_related**（多对多、反向一对多）：
   - 分两次查询，第一次查主表，第二次用 IN 查询关联表，Python 中组装
   - 支持多对多、反向一对多
   ```python
   Book.objects.prefetch_related('authors').all()
   ```

3. **only / defer**：
   - only：只查指定字段
   - defer：排除指定字段
   - 减少数据传输量

4. **values / values_list**：
   - 返回字典或元组，不转模型实例，性能更好
   - 适合只需要少量字段的场景

5. **annotate / aggregate**：
   - 聚合查询，在 SQL 层完成计算，避免 Python 层循环

</details>

---

### Q11: Python 深拷贝和浅拷贝的区别？

- **类别**: Python基础
- **难度**: 简单
- **频率**: 高

<details>
<summary>答题要点</summary>

**赋值（=）**：
- 只是创建新的引用，指向同一个对象
- 修改一个会影响另一个

**浅拷贝（shallow copy）**：
- 创建新对象，但内部元素的引用是共享的
- 只拷贝第一层，嵌套对象还是同一个引用
- 方式：`list.copy()`、切片 `[:]`、`dict.copy()`、`copy.copy()`

```python
import copy
a = [1, [2, 3]]
b = copy.copy(a)
b[0] = 100   # a 不受影响（第一层是新的）
b[1][0] = 200  # a 也变了！（嵌套列表是共享的）
```

**深拷贝（deep copy）**：
- 递归拷贝所有层级，完全独立的新对象
- 方式：`copy.deepcopy()`

```python
import copy
a = [1, [2, 3]]
b = copy.deepcopy(a)
b[1][0] = 200  # a 不变，完全独立
```

**对比总结**：

| 方式 | 新对象 | 嵌套对象 | 修改嵌套是否影响原对象 |
|------|--------|---------|----------------------|
| 赋值 = | 否 | 共享 | 是 |
| 浅拷贝 | 是（第一层） | 共享 | 是 |
| 深拷贝 | 是（所有层） | 独立 | 否 |

**注意**：
- 不可变对象（数字、字符串、tuple）深浅拷贝没区别
- 深拷贝可能遇到循环引用问题，`deepcopy` 内部有记录机制，不会无限递归
- 自定义类的拷贝：实现 `__copy__` 和 `__deepcopy__` 方法

</details>

---

### Q12: 协程是什么？asyncio 原理？和多线程区别？

- **类别**: 并发编程
- **难度**: 较难
- **频率**: 高

<details>
<summary>答题要点</summary>

**协程（Coroutine）**：
- 用户态的轻量级线程，由程序员调度，不由操作系统调度
- 一个线程内可以有很多协程，遇到 IO 自动切换
- 开销极小（内存几 KB），可以轻松创建上万协程

**asyncio 核心概念**：
- **事件循环（Event Loop）**：协程的调度器，管理所有协程的执行
- **协程函数**：`async def` 定义的函数，调用返回协程对象，不会立即执行
- **Task**：协程的包装，加入事件循环调度
- **Future**：异步操作的结果占位符

**执行流程**：
1. 创建事件循环
2. 把协程包装成 Task 加入事件循环
3. 事件循环调度执行，遇到 IO 挂起当前协程，切换到其他就绪协程
4. IO 完成后恢复协程继续执行

**asyncio 原理**：
- 底层基于生成器（generator）和事件循环
- Python 3.5+ 引入 `async/await` 语法糖，语义更清晰
- `await` 会挂起当前协程，让出控制权给事件循环
- 事件循环通过 select/epoll/kqueue 监听 IO 事件

**协程 vs 多线程**：

| 对比维度 | 协程 | 多线程 |
|---------|------|--------|
| 调度者 | 用户（事件循环） | 操作系统 |
| 切换开销 | 极小（函数调用级） | 较大（内核态切换） |
| 数量 | 几万~几十万 | 几千 |
| 数据共享 | 单线程内，无需锁（简单情况） | 需要锁机制 |
| 利用多核 | 不能（GIL + 单线程） | IO 密集型可以 |
| 适用场景 | IO 密集型高并发 | IO 密集型、CPU 密集型（多进程更好） |

**异步编程注意事项**：
- 不能在协程中写阻塞代码（如同步 IO、time.sleep），否则会阻塞整个事件循环
- 阻塞操作用对应的异步库（aiohttp、asyncpg）或放到线程池/进程池
- `asyncio.run()` 是 Python 3.7+ 的入口函数

</details>

---

### Q13: 闭包是什么？注意事项？

- **类别**: Python高级特性
- **难度**: 中等
- **频率**: 中等

<details>
<summary>答题要点</summary>

**闭包（Closure）**：
- 内层函数引用了外层函数的变量（非全局变量），内层函数就是闭包
- 外层函数返回内层函数后，内层函数仍然能访问外层函数的变量
- 被引用的外层变量叫"自由变量"

```python
def outer(x):
    def inner(y):
        return x + y  # x 是自由变量
    return inner

add5 = outer(5)
add5(3)  # 8，inner 仍然能访问 x=5
```

**闭包的条件**：
1. 必须有一个内层函数
2. 内层函数引用外层函数的变量
3. 外层函数返回内层函数

**闭包的作用**：
- 保存状态（函数调用之间保持数据）
- 数据封装（类似类的私有变量）
- 装饰器的基础

**注意事项**：

1. **闭包中修改外部变量需要 nonlocal**：
   ```python
   def counter():
       count = 0
       def inc():
           nonlocal count  # 必须声明，否则被当作局部变量
           count += 1
           return count
       return inc
   ```

2. **循环变量陷阱**：
   ```python
   def create_funcs():
       funcs = []
       for i in range(3):
           funcs.append(lambda: i)  # 所有 lambda 都引用同一个 i
       return funcs
   # 调用时 i 已经是 2，三个函数都返回 2
   # 解决：lambda i=i: i（默认参数捕获当前值）
   ```

3. **闭包变量保存在 `__closure__` 属性中**：
   - `inner.__closure__` 是一个元组，存自由变量的 cell 对象
   - `cell.cell_contents` 可以查看值

4. **内存泄漏风险**：闭包持有外层变量的引用，可能导致大对象无法回收。

</details>

---

### Q14: Python 中的 `__new__` 和 `__init__` 区别？

- **类别**: Python基础
- **难度**: 中等
- **频率**: 中等

<details>
<summary>答题要点</summary>

**`__new__`**：
- 构造方法，创建对象（分配内存）
- 是类方法（第一个参数是 cls）
- 返回一个新的实例（通常返回 super().__new__(cls)）
- 如果不返回实例，`__init__` 不会被调用

**`__init__`**：
- 初始化方法，给对象设置初始属性
- 是实例方法（第一个参数是 self）
- 没有返回值（返回 None）
- 在 `__new__` 创建实例后自动调用

**执行顺序**：
`__new__` 创建实例 → `__init__` 初始化实例

**对比**：

| 对比维度 | `__new__` | `__init__` |
|---------|-----------|------------|
| 作用 | 创建对象 | 初始化对象 |
| 参数 | cls + 其他 | self + 其他 |
| 返回值 | 必须返回实例 | 无返回值 |
| 调用时机 | 实例创建前 | 实例创建后 |
| 自定义 | 很少重写 | 经常重写 |

**什么时候重写 `__new__`**：
1. **单例模式**：控制只创建一个实例
2. **不可变类的子类**：如继承 int、str，需要在创建时修改值
3. **元类配合**：自定义类的创建过程

**单例模式示例**：
```python
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**注意**：`__new__` 是静态方法（虽然不用 @staticmethod 装饰），接收类作为第一个参数。

</details>

---

### Q15: 如何实现 Python 的单例模式？有几种方式？

- **类别**: 设计模式
- **难度**: 中等
- **频率**: 高

<details>
<summary>答题要点</summary>

**单例模式**：确保一个类只有一个实例，并提供全局访问点。

**实现方式**：

**1. 模块导入法（最推荐）**：
- Python 模块天然是单例的，导入时只执行一次
- 最简单、最 Pythonic

```python
# singleton.py
class Singleton:
    pass
instance = Singleton()
# 使用：from singleton import instance
```

**2. 装饰器法**：
```python
def singleton(cls):
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper

@singleton
class MyClass:
    pass
```

**3. `__new__` 方法**：
```python
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
```
- 注意：每次 `__init__` 都会被调用，需要处理重复初始化问题

**4. 元类（metaclass）法**：
```python
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    pass
```

**5. 多线程安全版本**：
- 以上方式在多线程下有问题（可能创建多个实例）
- 需要加锁：

```python
import threading
class Singleton:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # 双重检查
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**推荐方案**：
- 简单场景用模块导入法
- 需要类的形式用 `__new__` + 双重检查锁
- 装饰器法灵活可复用

</details>

---

### Q16: Python 中的上下文管理器？with 语句原理？

- **类别**: Python高级特性
- **难度**: 中等
- **频率**: 中等

<details>
<summary>答题要点</summary>

**上下文管理器**：
- 用于资源管理，确保资源被正确释放（文件、锁、数据库连接等）
- with 语句执行完自动清理资源，即使发生异常也会执行

**实现方式**：

**1. 类实现（`__enter__` + `__exit__`）**：
```python
class MyContext:
    def __enter__(self):
        # 进入 with 时执行，返回值绑定到 as 变量
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 离开 with 时执行（无论是否异常）
        # exc_type/val/tb 是异常信息，无异常则为 None
        # 返回 True 会抑制异常，返回 False 会继续抛出
        return False
```

**2. 生成器 + contextlib（更简洁）**：
```python
from contextlib import contextmanager

@contextmanager
def my_context():
    # __enter__ 部分
    resource = acquire_resource()
    try:
        yield resource  # yield 前是进入，yield 后是退出
    finally:
        # __exit__ 部分
        release_resource(resource)
```

**with 语句执行流程**：
1. 执行上下文管理器表达式，获取管理器对象
2. 调用 `__enter__()` 方法
3. `__enter__` 返回值赋给 `as` 后的变量
4. 执行 with 代码块
5. 无论是否异常，调用 `__exit__(exc_type, exc_val, exc_tb)`
6. `__exit__` 返回 True 则吞掉异常，False 则继续抛出

**常见应用**：
- 文件操作：`with open('file.txt') as f:`
- 线程锁：`with lock:`
- 数据库事务：`with conn.cursor() as cursor:`
- 临时修改环境变量、工作目录等

**为什么好用**：
- 比 try/finally 更简洁
- 不会忘记释放资源
- 逻辑更清晰

</details>

## Reference

- CSDN - Python 后端面试题汇总 2026（访问时间：2026-07-28）
- 掘金 - Python 八股文面试题精选（访问时间：2026-07-28）
- 牛客网 - Python 后端面试题库（访问时间：2026-07-28）
- 腾讯云开发者社区 - Python 高级面试题（访问时间：2026-07-28）

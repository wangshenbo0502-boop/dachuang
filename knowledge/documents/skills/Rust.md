---
title: Rust语言
category: skills
tags: [Rust, 系统编程, WebAssembly, 内存安全, 编程语言]
source: [Rust官方文档, Rust程序设计语言, 掘金Rust专栏, Rust圣经]
last_update: 2026-07-28
---

# Rust语言

> 由Mozilla主导开发的系统级编程语言，以内存安全、零成本抽象和并发安全为核心特性。2026年Rust连续第11年蝉联Stack Overflow"最受喜爱编程语言"，Linux内核、Android系统、Windows驱动均已引入Rust，区块链(Solana)、WebAssembly、云原生基础设施等领域Rust人才需求年增长率超120%。

- **就业影响**: 极高（系统编程/WebAssembly/区块链/云原生核心语言，薪资溢价显著）
- **前置技能**: C/C++基础, 操作系统原理, 数据结构与算法
- **关联系能**: WebAssembly, Solana, Substrate, Tokio, 嵌入式开发

---

## 阶段 1 — 目标：了解（预估 3 周）

**学习主题：**
- Rust核心概念与工具链：rustup、rustc、cargo环境搭建与项目创建
- 变量与可变性：let绑定、mut可变变量、const常量、shadowing变量遮蔽
- 基本数据类型：标量类型(整数/浮点/布尔/字符)、复合类型(元组/数组)
- 函数与控制流：函数定义与返回值、if/else表达式、loop/while/for循环
- 所有权(Ownership)与借用(Borrowing)：所有权规则、引用与借用、切片类型
- 结构体与枚举：struct定义与方法、enum定义与模式匹配、Option枚举
- 模式匹配：match表达式、if let简洁控制流、模式语法大全
- 包管理与Cargo：Cargo.toml配置、依赖管理、构建与发布流程
- 模块系统：mod模块定义、use导入、可见性pub、crate组织
- 集合类型与错误处理：Vector动态数组、HashMap哈希映射、Result错误处理

**学习资源：**
- [Rust程序设计语言(官方中文)](https://kaisery.github.io/trpl-zh-cn/) — 官方教程 · 免费 · 入门 · 中文
- [Rust圣经 - Rust Course](https://course.rs/) — 中文教程 · 免费 · 入门 · 中文
- [Rust by Example 中文版](https://rustwiki.org/zh-CN/rust-by-example/) — 实战示例 · 免费 · 入门 · 中文
- [极客时间 - Rust编程第一课](https://time.geekbang.org/) — 视频课程 · 付费 · 入门 · 中文

**练习项目：**
- 实现一个命令行猜数字游戏，练习变量、循环、随机数与模式匹配
- 编写一个学生成绩管理系统，使用struct、Vec和HashMap存储与查询数据
- 实现一个简易计算器，支持加减乘除四则运算与错误处理(Result)
- 使用Cargo管理一个多模块项目，包含lib库与bin二进制目标

**评估方式：**
- 概念掌握 — 能清晰解释所有权与借用机制，独立编写无编译错误的Rust代码
- 代码实操 — 熟练使用Cargo进行项目管理、依赖引入与构建发布
- 项目验收 — 完成至少3个练习项目，代码通过cargo clippy静态检查

---

## 阶段 2 — 目标：熟悉（预估 4 周）

**学习主题：**
- 泛型与特征(Trait)：泛型函数与结构体、Trait定义与实现、Trait作为参数与返回值
- 生命周期(Lifetime)：引用生命周期标注、结构体生命周期、生命周期省略规则
- 闭包与迭代器：闭包定义与捕获、Fn/FnMut/FnOnce trait、迭代器适配器与消费器
- 智能指针：Box<T>堆分配、Rc<T>引用计数、Arc<T>原子引用计数、RefCell<T>内部可变性
- 并发安全：线程创建与管理、消息传递(通道mpsc)、Sync与Send trait、线程池
- 文件IO与序列化：标准输入输出、文件读写、serde序列化与反序列化
- 单元测试与文档测试：#[test]测试函数、assert断言、文档测试、集成测试
- 命令行工具开发：clap参数解析、错误处理与退出码、日志输出(env_logger)
- WebAssembly入门：wasm-pack工具链、Rust编译为WASM、与JavaScript互操作
- 常用crate生态：rand、serde、tokio入门、reqwest、anyhow、thiserror

**学习资源：**
- [Rust标准库文档](https://doc.rust-lang.org/std/) — 官方文档 · 免费 · 进阶 · 英文
- [Rust 高级编程(中文版)](https://nomicon.purewhite.io/) — 高级教程 · 免费 · 进阶 · 中文
- [掘金Rust专栏 - Rust实战进阶](https://juejin.cn/column/rust) — 技术专栏 · 免费 · 进阶 · 中文
- [Rust实战 - Manning出版](https://www.manning.com/books/rust-in-action) — 实战书籍 · 付费 · 进阶 · 英文

**练习项目：**
- 使用clap + serde开发一个JSON/CSV格式转换命令行工具
- 实现一个多线程并发下载器，使用通道(mpsc)进行线程间通信
- 编写一个带单元测试和文档测试的数学运算库，覆盖率达80%以上
- 使用wasm-pack将Rust算法编译为WebAssembly，在浏览器中调用并对比性能
- 实现一个简单的Redis客户端，练习网络编程与错误处理最佳实践

**评估方式：**
- 代码质量 — 熟练使用泛型与Trait进行抽象设计，代码符合Rust idiomatic风格
- 并发编程 — 能够编写线程安全的并发程序，正确使用Arc/Mutex/通道
- 工程能力 — 独立完成命令行工具开发，包含完整的测试、文档与错误处理
- 技术广度 — 了解WebAssembly等前沿应用方向，具备跨领域拓展能力

---

## 阶段 3 — 目标：掌握（预估 5 周）

**学习主题：**
- unsafe Rust：裸指针操作、unsafe函数与trait、不安全代码块的安全边界
- 宏编程(Macro)：声明宏macro_rules!、过程宏(derive宏/属性宏/函数宏)、宏展开调试
- 类型系统深入：newtype模式、类型状态机、幽灵数据(PhantomData)、GAT泛型关联类型
- 零成本抽象与性能优化：内联优化、泛型单态化、内存布局优化、SIMD并行计算
- 内存布局与对齐：repr属性控制、内存对齐原则、packed布局、union联合体
- 异步编程：async/await语法、Future trait、Tokio运行时、异步IO与并发任务
- 嵌入式开发：no_std环境、嵌入式hal、外设驱动开发、RTIC实时框架
- 区块链开发：Solana程序开发、Substrate链上模块(pallet)、ink!智能合约
- 系统编程与操作系统：系统调用封装、Linux内核模块、设备驱动开发、操作系统原理实践
- FFI与互操作：Rust调用C/C++、C/C++调用Rust、cbindgen工具、Python/Node.js绑定

**学习资源：**
- [The Rustonomicon - 死灵书](https://doc.rust-lang.org/nomicon/) — 官方文档 · 免费 · 高级 · 英文
- [Rust异步编程指南](https://rust-lang.github.io/async-book/) — 官方文档 · 免费 · 高级 · 英文
- [Solana官方开发者文档](https://docs.solana.com/) — 官方文档 · 免费 · 高级 · 英文
- [Substrate开发者中心](https://substrate.io/developers/) — 官方文档 · 免费 · 高级 · 英文
- [Embedded Rust Book](https://docs.rust-embedded.org/book/) — 官方文档 · 免费 · 高级 · 英文

**练习项目：**
- 基于Tokio实现一个高性能异步HTTP服务器，支持路由、中间件与并发连接
- 使用过程宏(proc-macro)开发一个自定义derive宏，实现结构体的自动序列化
- 在STM32或ESP32上完成嵌入式项目：传感器数据采集 + OLED显示
- 开发一个Solana链上程序(SPL Token扩展或DeFi协议片段)，完成部署与测试
- 编写一个Linux内核模块或系统工具，使用Rust进行底层系统编程

**评估方式：**
- 深度掌握 — 能够阅读和编写unsafe Rust代码，准确评估安全性边界
- 架构能力 — 能够独立设计复杂系统架构，合理运用宏、类型系统等高级特性
- 领域专长 — 在嵌入式/区块链/系统编程至少一个方向具备生产级项目经验
- 性能调优 — 具备性能分析与优化能力，能够编写接近C语言性能的Rust代码

---

## 学习建议与进阶路径

- **编译驱动学习**：Rust编译器是最好的老师，遇到编译错误先仔细阅读错误提示，善用rustc --explain
- **所有权思维**：Rust的核心是所有权系统，初期多画图理解内存模型，切忌用GC语言思维写Rust
- **实战为王**：Rust学习曲线陡峭，务必边学边练，每周至少完成一个完整的小项目
- **拥抱生态**：crates.io有丰富的第三方库，优先使用成熟crate，避免重复造轮子
- **社区参与**：关注Rust官方博客、Inside Rust论坛，参与RFC讨论，紧跟语言演进
- **方向深耕**：Rust应用领域广泛（系统编程/区块链/WebAssembly/云原生/嵌入式），建议选定一个方向深入发展

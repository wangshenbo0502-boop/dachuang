---
title: "JavaScript基础面试题（20题）"
category: "面试题"
type: "前端"
difficulty: "中等"
tags: ["JavaScript", "前端基础", "闭包", "原型链", "事件循环"]
source: ["MDN Web Docs", "ECMAScript 标准", "前端面试题库", "掘金前端社区"]
last_update: "2026-07-28"
---

# JavaScript 基础面试题（20题）

本文档收录了 JavaScript 基础核心的 20 道高频面试题，涵盖闭包、原型链、事件循环、作用域、异步编程等核心知识点。

---

## Q1: 什么是闭包？闭包的应用场景有哪些？

**考察点**: 闭包的概念、形成条件、应用场景及优缺点

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

闭包（Closure）是指有权访问另一个函数作用域中变量的函数。当内部函数引用了外部函数的变量，即使外部函数执行完毕，这些变量仍然不会被销毁，因为闭包在引用它们。

闭包形成的三个条件：
1. 函数嵌套函数
2. 内部函数引用了外部函数的变量/参数
3. 内部函数被返回或被外部使用

常见应用场景：
- **数据私有化/封装**：通过闭包创建私有变量，只能通过特定方法访问和修改
- **函数柯里化**：利用闭包实现函数参数的缓存
- **防抖和节流**：利用闭包保存定时器或时间戳状态
- **模块化开发**：IIFE + 闭包实现模块化，避免全局变量污染
- **循环中保留变量**：解决循环中异步操作的变量引用问题
- **回调函数**：事件处理函数中保持对外部作用域的引用

**答案解析**:

闭包的本质是作用域链的应用。JavaScript 采用词法作用域（静态作用域），函数的作用域在定义时就已确定。当内部函数在外部函数之外被调用时，它仍然能够访问定义时的作用域，这就是闭包。

```javascript
// 数据私有化示例
function createCounter() {
  let count = 0; // 私有变量
  return {
    increment() { return ++count; },
    decrement() { return --count; },
    getCount() { return count; }
  };
}
const counter = createCounter();
console.log(counter.increment()); // 1
console.log(counter.getCount());  // 1
console.log(counter.count);     // undefined，外部无法直接访问
```

闭包的优点：
- 实现数据私有化和封装
- 避免全局变量污染
- 变量长期保存在内存中，可以做缓存

闭包的缺点：
- 变量不会被垃圾回收，可能导致内存泄漏
- 过度使用会增加内存消耗
- 性能上有一定开销

**扩展问题**:
- 闭包为什么会导致内存泄漏？如何避免？
- 如何用闭包实现一个 once 函数（只执行一次）？
- 闭包和作用域链的关系是什么？
- 循环中使用 var 和 let 对闭包有什么不同影响？

---

## Q2: 什么是原型和原型链？

**考察点**: 原型、原型对象、构造函数、实例的关系，原型链的查找机制

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**原型（Prototype）**：
每个函数都有一个 `prototype` 属性，它是一个对象，包含了所有实例共享的属性和方法。当使用构造函数创建实例时，实例的 `__proto__`（隐式原型）指向构造函数的 `prototype`（显式原型）。

**原型链（Prototype Chain）**：
当访问对象的某个属性或方法时，如果对象本身没有，就会去它的 `__proto__`（即构造函数的 prototype）上找，如果还没有，就继续往上找 `prototype.__proto__`，直到找到 `Object.prototype.__proto__`（为 null）为止。这条由 `__proto__` 串联起来的链就是原型链。

三个重要关系：
1. `实例.__proto__ === 构造函数.prototype`
2. `构造函数.prototype.constructor === 构造函数`
3. `构造函数.prototype.__proto__ === Object.prototype`

**答案解析**:

原型是 JavaScript 实现继承的核心机制。理解原型链的关键在于理清几个概念之间的关系：

```javascript
function Person(name) {
  this.name = name;
}
Person.prototype.sayName = function() {
  console.log(this.name);
};

const p = new Person('Tom');

console.log(p.__proto__ === Person.prototype);          // true
console.log(Person.prototype.constructor === Person);   // true
console.log(Person.prototype.__proto__ === Object.prototype); // true
console.log(Object.prototype.__proto__ === null);       // true
```

原型链的查找过程：
1. 先在对象自身属性中查找（`hasOwnProperty` 判断）
2. 找不到则沿 `__proto__` 向上查找构造函数的 prototype
3. 逐层向上，直到 `Object.prototype`
4. 最终找不到返回 `undefined`

注意：`__proto__` 是非标准属性，ES6 标准中使用 `Object.getPrototypeOf()` 和 `Object.setPrototypeOf()` 来获取和设置原型。

**扩展问题**:
- `__proto__` 和 `prototype` 有什么区别？
- 如何判断一个属性是对象自身的还是原型上的？
- 原型链继承有什么缺点？
- `Object.create()` 的原理是什么？
- `instanceof` 的实现原理是什么？

---

## Q3: 什么是事件循环（Event Loop）？

**考察点**: JavaScript 单线程机制、事件循环原理、宏任务微任务执行顺序

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

事件循环（Event Loop）是 JavaScript 实现异步编程的核心机制。JavaScript 是单线程语言，但通过事件循环机制可以实现非阻塞的异步操作。

事件循环的基本流程：
1. **执行栈（Call Stack）**：同步代码按顺序在执行栈中执行
2. **任务队列（Task Queue）**：异步任务的回调会被放入任务队列中等待
3. 当执行栈为空时，事件循环会从任务队列中取出任务放入执行栈执行
4. 不断重复这个过程，就是事件循环

事件循环分为浏览器的 Event Loop 和 Node.js 的 Event Loop，两者机制有所不同。

**答案解析**:

浏览器端的事件循环：

```
  执行栈（Call Stack）
        |
        v
  Web APIs（setTimeout、DOM事件、fetch等）
        |
        v
  任务队列（Task Queue）
        |
        v
  事件循环（Event Loop）→ 取出回调放入执行栈
```

完整的执行顺序：
1. 执行全局 Script 同步代码
2. 执行栈为空后，检查微任务队列，依次执行所有微任务
3. 执行完所有微任务后，取出一个宏任务执行
4. 宏任务执行完后，再次检查并执行所有微任务
5. 重复 3-4 步骤

关键要点：
- JavaScript 引擎负责执行代码，是单线程的
- 浏览器提供了 Web API（定时器、DOM事件、HTTP请求等）
- 任务队列分为宏任务队列和微任务队列
- 每次宏任务执行完毕后，会清空微任务队列
- 微任务在当前宏任务结束后、下一个宏任务开始前执行

**扩展问题**:
- Node.js 的事件循环和浏览器有什么不同？
- requestAnimationFrame 属于宏任务还是微任务？
- 为什么需要微任务？只有宏任务不行吗？
- 事件循环和 UI 渲染的时机是什么关系？

---

## Q4: 宏任务和微任务有哪些？执行顺序是怎样的？

**考察点**: 宏任务和微任务的分类、执行顺序、常见面试题输出

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**宏任务（Macrotask）**：
- `setTimeout、setInterval
- setImmediate（Node.js）
- I/O 操作（文件读写、网络请求）
- UI 渲染（浏览器）
- requestAnimationFrame（浏览器）
- 事件回调（DOM 事件）

**微任务（Microtask）**：
- Promise.then/catch/finally
- async/await（本质是 Promise）
- MutationObserver（浏览器）
- process.nextTick（Node.js，优先级高于 Promise）
- queueMicrotask

**执行顺序**：
1. 执行同步代码（属于宏任务）
2. 执行完同步代码后，执行所有微任务
3. 取出一个宏任务执行
4. 宏任务执行完后，执行所有微任务
5. 重复 3-4 步骤

**答案解析**:

经典面试题分析：

```javascript
console.log('1');

setTimeout(() => {
  console.log('2');
  Promise.resolve().then(() => {
    console.log('3');
  });
}, 0);

Promise.resolve().then(() => {
  console.log('4');
});

console.log('5');

// 输出顺序：1 5 4 2 3
```

解析：
1. 同步代码输出 1、5
2. 微任务队列：Promise.then → 输出 4
3. 宏任务队列：setTimeout 回调 → 输出 2
4. 该宏任务内产生微任务 → 输出 3

更复杂的例子（含 async/await）：

```javascript
async function async1() {
  console.log('async1 start');
  await async2();
  console.log('async1 end');
}
async function async2() {
  console.log('async2');
}
console.log('script start');
setTimeout(() => console.log('setTimeout'), 0);
async1();
new Promise(resolve => {
  console.log('promise1');
  resolve();
}).then(() => {
  console.log('promise2');
});
console.log('script end');

// 输出顺序：
// script start
// async1 start
// async2
// promise1
// script end
// async1 end
// promise2
// setTimeout
```

注意：`await` 后面的代码相当于 Promise.then 的回调，属于微任务。

**扩展问题**:
- process.nextTick 和 Promise.then 谁先执行？
- setImmediate 和 setTimeout 的执行顺序在 Node.js 中是怎样的？
- 为什么微任务要在宏任务之前执行？
- 如何手动创建一个微任务？

---

## Q5: var、let、const 的区别是什么？

**考察点**: 变量声明方式、作用域、变量提升、暂时性死区

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

| 特性 | var | let | const |
|------|-----|-----|-------|
| 作用域 | 函数作用域 | 块级作用域 | 块级作用域 |
| 变量提升 | 有（声明提升，赋值不提升） | 有但存在暂时性死区 | 有但存在暂时性死区 |
| 重复声明 | 可以 | 不可以 | 不可以 |
| 重新赋值 | 可以 | 可以 | 不可以（基本类型） |
| 初始化 | 可只声明不赋值 | 可只声明不赋值 | 声明时必须赋值 |
| 挂载到 window | 是（全局作用域下） | 否 | 否 |

**答案解析**:

1. **作用域区别**：
   - `var` 是函数作用域，在函数外部声明就是全局变量
   - `let` 和 `const` 是块级作用域（`{}` 包裹的区域）

```javascript
if (true) {
  var a = 1;
  let b = 2;
}
console.log(a); // 1，var 不受块级作用域限制
console.log(b); // ReferenceError，let 是块级作用域
```

2. **变量提升和暂时性死区**：
   - `var` 声明会被提升到函数/全局作用域顶部，值为 undefined
   - `let/const` 也有提升，但在声明之前访问会报 `ReferenceError`，这就是暂时性死区（TDZ）

```javascript
console.log(a); // undefined，undefined，变量提升但未赋值
console.log(b); // ReferenceError，暂时性死区
var a = 1;
let b = 2;
```

3. **重复声明**：
   - `var` 可以重复声明同一个变量
   - `let/const` 在同一作用域内不能重复声明

4. **const 的特殊性**：
   - `const` 声明的变量不能重新赋值，但如果是对象或数组时，其内部属性/元素可以修改
   - 要完全冻结对象，使用 `Object.freeze()`

```javascript
const obj = { a: 1 };
obj.a = 2; // 可以，对象引用不变
obj = {};  // TypeError，不能重新赋值
```

**扩展问题**:
- 什么是暂时性死区？为什么会有暂时性死区？
- 为什么 for 循环中用 var 会有闭包问题，let 不会？
- let 和 const 的底层实现有什么区别？
- 全局作用域下 let 声明的变量存在哪里？

---

## Q6: 箭头函数和普通函数的区别是什么？

**考察点**: 箭头函数的特性、this 指向、适用场景

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

箭头函数是 ES6 新增的函数定义方式，与普通函数主要有以下区别：

1. **this 指向不同**：
   - 普通函数的 this 指向调用时的对象（动态绑定）
   - 箭头函数没有自己的 this，它的 this 继承自定义时外层作用域的 this（静态绑定）

2. **不能作为构造函数**：
   - 箭头函数不能使用 new 调用，没有 prototype 属性

3. **没有 arguments 对象**：
   - 箭头函数没有 arguments，可以用 rest 参数代替

4. **不能用作 Generator 函数**：
   - 箭头函数不能使用 yield 关键字

5. **没有 new.target**：
   - 箭头函数没有 new.target

6. **语法更简洁**：
   - 单表达式可以省略 return 和大括号

**答案解析**:

**this 指向的区别是最核心的：

```javascript
const obj = {
  name: 'obj',
  normalFn: function() {
    console.log(this.name); // this 指向 obj
  },
  arrowFn: () => {
    console.log(this.name); // this 指向定义时外层的 this（全局或 undefined）
  }
};

obj.normalFn(); // 'obj'
obj.arrowFn();  // undefined（全局作用域中 this 指向 window/undefined
```

箭头函数 this 的应用场景：

```javascript
// 场景1：定时器中保持 this
function Person() {
  this.age = 0;
  setInterval(() => {
    this.age++; // this 指向 Person 实例
  }, 1000);
}

// 场景2：数组方法回调
const arr = [1, 2, 3];
const doubled = arr.map(x => x * 2); // 简洁的回调
```

箭头函数不适用的场景：
1. 作为对象方法（this 不会指向对象本身）
2. 作为构造函数（不能 new）
3. 需要 arguments 时
4. 需要动态 this 绑定的场景（如事件处理函数）

**扩展问题**:
- 箭头函数的 this 可以通过 call/apply/bind 改变吗？
- 箭头函数为什么不能作为构造函数的原因是什么？
- 如何用 ES5 实现箭头函数的 this 绑定效果？
- 箭头函数有 prototype 吗？为什么？

---

## Q7: this 的指向问题有哪些场景？

**考察点**: this 的绑定规则、优先级、常见场景分析

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

this 的指向遵循以下绑定规则（优先级从高到低）：

1. **new 绑定**：new 调用构造函数时，this 指向新创建的实例对象
2. **显式绑定**：通过 call、apply、bind 绑定，this 指向指定的对象
3. **隐式绑定**：作为对象方法调用时，this 指向调用该方法的对象
4. **默认绑定**：独立函数调用时，this 指向全局对象（严格模式下为 undefined）

特殊情况：
- 箭头函数：this 继承自外层作用域，不受以上规则
- 定时器/事件回调：取决于具体调用方式
- 严格模式：默认绑定为 undefined

**答案解析**:

**1. 默认绑定**：
```javascript
function foo() {
  console.log(this.a);
}
var a = 2;
foo(); // 2，默认绑定到全局对象
```

**2. 隐式绑定**：
```javascript
const obj = {
  a: 2,
  foo: function() { console.log(this.a); }
};
obj.foo(); // 2，隐式绑定到 obj
```

隐式丢失：
```javascript
const bar = obj.foo;
bar(); // undefined，函数赋值后独立调用，this 丢失
```

**3. 显式绑定**：
```javascript
function foo() { console.log(this.a); }
const obj = { a: 2 };
foo.call(obj);  // 2
foo.apply(obj); // 2
const boundFoo = foo.bind(obj);
boundFoo(); // 2
```

**4. new 绑定**：
```javascript
function Foo(a) {
  this.a = a;
}
const bar = new Foo(2);
console.log(bar.a); // 2
```

**优先级判断**：new 绑定 > 显式绑定 > 隐式绑定 > 默认绑定

**箭头函数的 this**：
```javascript
function foo() {
  return () => {
    console.log(this.a);
  };
}
const obj1 = { a: 2 };
const obj2 = { a: 3 };
const bar = foo.call(obj1);
bar.call(obj2); // 2，箭头函数 this 一旦确定就无法改变
```

**扩展问题**:
- 如何判断一个函数的 this 指向？
- bind 多次绑定 this 会怎样？
- 事件处理函数中的 this 指向什么？
- 如何实现一个 bind 函数？

---

## Q8: 什么是作用域和作用域链？

**考察点**: 作用域类型、作用域链的形成、变量查找机制

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

**作用域（Scope）**：
作用域是指程序中定义变量的区域，它决定了变量的可访问性。JavaScript 采用词法作用域（静态作用域），即作用域在代码书写时就已确定，而非运行时确定。

作用域类型：
- **全局作用域**：最外层的作用域，全局变量在任何地方都能访问
- **函数作用域**：函数内部定义的变量，只能在函数内部访问
- **块级作用域**：ES6 新增，通过 let/const 声明的变量在 {} 内有效

**作用域链（Scope Chain）**：
当访问一个变量时，JavaScript 引擎会先在当前作用域查找，如果找不到，就去父级作用域查找，一直找到全局作用域为止。这条由作用域嵌套形成的查找链就是作用域链。

**答案解析**:

作用域链的形成与函数的定义位置有关，与调用位置无关（词法作用域）。

```javascript
var a = 1; // 全局作用域

function outer() {
  var b = 2; // outer 函数作用域
  
  function inner() {
    var c = 3; // inner 函数作用域
    console.log(a + b + c); // 沿作用域链查找 a、b、c
  }
  
  inner();
}

outer(); // 6
```

作用域链的结构：
```
inner 作用域 → outer 作用域 → 全局作用域
```

**作用域链的特点：
1. 函数的作用域在定义时确定（词法作用域）
2. 作用域链保证了变量查找的顺序
3. 内部作用域可以访问外部作用域的变量，反之不行
4. 作用域链是单向的，从内到外查找

**延长作用域链**：
- try-catch 的 catch 块
- with 语句（不推荐使用）

**闭包与作用域链的关系**：
闭包的本质就是函数能够访问定义时的作用域链，即使函数在定义时的作用域之外被调用。

**扩展问题**:
- 什么是词法作用域和动态作用域？JavaScript 是哪种？
- 作用域链和原型链有什么区别和联系？
- 如何理解执行上下文和作用域的关系？
- eval 会影响作用域吗？

---

## Q9: == 和 === 的区别是什么？什么是隐式类型转换？

**考察点**: 相等运算符、类型转换规则、常见陷阱

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

**==（宽松相等）**：
- 比较时会进行隐式类型转换，再比较值是否相等
- 两边类型不同时，会尝试转换为相同类型再比较

**===（严格相等）**：
- 不会进行类型转换，类型不同直接返回 false
- 类型相同且值也相同时才返回 true

**隐式类型转换规则（==）**：
1. 两边类型相同，直接比较值
2. null 和 undefined 相等（互相 == 为 true，与其他值都为 false）
3. 数字和字符串比较，字符串转数字
4. 布尔值和其他类型比较，布尔值转数字
5. 对象和原始类型比较，对象转原始类型（先 valueOf 再 toString）

**答案解析**:

经典面试题：

```javascript
console.log([] == ![]); // true
// 解析：
// ![] → false（空数组转布尔为 true，取反为 false）
// [] == false
// false 转数字 → 0
// [] 转原始值 → ''
// '' == 0 → '' 转数字 0 → 0 == 0 → true
```

```javascript
console.log(null == undefined); // true
console.log(null === undefined); // false

console.log('' == false); // true
console.log('' === false); // false

console.log(1 == true); // true
console.log(1 === true); // false

console.log(NaN == NaN); // false，NaN 不等于任何值，包括自己
```

**对象转原始类型的过程**：
1. 如果是原始类型直接返回
2. 调用 `valueOf()`，如果返回原始类型则使用
3. 调用 `toString()`，如果返回原始类型则使用
4. 都不返回原始类型则报错

**推荐使用 === 的原因**：
- 避免隐式类型转换带来的意外结果
- 代码更清晰，减少 bug
- 性能略高（不需要类型转换）

**扩展问题**:
- Object.is() 和 === 有什么区别？
- 为什么 [] == false 和 !![] 分别是什么？为什么？
- 什么情况下推荐使用 ==？
- 如何让 a == 1 && a == 2 && a == 3 成立？

---

## Q10: 深拷贝和浅拷贝的实现方式有哪些？

**考察点**: 深浅拷贝的区别、各种实现方式及优缺点

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**浅拷贝**：只复制对象的第一层属性，嵌套对象只复制引用
- Object.assign()
- 展开运算符 ...
- Array.prototype.slice() / concat()（数组）

**深拷贝**：递归复制对象的所有层级，嵌套对象也完全独立
- JSON.parse(JSON.stringify())
- 递归实现
- lodash 的 _.cloneDeep()
- structuredClone()（浏览器原生 API）

**答案解析**:

**浅拷贝实现**：

```javascript
// 1. Object.assign
const obj = { a: 1, b: { c: 2 } };
const copy = Object.assign({}, obj);

// 2. 展开运算符
const copy2 = { ...obj };

// 数组浅拷贝
const arr = [1, 2, { a: 3 }];
const arrCopy = [...arr]; // 或 arr.slice() / arr.concat()
```

**深拷贝实现**：

```javascript
// 1. JSON 方法（最简单但有缺陷）
const deepCopy1 = JSON.parse(JSON.stringify(obj));
// 缺陷：不能复制函数、undefined、Symbol、循环引用、Date、RegExp 等

// 2. 递归实现
function deepClone(obj, hash = new WeakMap()) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj);
  if (obj instanceof RegExp) return new RegExp(obj);
  if (hash.has(obj)) return hash.get(obj); // 处理循环引用
  
  const clone = Array.isArray(obj) ? [] : {};
  hash.set(obj, clone);
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      clone[key] = deepClone(obj[key], hash);
    }
  }
  return clone;
}

// 3. 浏览器原生 structuredClone（现代浏览器支持）
const deepCopy3 = structuredClone(obj);
```

**深浅拷贝的区别**：
- 浅拷贝后，修改嵌套对象会影响原对象
- 深拷贝后，两个对象完全独立，互不影响

```javascript
const obj = { a: 1, b: { c: 2 } };
const shallow = { ...obj };
shallow.b.c = 3;
console.log(obj.b.c); // 3，浅拷贝嵌套对象共享引用

const deep = JSON.parse(JSON.stringify(obj));
deep.b.c = 4;
console.log(obj.b.c); // 3，深拷贝互不影响
```

**扩展问题**:
- JSON.parse(JSON.stringify()) 有哪些缺陷？
- 如何处理循环引用的深拷贝？
- 深拷贝函数和函数引用如何处理？
- lodash 的 cloneDeep 原理是什么？

---

## Q11: 什么是防抖和节流？如何实现？

**考察点**: 防抖节流的概念、区别、实现原理及应用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**防抖（Debounce）**：
在事件触发 n 秒后执行回调，如果在 n 秒内事件再次被触发，则重新计时。

应用场景：
- 搜索框输入联想（避免每次输入都请求）
- 窗口 resize 事件
- 表单验证

**节流（Throttle）**：
规定在单位时间内，事件只触发一次，多次触发只执行一次。

应用场景：
- 滚动加载更多
- 鼠标移动事件
- 按钮点击防重复提交

**答案解析**:

**防抖实现**：

```javascript
function debounce(fn, delay) {
  let timer = null;
  return function(...args) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

// 立即执行版
function debounceImmediate(fn, delay, immediate) {
  let timer = null;
  return function(...args) {
    if (timer) clearTimeout(timer);
    if (immediate && !timer) {
      fn.apply(this, args);
    }
    timer = setTimeout(() => {
      if (!immediate) fn.apply(this, args);
      timer = null;
    }, delay);
  };
}
```

**节流实现**：

```javascript
// 时间戳版（首触发立即执行）
function throttleTimestamp(fn, delay) {
  let prev = 0;
  return function(...args) {
    const now = Date.now();
    if (now - prev >= delay) {
      fn.apply(this, args);
      prev = now;
    }
  };
}

// 定时器版（尾触发）
function throttleTimer(fn, delay) {
  let timer = null;
  return function(...args) {
    if (!timer) {
      timer = setTimeout(() => {
        fn.apply(this, args);
        timer = null;
      }, delay);
    }
  };
}

// 结合版（首触发 + 尾触发）
function throttle(fn, delay) {
  let prev = 0;
  let timer = null;
  return function(...args) {
    const now = Date.now();
    const remaining = delay - (now - prev);
    if (remaining <= 0) {
      if (timer) {
        clearTimeout(timer);
        timer = null;
      }
      fn.apply(this, args);
      prev = now;
    } else if (!timer) {
      timer = setTimeout(() => {
        fn.apply(this, args);
        prev = Date.now();
        timer = null;
      }, remaining);
    }
  };
}
```

**核心区别**：
- 防抖：多次触发合并为一次执行（重置计时器）
- 节流：稀释执行频率，固定时间间隔执行一次

**扩展问题**:
- 防抖和节流的本质区别是什么？
- 如何选择使用防抖还是节流？
- lodash 的 debounce 和 throttle 有什么高级功能？
- 如何取消防抖/节流函数的执行？

---

## Q12: Promise 的三种状态和常用方法有哪些？

**考察点**: Promise 状态、常用方法、链式调用、错误处理

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**三种状态**：
1. **pending（进行中）**：初始状态
2. **fulfilled（已成功）**：操作成功完成
3. **rejected（已失败）**：操作失败

状态特点：
- 状态只能从 pending 变为 fulfilled 或 rejected
- 状态一旦改变就不会再变
- 状态改变后添加的回调会立即执行

**常用方法**：
- **Promise.prototype.then()：添加成功和失败回调
- **Promise.prototype.catch()**：添加失败回调
- **Promise.prototype.finally()**：无论成功失败都会执行
- **Promise.resolve()**：返回一个 resolved 的 Promise
- **Promise.reject()**：返回一个 rejected 的 Promise
- **Promise.all()**：所有 Promise 都成功才成功，一个失败就失败
- **Promise.race()**：谁先改变状态就返回谁的结果
- **Promise.allSettled()**：等待所有 Promise 完成，返回所有结果
- **Promise.any()**：只要有一个成功就成功，全部失败才失败

**答案解析**:

**Promise 链式调用**：
```javascript
new Promise((resolve, reject) => {
  setTimeout(() => resolve(1), 1000);
})
.then(result => {
  console.log(result); // 1
  return result * 2;
})
.then(result => {
  console.log(result); // 2
  throw new Error('error');
})
.catch(err => {
  console.error(err.message); // error
})
.finally(() => {
  console.log('done');
});
```

**Promise.all**：
```javascript
Promise.all([p1, p2, p3]).then(results => {
  console.log(results); // [r1, r2, r3]，顺序与传入一致
}).catch(err => {
  // 只要有一个失败就进入 catch
});
```

**Promise.race**：
```javascript
Promise.race([p1, p2]).then(result => {
  // 返回最先完成的那个的结果
});
```

**错误穿透**：
Promise 的错误会一直向后传递，直到被 catch 捕获，这就是错误穿透。

```javascript
new Promise((resolve, reject) => {
  reject('error');
}).then(() => {
  // 不会执行
}).then(() => {
  // 不会执行
}).catch(err => {
  console.log(err); // 'error'，错误穿透到这里
});
```

**扩展问题**:
- Promise.all 和 Promise.allSettled 有什么区别？
- Promise 的 then 方法返回的是什么？
- 如何实现一个 Promise？
- Promise 如何取消？有哪些取消方案？

---

## Q13: async/await 的原理和错误处理方式是什么？

**考察点**: async/await 语法、原理、错误处理、与 Promise 的关系

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**async/await 原理**：
async/await 是 ES8 引入的异步编程语法糖，基于 Promise 实现，使异步代码看起来像同步代码。

- **async 函数**：
  - 函数返回一个 Promise 对象
  - return 的值会成为 then 回调的参数
  - throw 的错误会成为 catch 回调的参数

- **await**：
  - 只能在 async 函数内使用
  - 后面跟一个 Promise 对象（也可以是普通值）
  - 会暂停 async 函数的执行，等待 Promise resolve
  - 返回 Promise resolve 的值
  - 如果 Promise reject，会抛出错误

**错误处理方式**：
1. try/catch 包裹 await
2. await 后面跟 .catch()
3. Promise 包装返回 [err, data] 模式

**答案解析**:

**基本用法**：
```javascript
async function fetchData() {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('请求失败:', error);
    throw error;
  }
}
```

**串行和并行**：
```javascript
// 串行执行
async function serial() {
  const a = await fetchA();
  const b = await fetchB(); // 等待 a 完成后才开始
  return a + b;
}

// 并行执行
async function parallel() {
  const [a, b] = await Promise.all([fetchA(), fetchB()]);
  return a + b;
}
```

**错误处理的几种方式**：

```javascript
// 1. try/catch（最常用）
async function test1() {
  try {
    const result = await promise;
  } catch (err) {
    console.error(err);
  }
}

// 2. .catch()
async function test2() {
  const result = await promise.catch(err => console.error(err));
}

// 3. 统一错误处理封装
function to(promise) {
  return promise
    .then(data => [null, data])
    .catch(err => [err, null]);
}

async function test3() {
  const [err, data] = await to(fetchData());
  if (err) return console.error(err);
  console.log(data);
}
```

**async/await 与 Generator 的关系**：
async/await 可以看作是 Generator + Promise 的语法糖，自动执行 Generator 并返回 Promise。

**扩展问题**:
- async/await 和 Promise 相比有什么优缺点？
- 如何实现多个 await 并发执行？
- await 后面跟非 Promise 值会怎样？
- async 函数的返回值一定是 Promise 吗？
- for 循环中使用 await 会怎样？和 forEach 中使用 await 有什么区别？

---

## Q14: 什么是 Generator 函数？

**考察点**: Generator 概念、语法、执行机制、应用场景

**难度**: 困难

**频率**: ⭐⭐⭐

**标准答案**:

Generator（生成器）函数是 ES6 提供的一种异步编程解决方案，它是一种状态机，封装了多个内部状态。

**特点**：
- function 关键字和函数名之间有一个星号 `*`
- 函数内部使用 `yield` 表达式定义不同的内部状态
- 调用 Generator 函数返回一个遍历器对象（Iterator）
- 通过调用 `next()` 方法遍历内部状态
- 可以暂停执行和恢复执行

**常用方法**：
- `next()`：恢复执行，返回 `{ value, done }`
- `return()`：终止遍历器
- `throw()`：在函数内部抛出错误

**答案解析**:

**基本用法**：
```javascript
function* gen() {
  yield 'hello';
  yield 'world';
  return 'ending';
}

const g = gen();
console.log(g.next()); // { value: 'hello', done: false }
console.log(g.next()); // { value: 'world', done: false }
console.log(g.next()); // { value: 'ending', done: true }
console.log(g.next()); // { value: undefined, done: true }
```

**next 传参**：
next 方法的参数会作为上一个 yield 表达式的返回值。

```javascript
function* gen(x) {
  const y = yield x + 1;
  const z = yield y + 2;
  return z + 3;
}

const g = gen(1);
console.log(g.next());    // { value: 2, done: false }
console.log(g.next(10));   // { value: 12, done: false }，y = 10
console.log(g.next(20));  // { value: 23, done: true }，z = 20
```

**yield* 表达式**：
在 Generator 函数内部调用另一个 Generator 函数。

```javascript
function* foo() {
  yield 'a';
  yield 'b';
}

function* bar() {
  yield 'x';
  yield* foo();
  yield 'y';
}
// 等价于 yield 'x'; yield 'a'; yield 'b'; yield 'y';
```

**应用场景**：
1. 异步操作的同步化表达（async/await 的前身）
2. 控制流管理
3. 部署 Iterator 接口
4. 作为数据结构使用

**Generator 自动执行**：
Generator 函数需要手动调用 next()，可以配合 co 库或自执行。

**扩展问题**:
- Generator 和 async/await 有什么关系？
- Generator 如何实现异步编程？
- 什么是可迭代对象和迭代器？
- Generator 如何实现状态机？

---

## Q15: 数组的常用方法有哪些？（map/filter/reduce/forEach 等）

**考察点**: 数组常用方法的用法、区别、是否改变原数组

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**遍历方法**（不改变原数组）**：
- **forEach**：遍历数组，无返回值
- **map**：遍历数组，返回新数组
- **filter**：过滤数组，返回满足条件的新数组
- **reduce**：累加器，累计为一个值
- **some**：有一个满足就返回 true
- **every**：所有都满足才返回 true
- **find**：找到第一个满足条件的元素
- **findIndex**：找到第一个满足条件元素的索引
- **includes**：是否包含某个元素
- **flat**：扁平化数组
- **flatMap**：先 map 再 flat

**改变原数组的方法**：
- **push/pop**：末尾添加/删除
- **unshift/shift**：开头添加/删除
- **splice**：删除/替换/添加元素
- **sort**：排序
- **reverse**：反转
- **fill**：填充

**其他方法**：
- **slice**：截取数组（不改变原数组）
- **concat**：合并数组（不改变原数组）
- **join**：转字符串
- **indexOf/lastIndexOf**：查找索引

**答案解析**:

**reduce 的用法：
```javascript
const arr = [1, 2, 3, 4];

// map - 映射
const doubled = arr.map(x => x * 2); // [2, 4, 6, 8]

// filter - 过滤
const even = arr.filter(x => x % 2 === 0); // [2, 4]

// reduce - 累加
const sum = arr.reduce((acc, cur) => acc + cur, 0); // 10

// forEach - 遍历（无返回值）
arr.forEach(x => console.log(x));
```

**reduce 高级用法**：
```javascript
// 数组去重
const unique = arr.reduce((acc, cur) => {
  if (!acc.includes(cur)) acc.push(cur);
  return acc;
}, []);

// 统计次数
const count = arr.reduce((acc, cur) => {
  acc[cur] = (acc[cur] || 0) + 1;
  return acc;
}, {});

// 数组扁平化
const flatten = arr.reduce((acc, cur) => {
  return acc.concat(Array.isArray(cur) ? flatten(cur) : cur);
}, []);
```

**方法对比**：
- forEach 没有返回值，不能链式调用
- map 返回新数组，长度与原数组相同
- filter 返回满足条件的新数组
- reduce 最灵活，可以实现 map、filter 等功能

**扩展问题**:
- forEach 和 map 的区别？什么场景用哪个？
- reduce 可以实现哪些高级功能？
- 如何判断一个变量是不是数组？
- 数组的哪些方法会改变原数组？
- 如何实现数组的扁平化？

---

## Q16: 什么是柯里化函数？

**考察点**: 柯里化的概念、实现、应用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

柯里化（Currying）是把接受多个参数的函数变换成接受一个单一参数（最初函数的第一个参数）的函数，并且返回接受余下的参数且返回结果的新函数的技术。

简单说：柯里化就是将 `fn(a, b, c)` 变成 `fn(a)(b)(c)` 的形式。

**核心特点**：
- 参数复用
- 提前返回
- 延迟计算/运行

**应用场景**：
- 参数复用（固定部分参数）
- 延迟执行
- 函数式编程中的组合函数

**答案解析**:

**实现柯里化**：
```javascript
// 简单实现
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) {
      return fn.apply(this, args);
    } else {
      return function(...args2) {
        return curried.apply(this, [...args, ...args2]);
      };
    }
  };
}

// 使用示例
function add(a, b, c) {
  return a + b + c;
}

const curriedAdd = curry(add);
console.log(curriedAdd(1)(2)(3)); // 6
console.log(curriedAdd(1, 2)(3)); // 6
console.log(curriedAdd(1)(2, 3)); // 6
```

**参数复用示例**：
```javascript
function check(reg, txt) {
  return reg.test(txt);
}

const curriedCheck = curry(check);
const hasNumber = curriedCheck(/\d+/g);

console.log(hasNumber('test1')); // true
console.log(hasNumber('test'));  // false
```

**无限累加的柯里化**：
```javascript
function add(...args) {
  const fn = function(...args2) {
    return add(...args, ...args2);
  };
  fn.valueOf = function() {
    return args.reduce((a, b) => a + b, 0);
  };
  return fn;
}

console.log(add(1)(2)(3) == 6); // true
console.log(add(1, 2, 3) == 6);    // true
```

**柯里化和偏函数的区别**：
- 柯里化：将多参数函数转换为一系列单参数函数
- 偏函数：固定部分参数，产生另一个函数

**扩展问题**:
- 柯里化的好处是什么？
- 如何实现无限参数的柯里化？
- 柯里化和闭包有什么关系？
- lodash 的 curry 是怎么实现的？

---

## Q17: 如何实现继承？有哪些方式？

**考察点**: JavaScript 继承的多种实现方式、各自优缺点

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

JavaScript 实现继承的常见方式：

1. **原型链继承**：子类原型指向父类实例
2. **构造函数继承**：在子类构造函数中调用父类构造函数
3. **组合继承**：原型链 + 构造函数组合
4. **原型式继承**：Object.create() 实现
5. **寄生式继承**：在原型式继承基础上增强对象
6. **寄生组合式继承**：组合继承的优化
7. **ES6 Class extends**：ES6 语法糖

**答案解析**:

**1. 原型链继承**：
```javascript
function Parent() {
  this.name = 'parent';
}
Parent.prototype.say = function() { console.log('say');
};

function Child() {}
Child.prototype = new Parent();
// 缺点：所有实例共享父类属性，无法传参
```

**2. 构造函数继承**：
```javascript
function Parent(name) {
  this.name = name;
}
function Child(name) {
  Parent.call(this, name);
}
// 缺点：方法都在构造函数中定义，无法复用
// 优点：可以传参，不共享引用属性
```

**3. 组合继承**：
```javascript
function Parent(name) {
  this.name = name;
}
Parent.prototype.say = function() { console.log(this.name); };

function Child(name, age) {
  Parent.call(this, name); // 继承属性
  this.age = age;
}
Child.prototype = new Parent(); // 继承方法
Child.prototype.constructor = Child;
// 缺点：调用了两次父类构造函数
```

**4. 寄生组合式继承（最理想方式）**：
```javascript
function inheritPrototype(child, parent) {
  const prototype = Object.create(parent.prototype);
  prototype.constructor = child;
  child.prototype = prototype;
}
```

**5. ES6 Class 继承**：
```javascript
class Parent {
  constructor(name) {
    this.name = name;
  }
  say() { console.log(this.name); }
}

class Child extends Parent {
  constructor(name, age) {
    super(name); // 必须调用 super
    this.age = age;
  }
}
```

**各方式对比**：
| 方式 | 优点 | 缺点 |
|------|------|------|
| 原型链 | 简单易实现 | 引用属性共享，不能传参 |
| 构造函数 | 可传参，不共享引用 | 方法不能复用，每次创建实例 |
| 组合继承 | 融合两者优点 | 调用两次父类构造函数 |
| 寄生组合 | 最优方案 | 实现稍复杂 |
| ES6 Class | 语法清晰，标准 | 兼容性问题（可转译解决 |

**扩展问题**:
- ES6 的 Class 继承和 ES5 的继承有什么区别？
- super 关键字的原理是什么？
- 为什么寄生组合式继承为什么是最优的？
- Object.create() 的原理和实现？

---

## Q18: new 操作符的实现原理是什么？

**考察点**: new 操作符的执行过程、手动实现

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

new 操作符创建一个用户定义的对象类型的实例或具有构造函数的内置对象的实例。

**new 操作符的执行过程：
1. 创建一个新的空对象
2. 将新对象的 __proto__ 指向构造函数的 prototype
3. 将构造函数的 this 指向这个新对象
4. 执行构造函数代码
5. 如果构造函数返回对象，则返回该对象；否则返回新创建的对象

**答案解析**:

**手动实现 new**：
```javascript
function myNew(constructor, ...args) {
  // 1. 创建新对象，原型指向构造函数的 prototype
  const obj = Object.create(constructor.prototype);
  
  // 2. 绑定 this 执行构造函数
  const result = constructor.apply(obj, args);
  
  // 3. 如果构造函数返回对象则返回对象，否则返回新对象
  return (typeof result === 'object' && result !== null) ? result : obj;
}
```

**验证**：
```javascript
function Person(name, age) {
  this.name = name;
  this.age = age;
}
Person.prototype.sayName = function() {
  console.log(this.name);
};

const p = myNew(Person, 'Tom', 18);
console.log(p.name); // 'Tom'
p.sayName(); // 'Tom'
console.log(p instanceof Person); // true
```

**构造函数返回值的情况**：
```javascript
// 返回对象，返回对象
function Foo() {
  return { a: 1 };
}
console.log(new Foo()); // { a: 1 }

// 返回原始类型，忽略返回新对象
function Bar() {
  return 1;
}
console.log(new Bar()); // Bar {}

// 返回 null，忽略
function Baz() {
  return null;
}
console.log(new Baz()); // Baz {}
```

**相关问题**：
- 箭头函数不能作为构造函数使用 new 会报错，因为箭头函数没有 prototype。

**扩展问题**:
- 构造函数返回对象会怎样？返回原始值呢？
- 为什么箭头函数不能 new？
- new.target 是什么？有什么用？
- Object.create() 和 new 的区别？

---

## Q19: call、apply、bind 的区别和实现？

**考察点**: 三个方法的区别、使用场景、手动实现

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

三者都是用来改变函数 this 指向的方法。

**区别**：
| 方法 | 参数形式 | 执行方式 | 返回值 |
|------|----------|----------|--------|
| call | 多个参数列表 | 立即执行 | 执行结果 |
| apply | 参数数组 | 立即执行 | 执行结果 |
| bind | 多个参数列表 | 返回新函数 | 新函数 |

**使用场景**：
- call：用于确定参数个数时
- apply：用于参数个数不确定时，或需要数组传参
- bind：需要延迟执行时，或需要预设参数时

**答案解析**:

**call 实现**：
```javascript
Function.prototype.myCall = function(context, ...args) {
  context = context || window;
  const fn = Symbol('fn');
  context[fn] = this;
  const result = context[fn](...args);
  delete context[fn];
  return result;
};
```

**apply 实现**：
```javascript
Function.prototype.myApply = function(context, args) {
  context = context || window;
  const fn = Symbol('fn');
  context[fn] = this;
  const result = context[fn](...args);
  delete context[fn];
  return result;
};
```

**bind 实现**：
```javascript
Function.prototype.myBind = function(context, ...args1) {
  const self = this;
  return function F(...args2) {
    // new 调用时 this 指向实例
    if (this instanceof F) {
      return new self(...args1, ...args2);
    }
    return self.apply(context, [...args1, ...args2]);
  };
};
```

**使用示例**：
```javascript
function say(greeting) {
  console.log(`${greeting}, I'm ${this.name}`);
}

const person = { name: 'Tom' };

say.call(person, 'Hello');    // Hello, I'm Tom
say.apply(person, ['Hello']); // Hello, I'm Tom
const boundSay = say.bind(person, 'Hello');
boundSay(); // Hello, I'm Tom
```

**经典应用**：
```javascript
// 类数组转数组
const arr = Array.prototype.slice.call(arguments);

// 求数组最大值
Math.max.apply(null, [1, 2, 3]);

// 数组追加数组
Array.prototype.push.apply(arr1, arr2);
```

**扩展问题**:
- bind 多次绑定会怎样？
- call/apply/bind 对箭头函数有效吗？
- 如何实现一个完美的 bind？
- call 和 apply 性能上有区别吗？

---

## Q20: 什么是事件委托/事件代理？

**考察点**: 事件委托的原理、优缺点、应用场景

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

事件委托（Event Delegation），也叫事件代理，是利用事件冒泡机制，把一个元素的响应事件绑定到其父元素或祖先元素上，让父元素来监听子元素的事件响应。

**原理**：
- 事件冒泡：事件从最具体的元素开始，逐级向上传播到 DOM 树的机制。
- 利用 event.target 判断事件源，执行相应的处理逻辑。

**优点**：
- 减少内存消耗，大量子元素只需要绑定一个事件
- 可以动态绑定事件，新增元素自动有事件响应
- 简化了 DOM 更新与事件处理的绑定

**缺点**：
- 不冒泡的事件无法委托
- 层级过多可能影响性能
- 可能误判事件源

**应用场景**：
- 列表项很多，需要给每个列表项绑定事件
- 动态添加的元素需要绑定事件

**答案解析**:

**事件冒泡和事件流**：
DOM 事件流分为三个阶段：
1. 捕获阶段：从 window 向下传播到目标元素
2. 目标阶段：到达目标元素
3. 冒泡阶段：从目标元素向上冒泡到 window

事件委托利用的是冒泡阶段。

**实现事件委托**：
```javascript
// 给 ul 绑定点击事件，委托给所有 li
document.getElementById('list').addEventListener('click', function(e) {
  // 判断事件源是不是 li
  if (e.target.tagName.toLowerCase() === 'li') {
    console.log(e.target.innerHTML);
  }
});
```

**封装一个事件委托函数：
```javascript
function delegate(parent, eventType, selector, handler) {
  parent.addEventListener(eventType, function(e) {
    let target = e.target;
    while (target !== parent) {
      if (target.matches(selector)) {
        handler.call(target, e);
        break;
      }
      target = target.parentNode;
    }
  });
}
```

**不冒泡的事件无法委托，如：
- focus/blur（可以用 focusin/focusout 代替）
- mouseenter/mouseleave（可以用 mouseover/mouseout 代替）

**扩展问题**:
- 事件冒泡和事件捕获的区别？
- 如何阻止事件冒泡和默认行为？
- 事件委托的局限性有哪些？
- 如何实现一个完美的事件委托？
- 事件对象 target 和 currentTarget 的区别？

---

## Reference

1. MDN Web Docs - JavaScript 指南. https://developer.mozilla.org/zh-CN/docs/Web/JavaScript
   访问时间：2026-07-28

2. ECMAScript 2024 语言规范. https://tc39.es/ecma262/
   访问时间：2026-07-28

3. 阮一峰 - ES6 标准入门. https://es6.ruanyifeng.com/
   访问时间：2026-07-28

4. 掘金前端社区 - JavaScript 深入系列文章. https://juejin.cn/frontend
   访问时间：2026-07-28

5. 前端面试题精选 - GitHub. https://github.com/haizlin/fe-interview
   访问时间：2026-07-28

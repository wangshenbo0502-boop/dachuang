---
title: "Vue/React框架面试题（20题）"
category: "面试题"
type: "前端"
difficulty: "中等"
tags: ["Vue", "React", "前端框架", "响应式", "虚拟DOM"]
source: ["Vue官方文档", "React官方文档", "前端面试题库", "掘金前端社区"]
last_update: "2026-07-28"
---

# Vue/React 框架面试题（20题）

本文档收录了 Vue 和 React 框架核心的 20 道高频面试题，涵盖响应式原理、虚拟 DOM、生命周期、状态管理等核心知识点。

---

## Q1: Vue 的响应式原理是什么？（Object.defineProperty / Proxy）

**考察点**: Vue 响应式原理、Object.defineProperty 和 Proxy 的区别、Vue2 和 Vue3 响应式对比

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**Vue2 响应式原理（Object.defineProperty）**：
Vue2 通过 `Object.defineProperty()` 劫持对象属性的 getter 和 setter，在数据变化时通知更新。

核心流程：
1. **Observer**：遍历 data 对象的所有属性，使用 Object.defineProperty 把这些属性全部转为 getter/setter
2. **Dep**：每个属性对应一个 Dep 实例，负责收集依赖和通知更新
3. **Watcher**：模板编译过程中会创建 Watcher，Watcher 会在 getter 中收集依赖
4. 当数据变化时，setter 触发，通知 Dep 中的所有 Watcher 更新视图

**Vue3 响应式原理（Proxy）**：
Vue3 使用 `Proxy` 代理整个对象，而不是劫持单个属性。

优势：
- 可以监听整个对象，包括新增属性和删除属性
- 可以监听数组索引和 length 变化
- 性能更好，不需要递归遍历所有属性
- 支持 Map、Set、WeakMap、WeakSet

**答案解析**:

**Vue2 响应式实现思路**：

```javascript
// 简化版响应式实现
function defineReactive(obj, key, val) {
  const dep = new Dep();
  Object.defineProperty(obj, key, {
    get() {
      // 收集依赖
      if (Dep.target) {
        dep.addSub(Dep.target);
      }
      return val;
    },
    set(newVal) {
      if (newVal === val) return;
      val = newVal;
      // 通知更新
      dep.notify();
    }
  });
}

class Dep {
  constructor() {
    this.subs = [];
  }
  addSub(watcher) {
    this.subs.push(watcher);
  }
  notify() {
    this.subs.forEach(watcher => watcher.update());
  }
}
```

**Vue2 的局限性**：
1. 不能监听对象属性的新增和删除（需要用 `Vue.set` / `Vue.delete`）
2. 不能监听数组索引和 length 变化（Vue 重写了 7 个数组方法）
3. 初始化时需要深度遍历，性能开销大

**Vue3 Proxy 响应式**：

```javascript
const reactive = (target) => {
  return new Proxy(target, {
    get(target, key, receiver) {
      const result = Reflect.get(target, key, receiver);
      track(target, key); // 收集依赖
      // 深层对象懒代理
      return typeof result === 'object' ? reactive(result) : result;
    },
    set(target, key, value, receiver) {
      const result = Reflect.set(target, key, value, receiver);
      trigger(target, key); // 触发更新
      return result;
    },
    deleteProperty(target, key) {
      const result = Reflect.deleteProperty(target, key);
      trigger(target, key);
      return result;
    }
  });
};
```

**扩展问题**:
- Vue2 为什么不能检测数组索引变化？
- Vue3 的 Proxy 相比 Object.defineProperty 有哪些优势？
- Vue 的依赖收集是在什么时候进行的？
- Vue3 的响应式有哪几种 API？（reactive/ref/toRefs 等）

---

## Q2: Vue 的虚拟 DOM 和 Diff 算法

**考察点**: 虚拟 DOM 原理、Diff 算法策略、key 的作用

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**虚拟 DOM（Virtual DOM）**：
虚拟 DOM 是用 JavaScript 对象来描述 DOM 结构的一种方式。当状态变化时，先在虚拟 DOM 上进行对比，找出差异，最后只更新有变化的真实 DOM，提高性能。

虚拟 DOM 的优点：
- 减少真实 DOM 操作次数，提高性能
- 跨平台能力（可以渲染到其他平台）
- 声明式编程，开发者不需要关心 DOM 操作细节

**Diff 算法**：
Diff 算法是对比两棵虚拟 DOM 树差异的算法。Vue 的 Diff 算法采用同层比较策略。

核心策略：
1. **同层比较**：只比较同一层级的节点，不跨层级比较
2. **同类型比较**：不同类型的节点直接替换
3. **key 标识**：通过 key 来判断节点是否可以复用

**答案解析**:

**虚拟 DOM 结构示例**：

```javascript
// 虚拟 DOM 对象
const vnode = {
  tag: 'div',
  props: { id: 'app' },
  children: [
    { tag: 'p', children: 'hello' }
  ]
};

// 对应的真实 DOM
// <div id="app"><p>hello</p></div>
```

**Vue2 的双端 Diff 算法**：
Vue2 使用双指针比较，四个指针分别指向新旧列表的首尾。

比较步骤：
1. 旧首 vs 新首
2. 旧尾 vs 新尾
3. 旧首 vs 新尾
4. 旧尾 vs 新首
5. 都不匹配时，用 key 建立索引表查找

**Vue3 的 Diff 算法优化**：
Vue3 采用最长递增子序列（LIS）算法优化移动次数。

核心优化：
1. 先处理首尾相同的节点（双端比较）
2. 对中间部分使用最长递增子序列算法
3. 最长递增子序列中的节点不需要移动
4. 只移动不在最长递增子序列中的节点

```javascript
// 最长递增子序列示例
// 旧：A B C D E
// 新：B C D A E
// 最长递增子序列：B C D E（索引 1,2,3,4）
// 只需要把 A 移动到正确位置
```

**为什么 Diff 算法时间复杂度从 O(n³) 降到 O(n)**：
- 同层比较：O(n) 遍历一次
- 通过 key 建立映射表：O(n)
- 总共 O(n) 时间复杂度

**扩展问题**:
- 虚拟 DOM 一定比真实 DOM 快吗？
- Vue2 和 Vue3 的 Diff 算法有什么区别？
- 为什么虚拟 DOM 能提高性能？
- key 的作用是什么？为什么不能用 index 作为 key？

---

## Q3: Vue 组件通信的方式有哪些？

**考察点**: 组件通信的多种方式、适用场景、父子/兄弟/跨层级通信

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

Vue 组件通信的常见方式：

**父子组件通信**：
1. **props / $emit**：父传子用 props，子传父用 $emit 触发事件
2. **v-model**：语法糖，本质是 props + emit
3. **.sync 修饰符**：Vue2 中的语法糖，Vue3 用 v-model:xxx 代替
4. **$parent / $children**：直接访问父子组件实例（不推荐）
5. **ref**：通过 ref 获取组件实例

**兄弟组件通信**：
6. **EventBus**：事件总线，通过共同的实例触发和监听事件
7. **共同父组件中转**：通过父组件做桥梁

**跨层级通信**：
8. **provide / inject**：祖先组件提供数据，后代组件注入使用
9. **Vuex / Pinia**：状态管理库
10. **$attrs / $listeners**：隔代传递属性和事件（Vue3 中 $listeners 移除）

**答案解析**:

**1. props / $emit**：
```vue
<!-- 父组件 -->
<Child :msg="message" @update="handleUpdate" />

<!-- 子组件 -->
props: ['msg'],
methods: {
  send() { this.$emit('update', 'new value'); }
}
```

**2. v-model**：
```vue
<!-- Vue3 中 -->
<Child v-model:msg="message" />
<!-- 等价于 -->
<Child :msg="message" @update:msg="message = $event" />
```

**3. provide / inject**：
```javascript
// 祖先组件
provide() {
  return { theme: 'dark' };
}

// 后代组件
inject: ['theme']
```

**4. EventBus**：
```javascript
// event-bus.js
import Vue from 'vue';
export const EventBus = new Vue();

// 组件 A 发送
EventBus.$emit('event', data);

// 组件 B 接收
EventBus.$on('event', callback);
```

**5. Vuex / Pinia**：
适用于大型应用，集中式状态管理。

**使用场景总结**：
- 父子：props / emit / v-model
- 兄弟：EventBus / 父组件中转 / Vuex
- 跨多层：provide/inject / Vuex/Pinia
- 全局状态：Vuex / Pinia

**扩展问题**:
- props 是单向数据流还是双向？为什么？
- provide/inject 和 Vuex 有什么区别？
- Vue3 中组件通信有哪些变化？
- 如何实现祖孙组件通信？

---

## Q4: Vue 的生命周期钩子函数有哪些？

**考察点**: Vue 生命周期各阶段、常用钩子、使用场景

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**Vue2 生命周期**：

| 阶段 | 钩子函数 | 说明 |
|------|----------|------|
| 创建 | beforeCreate | 实例创建前，data 和 methods 不可用 |
| 创建 | created | 实例创建完成，data 和 methods 可用，DOM 不可用 |
| 挂载 | beforeMount | 挂载前，模板编译完成，DOM 未渲染 |
| 挂载 | mounted | 挂载完成，DOM 可用 |
| 更新 | beforeUpdate | 数据更新前，DOM 未更新 |
| 更新 | updated | 数据更新后，DOM 已更新 |
| 销毁 | beforeDestroy | 销毁前，实例仍可用 |
| 销毁 | destroyed | 销毁完成，所有东西解绑 |

**Vue3 生命周期（组合式 API）**：
- setup 代替了 beforeCreate 和 created
- onBeforeMount / onMounted
- onBeforeUpdate / onUpdated
- onBeforeUnmount / onUnmounted

**答案解析**:

**Vue2 生命周期流程**：
```
new Vue()
    ↓
beforeCreate（初始化事件和生命周期）
    ↓
created（数据观测、属性和方法运算完成）
    ↓
判断是否有 el / template
    ↓
beforeMount（模板编译完成）
    ↓
mounted（真实 DOM 挂载完成）
    ↓
数据变化 → beforeUpdate → 虚拟 DOM 重新渲染 → updated
    ↓
$destroy() → beforeDestroy → destroyed
```

**各阶段使用场景**：
- **created**：发送 ajax 请求、初始化数据（不依赖 DOM）
- **mounted**：操作 DOM、获取 DOM 元素、初始化第三方库
- **beforeDestroy**：清除定时器、解绑事件、取消订阅
- **updated**：数据更新后需要操作 DOM 时

**Vue3 生命周期变化**：
```javascript
// 组合式 API 写法
import { onMounted, onUnmounted } from 'vue';

setup() {
  onMounted(() => {
    console.log('mounted');
  });
  
  onUnmounted(() => {
    console.log('unmounted');
  });
}
```

注意：Vue3 中 setup 在 beforeCreate 和 created 之前执行，所以不需要这两个钩子。

**扩展问题**:
- created 和 mounted 的区别？什么时候用哪个？
- 父子组件的生命周期执行顺序是什么？
- 异步请求应该放在哪个生命周期？
- keep-alive 组件的生命周期有哪些？

---

## Q5: computed 和 watch 的区别是什么？

**考察点**: computed 和 watch 的区别、使用场景、实现原理

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**computed（计算属性）**：
- 基于它的依赖进行缓存，依赖不变时不会重新计算
- 有缓存，依赖不变直接返回缓存值
- 必须有返回值
- 适合做数据的转换和派生
- 不支持异步

**watch（侦听器）**：
- 监听数据变化，数据变化时执行回调
- 没有缓存，每次变化都会执行
- 不需要返回值
- 适合做数据变化后的操作（如发送请求、操作 DOM）
- 支持异步操作

**核心区别**：
| 特性 | computed | watch |
|------|----------|-------|
| 缓存 | 有缓存 | 无缓存 |
| 返回值 | 必须有 | 不需要 |
| 异步 | 不支持 | 支持 |
| 用途 | 派生数据 | 监听变化执行操作 |
| 调用时机 | 访问时计算 | 数据变化时执行 |

**答案解析**:

**computed 示例**：
```javascript
computed: {
  fullName() {
    return this.firstName + ' ' + this.lastName;
  }
}
// 只有 firstName 或 lastName 变化时才重新计算
// 多次访问 fullName 会返回缓存结果
```

**watch 示例**：
```javascript
watch: {
  searchText: {
    handler(newVal) {
      this.fetchData(newVal);
    },
    immediate: true,  // 立即执行一次
    deep: true       // 深度监听
  }
}
```

**computed 缓存原理**：
computed 属性有一个 dirty 属性标记是否需要重新计算。
- 依赖变化时，dirty = true
- 访问 computed 时，dirty 为 true 则重新计算，然后 dirty = false
- dirty 为 false 时直接返回缓存值

**使用场景建议**：
- 一个数据受多个数据影响 → computed（如总价 = 单价 × 数量）
- 一个数据变化影响多个数据 → watch（如搜索关键字变化触发搜索）

**Vue3 中的写法**：
```javascript
import { computed, watch, watchEffect } from 'vue';

const fullName = computed(() => first.value + last.value);

watch(count, (newVal, oldVal) => {
  console.log('count changed');
});

watchEffect(() => {
  console.log(count.value);
});
```

**扩展问题**:
- computed 的缓存原理是什么？
- watch 的 deep 和 immediate 选项有什么用？
- watchEffect 和 watch 的区别？
- computed 和 methods 的区别？

---

## Q6: v-if 和 v-show 的区别是什么？

**考察点**: v-if 和 v-show 的区别、使用场景、性能对比

**难度**: 简单

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

| 特性 | v-if | v-show |
|------|------|--------|
| 控制方式 | 销毁/重建 DOM 元素 | 切换 display:none |
| 编译 | 条件为 false 时不编译 | 始终编译，只是 CSS 控制显示 |
| 切换开销 | 高（DOM 操作） | 低（CSS 切换） |
| 初始开销 | 低（条件为 false 时不渲染） | 高（始终渲染） |
| 使用场景 | 切换不频繁 | 切换频繁 |
| v-for 优先级 | v-for 优先级高于 v-if | 同左 |

**答案解析**:

**v-if 原理**：
- 条件为 true 时渲染元素，条件为 false 时完全不渲染或销毁
- 切换时会触发组件的完整生命周期（销毁/重建）
- 支持 `<template>` 标签使用

**v-show 原理**：
- 无论条件真假都会渲染元素
- 通过 CSS 的 `display` 属性控制显示隐藏
- 条件变化时只修改 style，不会触发组件生命周期

```html
<!-- v-if：DOM 中完全不存在 -->
<div v-if="false">v-if test</div>

<!-- v-show：DOM 存在，只是 display: none -->
<div v-show="false">v-show test</div>
```

**性能对比**：
- 初始渲染：v-if 开销小（条件为 false 时不渲染），v-show 开销大
- 切换开销：v-if 开销大（DOM 操作），v-show 开销小（CSS）
- 频繁切换：用 v-show
- 很少切换或条件很少变化：用 v-if

**注意事项**：
- v-if 和 v-for 一起使用时，v-for 优先级更高（Vue2 中）
- Vue3 中 v-if 优先级高于 v-for
- 不推荐 v-if 和 v-for 一起使用，性能差且逻辑混乱

**扩展问题**:
- v-if 和 v-for 为什么不推荐一起用？
- Vue2 和 Vue3 中 v-if 和 v-for 的优先级有什么不同？
- 如何优化 v-if 和 v-for 一起使用的情况？
- v-show 和 CSS 的 display:none 有什么区别？

---

## Q7: v-for 为什么要加 key？

**考察点**: key 的作用、Diff 算法、为什么不能用 index 作为 key

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**key 的作用**：
key 是给虚拟 DOM 节点的唯一标识，Diff 算法通过 key 来判断节点是否可以复用，从而更高效地更新 DOM。

**为什么需要 key**：
1. **提高 Diff 效率**：有 key 时可以快速定位到相同节点，减少 DOM 操作
2. **保证状态正确**：避免节点复用导致的状态混乱问题
3. **正确触发过渡动画**：Vue 的 transition-group 需要 key 来识别节点

**为什么不能用 index 作为 key**：
当列表顺序发生变化（如插入、删除、排序）时，index 作为 key 会导致：
1. 节点复用错误，状态错乱
2. 增加不必要的 DOM 操作，性能变差
3. 表单输入框等有状态的元素状态丢失

**答案解析**:

**Diff 算法中 key 的作用**：
没有 key 时，Diff 算法只能按顺序逐个比较，可能会做很多不必要的 DOM 操作。
有 key 时，可以通过 key 快速找到对应的节点，判断是否可以复用。

**index 作为 key 的问题示例**：
```html
<!-- 初始列表 -->
<ul>
  <li v-for="(item, index) in list" :key="index">
    <input type="checkbox"> {{ item.name }}
  </li>
</ul>
```

初始状态：
- 第1项：A（勾选）
- 第2项：B（未勾选）
- 第3项：C（未勾选）

在开头插入 D 后：
- index 0: D（复用了原来 A 的节点，勾选状态保留了 → 错误）
- index 1: A（复用了原来 B 的节点，未勾选 → 错误）
- index 2: B（复用了原来 C 的节点，未勾选）
- index 3: C（新建节点）

正确做法：使用唯一 id 作为 key
```html
<li v-for="item in list" :key="item.id">{{ item.name }}</li>
```

**key 的最佳实践**：
- 使用唯一且稳定的 id 作为 key
- 不要用 index 作为 key（除非列表不会增删排序）
- 不要用随机数作为 key（每次渲染都变，无法复用）
- v-for 和 v-if 一起用时，key 要正确设置

**扩展问题**:
- key 在 Diff 算法中具体是怎么工作的？
- 没有 key 和用 index 作为 key 哪个更差？
- 为什么 Vue 推荐用 key？
- 列表渲染时 key 必须是唯一的吗？

---

## Q8: nextTick 的原理和使用场景是什么？

**考察点**: nextTick 原理、事件循环、使用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

**nextTick 是什么**：
`Vue.nextTick()` 是在下次 DOM 更新循环结束之后执行延迟回调。在修改数据之后立即使用这个方法，获取更新后的 DOM。

**原理**：
Vue 在更新 DOM 时是异步执行的。当数据变化时，Vue 不会立即更新 DOM，而是将 watcher 更新推入一个队列中，等下一个事件循环 tick 时统一执行。nextTick 就是在 DOM 更新后执行回调。

nextTick 的实现优先使用微任务（Promise.then > MutationObserver > setImmediate > setTimeout）。

**使用场景**：
1. 获取更新后的 DOM 元素
2. 在 created 中操作 DOM（放在 nextTick 中）
3. 第三方库初始化需要 DOM 时
4. 某些需要等待 DOM 更新后的操作

**答案解析**:

**为什么需要 nextTick**：
Vue 采用异步更新队列策略，数据变化不会立即更新 DOM，而是缓存起来批量更新，避免频繁操作 DOM。

```javascript
// 修改数据
vm.message = 'new message';
// DOM 还没更新
console.log(vm.$el.textContent); // 'old message'

// 使用 nextTick
Vue.nextTick(() => {
  // DOM 已更新
  console.log(vm.$el.textContent); // 'new message'
});
```

**nextTick 实现原理**：

```javascript
// 简化版 nextTick 实现
let callbacks = [];
let pending = false;

function flushCallbacks() {
  pending = false;
  const copies = callbacks.slice(0);
  callbacks = [];
  for (let i = 0; i < copies.length; i++) {
    copies[i]();
  }
}

let timerFunc;
// 优先使用 Promise
if (typeof Promise !== 'undefined') {
  const p = Promise.resolve();
  timerFunc = () => {
    p.then(flushCallbacks);
  };
} else if (typeof MutationObserver !== 'undefined') {
  // MutationObserver
} else if (typeof setImmediate !== 'undefined') {
  timerFunc = () => setImmediate(flushCallbacks);
} else {
  timerFunc = () => setTimeout(flushCallbacks, 0);
}

function nextTick(cb) {
  callbacks.push(cb);
  if (!pending) {
    pending = true;
    timerFunc();
  }
}
```

**事件循环中的位置**：
- 修改数据 → watcher 入队 → nextTick 回调入队（微任务）
- 当前宏任务执行完 → 执行所有微任务 → 先更新 DOM → 执行 nextTick 回调

**扩展问题**:
- nextTick 是宏任务还是微任务？
- nextTick 和 setTimeout 的区别？
- 为什么 nextTick 优先用微任务？
- nextTick 在 Vue3 中有变化吗？

---

## Q9: Vue Router 的两种模式和区别是什么？

**考察点**: hash 模式和 history 模式的原理、区别、优缺点

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

**hash 模式**：
- URL 中带 `#` 号，如 `http://example.com/#/home`
- 原理：监听 `hashchange` 事件
- 特点：hash 变化不会触发页面刷新，只是前端路由变化
- 优点：兼容性好，不需要服务端配置
- 缺点：URL 不美观，有 # 号

**history 模式**：
- URL 正常显示，如 `http://example.com/home`
- 原理：使用 HTML5 的 `pushState` 和 `replaceState` API
- 特点：修改 URL 但不刷新页面
- 优点：URL 美观，没有 # 号
- 缺点：需要服务端配置支持，刷新时会 404

**答案解析**:

**hash 模式原理**：
```javascript
// hash 变化不刷新页面
window.location.hash = '/home';

// 监听 hash 变化
window.addEventListener('hashchange', () => {
  console.log(window.location.hash);
});
```

**history 模式原理**：
```javascript
// pushState 修改 URL 但不刷新
history.pushState({ path: '/home' }, '', '/home');

// replaceState 替换当前历史记录
history.replaceState({ path: '/about' }, '', '/about');

// 监听前进后退
window.addEventListener('popstate', (e) => {
  console.log(e.state);
});
```

**history 模式的服务端配置**：
由于 history 模式下刷新页面会真实请求服务器，需要服务端配置将所有请求都重定向到 index.html。

Nginx 配置：
```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

Apache 配置：
```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

**其他区别**：
| 特性 | hash 模式 | history 模式 |
|------|-----------|--------------|
| URL 外观 | 有 # | 无 # |
| 兼容性 | IE8+ | IE10+ |
| 服务端配置 | 不需要 | 需要 |
| 刷新 | 正常 | 404（需配置） |
| 锚点功能 | 冲突 | 正常 |

**扩展问题**:
- history 模式刷新 404 怎么解决？
- pushState 和 hashchange 的区别？
- 如何实现一个简单的前端路由？
- Vue Router 还有哪些模式？

---

## Q10: Vuex 的核心概念和使用场景是什么？

**考察点**: Vuex 核心概念、数据流、使用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

**Vuex 是什么**：
Vuex 是 Vue.js 的状态管理库，采用集中式存储管理应用的所有组件的状态。

**核心概念**：
1. **State**：状态数据，单一状态树
2. **Getters**：派生状态，类似 computed
3. **Mutations**：修改状态的唯一方式，必须是同步函数
4. **Actions**：提交 mutation，可以包含异步操作
5. **Modules**：模块化，将 store 分割成模块

**数据流**：
`组件 → dispatch(Action) → commit(Mutation) → 修改 State → 视图更新`

**使用场景**：
- 中大型单页应用
- 多个组件共享状态
- 组件间状态需要同步
- 需要持久化状态

**答案解析**:

**Vuex 数据流图示**：
```
        ┌─────────────┐
        │   Actions   │
        └──────┬──────┘
               │ dispatch
               ▼
        ┌─────────────┐
        │  Mutations  │
        └──────┬──────┘
               │ commit
               ▼
        ┌─────────────┐
        │    State    │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │   视图渲染   │
        └─────────────┘
```

**基本使用**：
```javascript
// store/index.js
import Vuex from 'vuex';

export default new Vuex.Store({
  state: { count: 0 },
  getters: {
    doubleCount: state => state.count * 2
  },
  mutations: {
    increment(state, payload) {
      state.count += payload;
    }
  },
  actions: {
    asyncIncrement({ commit }, payload) {
      setTimeout(() => {
        commit('increment', payload);
      }, 1000);
    }
  },
  modules: {
    user: {
      namespaced: true,
      state: { name: 'Tom' }
    }
  }
});
```

**为什么 Mutation 必须是同步的**：
- 为了 devtools 能够准确追踪状态变化
- 异步操作放在 Actions 中处理
- 保证状态可追踪、可调试

**Vue3 中的 Pinia**：
Pinia 是 Vue3 推荐的状态管理库，相比 Vuex：
- 更简洁的 API
- 更好的 TypeScript 支持
- 不需要 mutations
- 模块化更简单

**扩展问题**:
- Vuex 为什么要分 Action 和 Mutation？
- Vuex 和 localStorage 的区别？
- Vuex 的模块有什么用？namespaced 是什么？
- Pinia 和 Vuex 有什么区别？
- Vuex 状态持久化怎么实现？

---

## Q11: React 的生命周期有哪些？（类组件 + 函数组件 Hooks）

**考察点**: React 生命周期各阶段、常用方法、Hooks 对应关系

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**类组件生命周期**：

| 阶段 | 方法 | 说明 |
|------|------|------|
| 挂载 | constructor | 构造函数，初始化 state 和绑定方法 |
| 挂载 | static getDerivedStateFromProps | props 变化时更新 state |
| 挂载 | render | 渲染组件 |
| 挂载 | componentDidMount | 挂载完成，DOM 可用 |
| 更新 | static getDerivedStateFromProps | props/state 变化触发 |
| 更新 | shouldComponentUpdate | 是否需要更新，返回布尔值 |
| 更新 | render | 重新渲染 |
| 更新 | getSnapshotBeforeUpdate | 更新前获取 DOM 快照 |
| 更新 | componentDidUpdate | 更新完成 |
| 卸载 | componentWillUnmount | 卸载前清理 |

**函数组件 Hooks 对应**：
- `useEffect` 可以模拟 componentDidMount + componentDidUpdate + componentWillUnmount
- 没有直接对应 constructor 的，可使用 useState 初始化

**答案解析**:

**类组件完整生命周期**：

```
挂载阶段：
constructor → getDerivedStateFromProps → render → componentDidMount

更新阶段（props/state 变化）：
getDerivedStateFromProps → shouldComponentUpdate → render → getSnapshotBeforeUpdate → componentDidUpdate

卸载阶段：
componentWillUnmount
```

**常用生命周期使用场景**：
- **componentDidMount**：发送请求、操作 DOM、初始化第三方库
- **componentDidUpdate**：依赖 DOM 更新后的操作
- **componentWillUnmount**：清除定时器、解绑事件、取消订阅
- **shouldComponentUpdate**：性能优化，避免不必要的渲染

**useEffect 模拟生命周期**：
```javascript
import { useEffect } from 'react';

// componentDidMount
useEffect(() => {
  console.log('mounted');
}, []);

// componentDidUpdate（依赖变化时）
useEffect(() => {
  console.log('updated');
}, [count]);

// componentWillUnmount
useEffect(() => {
  return () => {
    console.log('unmounted');
  };
}, []);
```

**废弃的生命周期**（React 16.3 后逐步废弃）：
- componentWillMount
- componentWillReceiveProps
- componentWillUpdate

这些生命周期容易导致 bug，且与未来的 React 特性不兼容。

**扩展问题**:
- componentDidMount 和 useEffect 的区别？
- getDerivedStateFromProps 为什么是 static 的？
- 为什么 componentWillReceiveProps 被废弃了？
- useEffect 和 useLayoutEffect 的区别？

---

## Q12: React Hooks 的常用 Hooks 有哪些？

**考察点**: 常用 Hooks 的用法、使用规则、注意事项

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**基础 Hooks**：
1. **useState**：状态管理
2. **useEffect**：副作用处理
3. **useContext**：Context 消费

**额外 Hooks**：
4. **useReducer**：复杂状态管理
5. **useCallback**：缓存函数
6. **useMemo**：缓存值
7. **useRef**：获取 DOM 或保存可变值
8. **useImperativeHandle**：暴露给父组件的实例值
9. **useLayoutEffect**：DOM 变更后同步执行
10. **useDebugValue**：自定义 Hook 标签

**Hooks 使用规则**：
- 只能在函数组件最顶层调用
- 只能在 React 函数组件或自定义 Hook 中调用
- 依赖数组要正确填写

**答案解析**:

**useState**：
```javascript
const [count, setCount] = useState(0);
// 函数式更新
setCount(prevCount => prevCount + 1);
```

**useEffect**：
```javascript
// 每次渲染后执行
useEffect(() => {
  document.title = `Count: ${count}`;
});

// 仅挂载时执行（空依赖）
useEffect(() => {
  fetchData();
}, []);

// 依赖变化时执行
useEffect(() => {
  fetchUser(userId);
}, [userId]);

// 清理函数
useEffect(() => {
  const timer = setInterval(() => {}, 1000);
  return () => clearInterval(timer);
}, []);
```

**useCallback 和 useMemo**：
```javascript
// useCallback 缓存函数
const handleClick = useCallback(() => {
  setCount(count + 1);
}, [count]);

// useMemo 缓存计算值
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);
```

**useRef**：
```javascript
const inputRef = useRef(null);
const countRef = useRef(0); // 保存不需要触发渲染的值

useEffect(() => {
  inputRef.current.focus();
}, []);
```

**useReducer**：
```javascript
const initialState = { count: 0 };
function reducer(state, action) {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 };
    case 'decrement': return { count: state.count - 1 };
    default: return state;
  }
}

const [state, dispatch] = useReducer(reducer, initialState);
```

**扩展问题**:
- useState 和 useReducer 的区别和选择？
- useCallback 和 useMemo 的区别？
- useRef 和 useState 的区别？
- 为什么不能在条件语句中使用 Hooks？
- 如何实现一个自定义 Hook？

---

## Q13: useEffect 和 useLayoutEffect 的区别是什么？

**考察点**: 两个 Hook 的区别、执行时机、使用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

| 特性 | useEffect | useLayoutEffect |
|------|-----------|-----------------|
| 执行时机 | 浏览器绘制之后异步执行 | DOM 更新后、浏览器绘制之前同步执行 |
| 阻塞渲染 | 不阻塞 | 会阻塞浏览器绘制 |
| 使用场景 | 大多数副作用操作 | 需要操作 DOM 且避免闪烁 |
| 性能 | 更好 | 可能影响性能 |

**useEffect**：
- 在组件渲染到屏幕之后异步执行
- 不会阻塞浏览器绘制
- 适合数据请求、订阅、定时器等

**useLayoutEffect**：
- 在 DOM 更新后、浏览器绘制前同步执行
- 会阻塞浏览器绘制
- 适合需要读取 DOM 布局或同步修改 DOM 的场景

**答案解析**:

**执行时机对比**：
```
组件状态更新
    ↓
render 阶段（计算虚拟 DOM）
    ↓
commit 阶段（更新真实 DOM）
    ↓
useLayoutEffect 同步执行（此时 DOM 已更新但未绘制）
    ↓
浏览器绘制（Paint）
    ↓
useEffect 异步执行
```

**useLayoutEffect 使用场景**：

1. **需要读取 DOM 后立即修改**：
```javascript
useLayoutEffect(() => {
  const height = ref.current.offsetHeight;
  // 根据高度做调整，避免闪烁
  ref.current.style.marginTop = `${-height / 2}px`;
}, []);
```

2. **避免视觉闪烁**：
如果在 useEffect 中修改 DOM 样式，用户可能会看到闪烁（先看到旧的，再看到新的），useLayoutEffect 可以避免。

**性能考虑**：
- 优先使用 useEffect，因为它不会阻塞浏览器渲染
- 只有当确实需要在绘制前操作 DOM 时才用 useLayoutEffect
- useLayoutEffect 中的代码执行时间长会导致页面卡顿

**类组件对应关系**：
- useEffect 对应 componentDidMount + componentDidUpdate（异步）
- useLayoutEffect 对应 componentDidMount + componentDidUpdate（同步）

**扩展问题**:
- 什么情况下必须用 useLayoutEffect？
- useLayoutEffect 和 componentDidMount 的执行时机一样吗？
- 为什么 useEffect 是异步执行的？
- 服务端渲染（SSR）中 useLayoutEffect 会有什么问题？

---

## Q14: 什么是虚拟 DOM？React Diff 算法是什么？

**考察点**: 虚拟 DOM 概念、React Diff 算法策略、Fiber 架构

**难度**: 困难

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**虚拟 DOM**：
虚拟 DOM 是用 JavaScript 对象来描述真实 DOM 结构的一种技术。状态变化时，先比较新旧虚拟 DOM 的差异，再将差异批量更新到真实 DOM 上。

优点：
- 减少 DOM 操作次数，提高性能
- 声明式编程，开发者无需关心 DOM 操作
- 跨平台能力（React Native 等）

**React Diff 算法**：
React 的 Diff 算法采用三个策略将 O(n³) 复杂度降到 O(n)：

1. **Tree Diff（同层比较）**：只比较同一层级的节点
2. **Component Diff（组件比较）**：
   - 同一类型组件，继续比较子节点
   - 不同类型组件，直接替换整个组件
3. **Element Diff（元素比较）**：通过 key 来判断节点是否可复用

**答案解析**:

**虚拟 DOM 结构**：
```javascript
// 虚拟 DOM 对象（React Element）
const element = {
  type: 'div',
  props: {
    className: 'container',
    children: [
      { type: 'p', props: { children: 'Hello' } }
    ]
  }
};
```

**Diff 三个策略详解**：

1. **Tree Diff**：
   - 只对同层级节点比较
   - 节点跨层级移动时，先删除再创建
   - 因为 DOM 节点跨层级移动操作很少

2. **Component Diff**：
   - 相同类型组件：按原策略继续比较子树
   - 不同类型组件：直接替换整个组件树

3. **Element Diff**：
   - 同一层级的子节点通过 key 来识别
   - 有三种操作：插入、移动、删除

**React Fiber 架构**：
React 16 引入 Fiber 架构，将渲染工作分片：
- 可中断的渲染：将长任务分片，避免阻塞主线程
- 优先级调度：高优先级任务优先处理
- 双缓存技术：current 树和 workInProgress 树

Fiber 的 Diff 发生在 reconciliation 阶段，这个阶段是可中断的。

**key 的作用**：
- 帮助 React 识别哪些元素改变了
- 列表渲染时必须有唯一 key
- 不建议用 index 作为 key（列表变化时可能导致性能问题和状态错误）

**扩展问题**:
- 虚拟 DOM 一定比真实 DOM 快吗？
- React 的 Diff 和 Vue 的 Diff 有什么区别？
- Fiber 架构解决了什么问题？
- 为什么 Diff 算法的时间复杂度是 O(n)？
- React 18 的并发模式和 Diff 有什么关系？

---

## Q15: React 中 setState 是同步还是异步？

**考察点**: setState 执行机制、批量更新、不同场景下的表现

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**结论**：setState 在 React 控制的事件处理函数和生命周期中是异步的，在原生事件和 setTimeout 等异步操作中是同步的。

**为什么是异步（批量更新）**：
- 性能优化：多次 setState 合并为一次更新，减少重渲染
- 保持状态一致性：避免中间状态导致的问题
- 为后续的并发模式打基础

**不同场景下的表现**：
1. **React 合成事件中**：异步（批量更新）
2. **生命周期中**：异步（批量更新）
3. **setTimeout/setInterval 中**：同步
4. **原生事件中**：同步
5. **Promise.then 中**：同步

**答案解析**:

**合成事件中的异步更新**：
```javascript
class App extends React.Component {
  state = { count: 0 };
  
  handleClick = () => {
    this.setState({ count: this.state.count + 1 });
    console.log(this.state.count); // 0，异步，还没更新
    
    this.setState({ count: this.state.count + 1 });
    console.log(this.state.count); // 还是 0
    
    // 多次 setState 会合并，最终只 +1
  };
}
```

**setTimeout 中的同步更新**：
```javascript
handleClick = () => {
  setTimeout(() => {
    this.setState({ count: this.state.count + 1 });
    console.log(this.state.count); // 1，同步更新了
  }, 0);
};
```

**setState 的第二个参数**：
```javascript
this.setState({ count: this.state.count + 1 }, () => {
  console.log(this.state.count); // 回调中获取最新值
});
```

**函数式 setState**：
```javascript
// 如果新状态依赖旧状态，使用函数式更新
this.setState((prevState) => ({
  count: prevState.count + 1
}));
```

**批量更新原理**：
React 有一个 `isBatchingUpdates` 变量，在 React 事件处理和生命周期中设为 true，此时 setState 不会立即更新，而是放入队列。

**React 18 的变化**：
React 18 引入自动批处理（Automatic Batching），在 Promise、setTimeout、原生事件中也会批量更新。

**扩展问题**:
- 为什么 setState 要设计成异步的？
- 如何获取 setState 更新后的值？
- React 18 的自动批处理是什么？
- setState 的批量更新原理是什么？
- useState 的更新是同步还是异步？

---

## Q16: React 组件通信方式有哪些？

**考察点**: React 组件通信的多种方式、适用场景

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

**父子组件通信**：
1. **props / 回调函数**：父传子用 props，子传父用回调函数
2. **ref**：通过 ref 获取子组件实例（类组件）或暴露方法（forwardRef）
3. **children**：通过 children 传递内容

**跨层级通信**：
4. **Context**：跨组件传递数据，避免 props 层层传递
5. **状态管理库**：Redux、MobX、Zustand 等

**兄弟组件通信**：
6. **状态提升**：将共享状态提升到共同父组件
7. **状态管理库**

**其他方式**：
8. **EventEmitter**：事件总线
9. **useImperativeHandle**：父组件调用子组件方法

**答案解析**:

**1. props + 回调函数**：
```jsx
// 父组件
function Parent() {
  const [count, setCount] = useState(0);
  return <Child count={count} onIncrement={() => setCount(c => c + 1)} />;
}

// 子组件
function Child({ count, onIncrement }) {
  return <button onClick={onIncrement}>{count}</button>;
}
```

**2. Context**：
```jsx
// 创建 Context
const ThemeContext = React.createContext('light');

// Provider 提供值
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Child />
    </ThemeContext.Provider>
  );
}

// Consumer 消费值（类组件）
// 或 useContext（函数组件）
function Child() {
  const theme = useContext(ThemeContext);
  return <div>{theme}</div>;
}
```

**3. useImperativeHandle + forwardRef**：
```jsx
const Child = forwardRef((props, ref) => {
  const inputRef = useRef();
  
  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current.focus()
  }));
  
  return <input ref={inputRef} />;
});

// 父组件使用
function Parent() {
  const childRef = useRef();
  return (
    <>
      <Child ref={childRef} />
      <button onClick={() => childRef.current.focus()}>聚焦</button>
    </>
  );
}
```

**4. Redux / Zustand 等状态管理库**：
适用于大型应用，全局状态共享。

**使用场景建议**：
- 父子：props + 回调
- 跨多层：Context（不频繁变化）或状态管理库
- 兄弟：状态提升或状态管理库
- 全局状态：状态管理库

**扩展问题**:
- Context 和 Redux 的区别？
- props  drilling 是什么？如何解决？
- useContext 的性能问题如何优化？
- 为什么不推荐用 EventEmitter？

---

## Q17: Redux 的工作原理和三大原则是什么？

**考察点**: Redux 核心概念、工作流程、三大原则

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

**Redux 三大原则**：
1. **单一数据源**：整个应用的 state 存储在唯一的 store 中
2. **State 是只读的**：唯一改变 state 的方式是触发 action
3. **使用纯函数来执行修改**：通过 reducer 来描述状态如何变化

**核心概念**：
- **Store**：存储 state 的仓库，唯一
- **Action**：描述发生了什么的对象，必须有 type 字段
- **Reducer**：纯函数，根据 action 返回新的 state
- **Dispatch**：触发 action 的方法
- **Middleware**：中间件，处理异步等副作用

**工作流程**：
`View → dispatch(Action) → Reducer → 更新 Store → View 更新`

**答案解析**:

**Redux 工作流程**：
```
        ┌──────────┐
        │  Action  │
        └────┬─────┘
             │ dispatch
             ▼
        ┌──────────┐
        │ Reducer  │
        └────┬─────┘
             │
             ▼
        ┌──────────┐
        │  Store   │
        └────┬─────┘
             │ subscribe
             ▼
        ┌──────────┐
        │   View   │
        └──────────┘
```

**基本使用**：
```javascript
import { createStore } from 'redux';

// Action
const increment = () => ({ type: 'INCREMENT' });
const decrement = () => ({ type: 'DECREMENT' });

// Reducer
function counterReducer(state = 0, action) {
  switch (action.type) {
    case 'INCREMENT': return state + 1;
    case 'DECREMENT': return state - 1;
    default: return state;
  }
}

// Store
const store = createStore(counterReducer);

// 使用
store.dispatch(increment());
console.log(store.getState()); // 1

store.subscribe(() => {
  console.log('state changed:', store.getState());
});
```

**中间件（Middleware）**：
中间件在 dispatch action 和到达 reducer 之间提供扩展点，用于处理异步、日志等。

```javascript
import { applyMiddleware, createStore } from 'redux';
import thunk from 'redux-thunk';

const store = createStore(reducer, applyMiddleware(thunk));

// 异步 action
const fetchData = () => (dispatch) => {
  dispatch({ type: 'FETCH_START' });
  return fetch('/api').then(res => {
    dispatch({ type: 'FETCH_SUCCESS', payload: res.data });
  });
};
```

**Redux Toolkit（RTK）**：
官方推荐的 Redux 工具集，简化 Redux 使用：
- 简化 store 配置
- 内置 immer 支持可变写法
- 内置 thunk 中间件
- createSlice 自动生成 action 和 reducer

**扩展问题**:
- Redux 为什么要用纯函数？
- Redux 和 Vuex 有什么区别？
- Redux 中间件的原理是什么？
- Redux Toolkit 解决了什么问题？
- 如何实现一个简单的 Redux？

---

## Q18: 什么是受控组件和非受控组件？

**考察点**: 受控组件和非受控组件的概念、区别、使用场景

**难度**: 简单

**频率**: ⭐⭐⭐⭐

**标准答案**:

**受控组件（Controlled Component）**：
表单数据由 React 的 state 控制，value 由 state 决定，onChange 来更新 state。

特点：
- 表单值受 React 状态控制
- 每次输入都会触发 onChange
- 可以实时获取和修改表单值
- 可以做实时校验、格式化等

**非受控组件（Uncontrolled Component）**：
表单数据由 DOM 本身管理，通过 ref 获取表单值。

特点：
- 表单值存在 DOM 中
- 通过 ref 获取值
- 代码更简单，适合简单表单
- 无法实时控制输入

**答案解析**:

**受控组件**：
```jsx
function Form() {
  const [value, setValue] = useState('');
  
  const handleChange = (e) => {
    setValue(e.target.value);
  };
  
  return (
    <input
      type="text"
      value={value}
      onChange={handleChange}
    />
  );
}
```

**非受控组件**：
```jsx
function Form() {
  const inputRef = useRef(null);
  
  const handleSubmit = () => {
    console.log(inputRef.current.value); // 通过 ref 获取值
  };
  
  return (
    <>
      <input type="text" ref={inputRef} defaultValue="default" />
      <button onClick={handleSubmit}>提交</button>
    </>
  );
}
```

**对比**：
| 特性 | 受控组件 | 非受控组件 |
|------|----------|------------|
| 数据源 | React state | DOM |
| 实时获取值 | 可以 | 不行 |
| 代码量 | 较多 | 较少 |
| 适用场景 | 需要实时控制、校验 | 简单表单、文件上传 |
| 文件上传 | 不支持（必须非受控） | 支持 |

**默认值**：
- 受控组件：value + onChange
- 非受控组件：defaultValue / defaultChecked

**使用场景建议**：
- 大多数情况推荐使用受控组件
- 文件上传（`<input type="file">`）必须用非受控
- 简单的一次性表单可以用非受控
- 需要实时验证、格式化、条件禁用等用受控

**扩展问题**:
- 为什么文件上传必须用非受控组件？
- 受控组件和非受控组件性能上有区别吗？
- 如何实现一个受控组件？
- React Hook Form 是受控还是非受控？

---

## Q19: Vue3 和 Vue2 的区别是什么？

**考察点**: Vue3 相比 Vue2 的新特性、性能提升、API 变化

**难度**: 中等

**频率**: ⭐⭐⭐⭐⭐

**标准答案**:

**1. 响应式系统**：
- Vue2：Object.defineProperty（有局限性）
- Vue3：Proxy（更完善的响应式）

**2. API 风格**：
- Vue2：选项式 API（Options API）
- Vue3：组合式 API（Composition API）+ 选项式 API

**3. 性能提升**：
- 体积更小（tree-shaking 支持）
- 编译优化（静态提升、PatchFlags、缓存事件处理函数）
- Diff 算法优化（最长递增子序列）
- 响应式性能提升

**4. 其他新特性**：
- Teleport（传送门）
- Suspense（异步组件）
- Fragment（多根节点）
- 更好的 TypeScript 支持
- 自定义渲染器
- 全局 API 改为具名导出

**答案解析**:

**组合式 API vs 选项式 API**：

```javascript
// Vue2 选项式
export default {
  data() { return { count: 0 }; },
  computed: { double() { return this.count * 2; } },
  methods: { increment() { this.count++; } }
};

// Vue3 组合式
<script setup>
import { ref, computed } from 'vue';

const count = ref(0);
const double = computed(() => count.value * 2);
const increment = () => count.value++;
</script>
```

组合式 API 的优势：
- 更好的逻辑复用（自定义 Hook）
- 更好的 TypeScript 类型推导
- 代码组织更灵活（按功能组织，不是按选项组织）
- tree-shaking 友好

**编译优化**：
Vue3 编译时做了大量优化：
- 静态节点提升（hoistStatic）
- 静态属性提升
- PatchFlags 标记动态节点
- 缓存事件处理函数

```html
<!-- 模板 -->
<div>
  <p>静态文本</p>
  <p>{{ msg }}</p>
</div>

<!-- 编译后（简化） -->
const _hoisted_1 = /*#__PURE__*/_createElementVNode("p", null, "静态文本")

function render(_ctx, _cache) {
  return (_openBlock(), _createElementBlock("div", null, [
    _hoisted_1,
    _createElementVNode("p", null, _toDisplayString(_ctx.msg), 1 /* TEXT */)
  ]))
}
```

**其他重要变化**：
- 移除 `$listeners`（合并到 `$attrs`）
- v-model 语法变化（支持多个 v-model）
- .sync 修饰符移除（用 v-model:xxx 代替）
- 全局 API 变化（Vue.use → app.use 等）
- 过滤器移除
- 生命周期命名变化（destroyed → unmounted 等）

**扩展问题**:
- Vue3 为什么用 Proxy 代替 Object.defineProperty？
- 组合式 API 和选项式 API 各有什么优缺点？
- Vue3 的编译优化有哪些？
- Vue3 的响应式有哪几种 API？（ref/reactive/toRefs/toRef）
- Vue3 中为什么推荐用 ref 而不是 reactive？

---

## Q20: 什么是高阶组件（HOC）？

**考察点**: 高阶组件的概念、实现、应用场景、与其他模式的对比

**难度**: 中等

**频率**: ⭐⭐⭐⭐

**标准答案**:

**高阶组件（Higher-Order Component，HOC）**：
高阶组件是一种设计模式，是接收一个组件并返回一个新组件的函数。

简单说：`HOC = (Component) => NewComponent`

**作用**：
- 代码复用，逻辑抽象
- 横切关注点（如权限控制、日志、数据获取）
- 增强组件功能

**常见应用场景**：
- 权限控制
- 数据获取
- 表单处理
- 日志埋点
- 错误边界

**答案解析**:

**简单 HOC 示例**：
```jsx
// 高阶组件：添加日志
function withLogger(WrappedComponent) {
  return class extends React.Component {
    componentDidMount() {
      console.log('Component mounted:', WrappedComponent.name);
    }
    
    componentWillUnmount() {
      console.log('Component unmounted:', WrappedComponent.name);
    }
    
    render() {
      return <WrappedComponent {...this.props} />;
    }
  };
}

// 使用
const EnhancedComponent = withLogger(MyComponent);
```

**属性代理和反向继承**：

1. **属性代理（Props Proxy）**：
   - 通过 props 传递数据和方法
   - 操作 props
   - 抽象 state

2. **反向继承（Inheritance Inversion）**：
   - 返回的组件继承原组件
   - 可以访问原组件的 state、生命周期
   - 渲染劫持

**HOC 的注意事项**：
- 不要在 render 方法中使用 HOC（每次都会创建新组件）
- 务必复制静态方法
- ref 不会被传递（需要 forwardRef）
- 约定以 with 开头命名

**与其他模式对比**：
- **HOC**：函数式，组件增强，适合横切关注点
- **Render Props**：更灵活的组件复用
- **Hooks**：函数组件中的逻辑复用（更推荐）

```jsx
// Hooks 方式（更简洁）
function useLogger(name) {
  useEffect(() => {
    console.log('mounted:', name);
    return () => console.log('unmounted:', name);
  }, [name]);
}

function MyComponent() {
  useLogger('MyComponent');
  return <div>...</div>;
}
```

**扩展问题**:
- HOC 和 Mixin 有什么区别？
- HOC 和 Render Props 的区别？
- HOC 和 Hooks 各有什么优缺点？
- HOC 为什么会导致 ref 丢失？
- 常见的 HOC 有哪些？（如 connect、withRouter）

---

## Reference

1. Vue 官方文档. https://cn.vuejs.org/
   访问时间：2026-07-28

2. React 官方文档. https://react.dev/
   访问时间：2026-07-28

3. 阮一峰 - React 技术栈. https://www.ruanyifeng.com/blog/react/
   访问时间：2026-07-28

4. 掘金前端社区 - Vue/React 技术文章. https://juejin.cn/frontend
   访问时间：2026-07-28

5. Vue3 源码解析 - GitHub. https://github.com/vuejs/core
   访问时间：2026-07-28

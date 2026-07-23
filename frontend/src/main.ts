/**
 * 文件名称：main.ts
 * 文件作用：Vue3 应用入口文件，负责创建应用实例、注册插件。
 * 当前阶段仅注册基础插件（Router、Pinia），挂载根组件。
 */

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import pinia from "./store";

const app = createApp(App);

// 注册路由
app.use(router);

// 注册状态管理
app.use(pinia);

app.mount("#app");

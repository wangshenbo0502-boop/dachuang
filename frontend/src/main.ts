/**
 * 文件名称：main.ts
 * 文件作用：Vue3 应用入口，注册 Router、Pinia 及全局 v-reveal 指令，挂载根组件。
 */

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import pinia from "./store";
import { reveal } from "./directives/reveal";
import "./styles/main.css";

const app = createApp(App);

app.use(router);
app.use(pinia);
app.directive("reveal", reveal);

app.mount("#app");
<!--
  文件名称：App.vue
  文件作用：Vue3 根组件，提供全局布局和路由出口。
  当前阶段仅搭建基础结构，后续集成布局组件。
-->
<template>
  <div id="app-root">
    <!-- TODO: 集成全局布局组件 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
// 根组件逻辑 —— 后续在此添加全局初始化和状态管理
</script>

<style>
/* 全局样式重置 —— 后续补充 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app-root {
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  min-height: 100vh;
}
</style>

<!--
  文件名称：DefaultLayout.vue
  文件作用：默认页面布局组件，包含顶部导航栏和底部信息。
  当前阶段仅搭建布局骨架，具体样式和组件后续实现。
-->
<template>
  <div class="default-layout">
    <!-- TODO: 集成 NavBar 公共组件 -->
    <header class="layout-header">
      <slot name="header">
        <!-- 顶部导航栏 -->
      </slot>
    </header>

    <main class="layout-main">
      <slot />
    </main>

    <!-- TODO: 集成 Footer 公共组件 -->
    <footer class="layout-footer">
      <slot name="footer">
        <!-- 底部信息 -->
      </slot>
    </footer>
  </div>
</template>

<script setup lang="ts">
// 默认布局逻辑 —— 后续添加导航状态等
</script>

<style scoped>
.default-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.layout-main {
  flex: 1;
}
</style>

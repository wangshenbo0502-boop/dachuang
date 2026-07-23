<!--
  文件名称：AuthLayout.vue
  文件作用：认证页面布局组件（登录/注册页面），无导航栏，居中卡片式布局。
  当前阶段仅搭建布局骨架，具体样式后续实现。
-->
<template>
  <div class="auth-layout">
    <div class="auth-card">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
// 认证页面布局逻辑
</script>

<style scoped>
.auth-layout {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.auth-card {
  /* TODO: 卡片样式 */
}
</style>

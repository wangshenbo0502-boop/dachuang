<!--
  文件名称：Loading.vue
  文件作用：全局加载状态组件，霓虹渐变旋转动画。
-->
<template>
  <div class="loading-wrapper" role="status">
    <div class="spinner"></div>
    <p v-if="text" class="text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text?: string;
}>();
</script>

<style scoped>
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 48px 20px;
}
.spinner {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 3px solid rgba(91, 124, 255, 0.2);
  border-top-color: var(--cyan);
  animation: spin 0.9s linear infinite;
  box-shadow: var(--glow-cyan);
}
.text {
  color: var(--text-1);
  font-size: 14px;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
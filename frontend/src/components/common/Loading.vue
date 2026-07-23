<!--
  文件名称：Loading.vue
  文件作用：全局加载状态组件，用于页面/数据加载时展示 loading 动画。
  当前阶段仅搭建组件骨架，具体动画效果后续实现。
-->
<template>
  <div class="loading-wrapper">
    <!-- TODO: Loading 动画效果 -->
    <div class="loading-spinner"></div>
    <p v-if="text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
// Loading 组件逻辑
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
  padding: 40px;
}
</style>

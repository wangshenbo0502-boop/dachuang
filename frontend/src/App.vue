<!--
  文件名称：App.vue
  文件作用：Vue3 根组件，用默认布局包裹所有路由页面。
-->
<template>
  <DefaultLayout>
    <router-view />
  </DefaultLayout>
</template>

<script setup lang="ts">
import DefaultLayout from "@/layouts/DefaultLayout.vue";
</script>
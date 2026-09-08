<!--
  文件名称：DefaultLayout.vue
  文件作用：默认页面布局 —— 星海背景 + 顶部导航 + 内容区 + 底部。
-->
<template>
  <div class="default-layout">
    <StarField />
    <NavBar />
    <main class="layout-main">
      <slot />
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import StarField from "@/components/common/StarField.vue";
import NavBar from "@/components/common/NavBar.vue";
import Footer from "@/components/common/Footer.vue";
</script>

<style scoped>
.default-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
}
.layout-main {
  flex: 1;
  position: relative;
  z-index: 1;
}
</style>
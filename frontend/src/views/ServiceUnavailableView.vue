<script setup lang="ts">
import { useRoute } from "vue-router";
import StateView from "@/components/common/StateView.vue";

// 网络或后端暂时不可用时显示；登录态保留，恢复后点击重试回到原页面
const route = useRoute();
function retry() {
  const redirect = typeof route.query.redirect === "string" && route.query.redirect.startsWith("/") && !route.query.redirect.startsWith("//")
    ? route.query.redirect
    : "/";
  window.location.assign(redirect);
}
</script>

<template>
  <main class="service-unavailable">
    <StateView error="暂时无法连接服务器，请检查网络后重试。你的登录状态已保留。" @retry="retry" />
  </main>
</template>

<style scoped>
.service-unavailable { min-height: 100vh; display: grid; place-items: center; padding: 24px; }
</style>

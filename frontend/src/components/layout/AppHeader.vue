<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAppStore } from "@/stores/app";
import { Bell, Menu, Search } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const app = useAppStore();
const title = computed(() => String(route.meta.title || ""));
</script>

<template>
  <header class="top-header">
    <div class="header-left">
      <el-button class="mobile-menu" :icon="Menu" circle aria-label="打开导航" @click="app.toggleMobile" />
      <div><span class="header-eyebrow">AI CAREER WORKSPACE</span><h1>{{ title }}</h1></div>
    </div>
    <div class="header-actions">
      <el-tooltip content="检索就业资源"><el-button :icon="Search" circle aria-label="检索就业资源" @click="router.push('/resources')" /></el-tooltip>
      <el-tooltip content="暂无新通知"><el-button :icon="Bell" circle aria-label="通知" /></el-tooltip>
    </div>
  </header>
</template>

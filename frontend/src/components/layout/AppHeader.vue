<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAppStore } from "@/stores/app";
import { Bell, Menu, Search } from "@element-plus/icons-vue";

const router = useRouter();
const app = useAppStore();
</script>

<template>
  <header class="top-header">
    <div class="header-left">
      <el-button class="mobile-menu" :icon="Menu" circle aria-label="打开导航" @click="app.toggleMobile" />
      <div><span class="header-eyebrow">CAREER WORKSPACE</span><h1>就业工作台</h1></div>
    </div>
    <div class="header-actions">
      <el-tooltip content="检索就业资源"><el-button :icon="Search" circle aria-label="检索就业资源" @click="router.push('/resources')" /></el-tooltip>
      <el-tooltip content="暂无新通知"><el-button :icon="Bell" circle aria-label="通知" /></el-tooltip>
    </div>
  </header>
</template>

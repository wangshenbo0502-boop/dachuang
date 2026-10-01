<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAppStore } from "@/stores/app";
import { useAuthStore } from "@/stores/auth";
import { Bell, Menu, Search } from "@element-plus/icons-vue";

const router = useRouter();
const app = useAppStore();
const auth = useAuthStore();
</script>

<template>
  <header class="top-header">
    <div class="header-left">
      <el-button class="mobile-menu" :icon="Menu" circle aria-label="打开导航" aria-controls="app-sidebar" :aria-expanded="app.mobileSidebarOpen" @click="app.toggleMobile" />
      <div><span class="header-eyebrow">{{ auth.isRecruiter ? 'RECRUITMENT WORKSPACE' : 'IT CAREER WORKSPACE' }}</span><h1>{{ auth.isRecruiter ? '招聘工作台' : 'IT 求职工作台' }}</h1></div>
    </div>
    <div class="header-actions">
      <el-tooltip v-if="!auth.isRecruiter" content="检索就业资源"><el-button :icon="Search" circle aria-label="检索就业资源" @click="router.push('/resources')" /></el-tooltip>
      <el-tooltip content="暂无新通知"><el-button :icon="Bell" circle aria-label="通知" /></el-tooltip>
    </div>
  </header>
</template>

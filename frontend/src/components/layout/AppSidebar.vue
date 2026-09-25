<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { useAppStore } from "@/stores/app";
import { useUserStore } from "@/stores/user";
import {
  ArrowLeft,
  ArrowRight,
  Briefcase,
  Collection,
  DataAnalysis,
  Document,
  House,
  ChatDotRound,
  Opportunity,
  SwitchButton,
  TrendCharts,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const app = useAppStore();
const user = useUserStore();
const items = [
  ["/dashboard", "首页", House],
  ["/analysis", "AI就业画像", DataAnalysis],
  ["/coach", "AI求职教练", ChatDotRound],
  ["/jobs", "岗位匹配", Briefcase],
  ["/resume", "简历优化", Document],
  ["/growth", "成长规划", TrendCharts],
  ["/resources", "就业资源", Collection],
] as const;

const go = (path: string) => {
  router.push(path);
  if (innerWidth < 900) app.toggleMobile();
};
const logout = () => {
  user.logout();
  router.replace("/login");
};
const accountCommand = (path: string) => {
  if (path === "logout") {
    logout();
    return;
  }
  router.push(path);
  if (innerWidth < 900) app.toggleMobile();
};
</script>

<template>
  <aside class="sidebar" :class="{ open: app.mobileSidebarOpen }">
    <div class="brand">
      <div class="brand-mark"><el-icon><Opportunity /></el-icon></div>
      <div class="brand-text"><b>Career Copilot</b><span>AI就业成长工作台</span></div>
    </div>
    <nav class="nav-list" aria-label="主导航">
      <button
        v-for="[path, label, icon] in items"
        :key="path"
        :title="app.sidebarCollapsed ? label : undefined"
        :class="{ active: route.path === path || (path === '/jobs' && route.path.startsWith('/jobs/')) }"
        @click="go(path)"
      >
        <el-icon><component :is="icon" /></el-icon><span>{{ label }}</span>
      </button>
    </nav>
    <div class="sidebar-foot">
      <button class="collapse-button" :title="app.sidebarCollapsed ? '展开导航' : '收起导航'" @click="app.toggleSidebar">
        <el-icon><component :is="app.sidebarCollapsed ? ArrowRight : ArrowLeft" /></el-icon><span>收起导航</span>
      </button>
      <el-dropdown class="user-menu" trigger="click" placement="top-start" @command="accountCommand">
        <div class="user-mini" tabindex="0" role="button" aria-label="打开个人菜单">
          <el-avatar :size="38">{{ user.user?.name?.slice(0, 1) || "学" }}</el-avatar>
          <div><b>{{ user.user?.name || "学生" }}</b><span>{{ user.user?.major || "尚未填写专业" }}</span></div>
          <el-icon class="user-menu-arrow"><ArrowRight /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="/profile">我的就业档案</el-dropdown-item>
            <el-dropdown-item command="/settings">系统设置</el-dropdown-item>
            <el-dropdown-item command="/history">分析记录</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </aside>
</template>

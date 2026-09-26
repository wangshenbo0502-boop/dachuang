<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessageBox } from "element-plus";
import { useAppStore } from "@/stores/app";
import { useUserStore } from "@/stores/user";
import {
  createAssistantSession,
  readAssistantSessionStore,
  writeAssistantSessionStore,
  type AssistantSession,
} from "@/utils/assistantSessions";
import {
  ArrowLeft,
  ArrowRight,
  Briefcase,
  Collection,
  DataAnalysis,
  Document,
  House,
  ChatDotRound,
  Delete,
  EditPen,
  Opportunity,
  Plus,
  TrendCharts,
  User,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const app = useAppStore();
const user = useUserStore();
const recentSessions = ref<AssistantSession[]>([]);
const workflowItems = [
  ["/dashboard", "首页", House],
  ["/profile", "我的个人档案", User],
  ["/analysis", "AI就业画像", DataAnalysis],
  ["/jobs", "岗位匹配", Briefcase],
  ["/resume", "我的简历", Document],
  ["/growth", "成长规划", TrendCharts],
] as const;
const toolItems = [
  ["/resources", "就业资源", Collection],
] as const;
const activeSessionId = computed(() => typeof route.query.session === "string" ? route.query.session : "");

function loadRecentSessions() {
  if (!user.userId) {
    recentSessions.value = [];
    return;
  }
  const store = readAssistantSessionStore(user.userId);
  recentSessions.value = [...(store?.sessions || [])]
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
}

function newConversation() {
  if (!user.userId) return;
  const session = createAssistantSession("consult");
  const existing = readAssistantSessionStore(user.userId);
  writeAssistantSessionStore(user.userId, {
    version: 3,
    activeId: session.id,
    sessions: [session, ...(existing?.sessions || [])],
  });
  router.push({ path: "/coach", query: { session: session.id } });
  if (innerWidth < 900) app.toggleMobile();
}

function openSession(session: AssistantSession) {
  router.push({ path: "/coach", query: { session: session.id, ...(session.mode === "profile" ? { mode: "profile" } : {}) } });
  if (innerWidth < 900) app.toggleMobile();
}

async function removeSession(session: AssistantSession) {
  if (!user.userId) return;
  try {
    await ElMessageBox.confirm(`删除“${session.title}”的聊天记录？`, "删除对话", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
  } catch {
    return;
  }
  const store = readAssistantSessionStore(user.userId);
  if (!store) return;
  const remaining = store.sessions.filter(item => item.id !== session.id);
  const next = remaining[0] || createAssistantSession("consult");
  const sessions = remaining.length ? remaining : [next];
  writeAssistantSessionStore(user.userId, { version: 3, activeId: next.id, sessions });
  if (activeSessionId.value === session.id) {
    router.replace({ path: "/coach", query: { session: next.id, ...(next.mode === "profile" ? { mode: "profile" } : {}) } });
  }
}

function formatSessionTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const today = new Date();
  if (date.toDateString() === today.toDateString()) return date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
  return date.toLocaleDateString("zh-CN", { month: "numeric", day: "numeric" });
}

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

watch(() => user.userId, loadRecentSessions);
onMounted(() => {
  loadRecentSessions();
  window.addEventListener("assistant-sessions-updated", loadRecentSessions);
  window.addEventListener("storage", loadRecentSessions);
});
onBeforeUnmount(() => {
  window.removeEventListener("assistant-sessions-updated", loadRecentSessions);
  window.removeEventListener("storage", loadRecentSessions);
});
</script>

<template>
  <aside class="sidebar" :class="{ open: app.mobileSidebarOpen }">
    <div class="brand">
      <div class="brand-mark"><el-icon><Opportunity /></el-icon></div>
      <div class="brand-text"><b>AI求职助手</b><span>AI就业成长工作台</span></div>
    </div>
    <nav class="nav-list nav-list-main" aria-label="主要功能">
      <div class="nav-section-label">工作台</div>
      <button
        v-for="[path, label, icon] in workflowItems"
        :key="path"
        :title="app.sidebarCollapsed ? label : undefined"
        :class="{ active: route.path === path || (path === '/profile' && route.path.startsWith('/profile')) || (path === '/jobs' && route.path.startsWith('/jobs/')) }"
        @click="go(path)"
      >
        <el-icon><component :is="icon" /></el-icon><span>{{ label }}</span>
      </button>
    </nav>
    <section class="assistant-nav" aria-label="AI求职助手对话">
      <div class="assistant-nav-heading">
        <span>对话</span>
        <el-tooltip content="开启新对话" placement="right">
          <button class="assistant-new-icon" aria-label="开启新对话" @click="newConversation"><el-icon><Plus /></el-icon></button>
        </el-tooltip>
      </div>
      <button class="assistant-new-button" :class="{ active: route.path === '/coach' && !activeSessionId }" @click="newConversation">
        <el-icon><EditPen /></el-icon><span>开启新对话</span>
      </button>
      <div v-if="recentSessions.length" class="assistant-history">
        <div class="assistant-history-label">历史对话</div>
        <div class="assistant-history-list">
          <div
            v-for="session in recentSessions"
            :key="session.id"
            class="assistant-history-item"
            :class="{ active: activeSessionId === session.id }"
            role="button"
            tabindex="0"
            :title="session.title"
            @click="openSession(session)"
            @keydown.enter="openSession(session)"
          >
            <el-icon><ChatDotRound /></el-icon>
            <div><b>{{ session.title }}</b><span>{{ formatSessionTime(session.updatedAt) }}</span></div>
            <button class="assistant-history-delete" title="删除对话" aria-label="删除对话" @click.stop="removeSession(session)"><el-icon><Delete /></el-icon></button>
          </div>
        </div>
      </div>
    </section>
    <nav class="nav-list nav-list-tools" aria-label="更多功能">
      <div class="nav-section-label">更多</div>
      <button
        v-for="[path, label, icon] in toolItems"
        :key="path"
        :title="app.sidebarCollapsed ? label : undefined"
        :class="{ active: route.path === path }"
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

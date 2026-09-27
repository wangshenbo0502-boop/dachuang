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
  ArrowDown,
  Briefcase,
  Promotion,
  Collection,
  DataAnalysis,
  Document,
  House,
  ChatDotRound,
  Delete,
  EditPen,
  Opportunity,
  Close,
  Search,
  TrendCharts,
  User,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const app = useAppStore();
const user = useUserStore();
const recentSessions = ref<AssistantSession[]>([]);
const sessionSearch = ref("");
const isMobile = ref(window.matchMedia("(max-width: 900px)").matches);
const isCompact = computed(() => app.sidebarCollapsed && !isMobile.value);
const workflowItems = [
  ["/dashboard", "首页", House],
  ["/profile", "个人档案", User],
  ["/analysis", "就业画像", DataAnalysis],
  ["/jobs", "岗位匹配", Briefcase],
  ["/applications", "投递助手", Promotion],
  ["/resume", "我的简历", Document],
  ["/growth", "成长规划", TrendCharts],
  ["/resources", "就业资源", Collection],
] as const;
const activeSessionId = computed(() => typeof route.query.session === "string" ? route.query.session : "");
const filteredSessions = computed(() => {
  const query = sessionSearch.value.trim().toLocaleLowerCase();
  return recentSessions.value.filter(session => session.title.toLocaleLowerCase().includes(query));
});

function closeMobile() {
  app.mobileSidebarOpen = false;
}

function handleViewport(event: MediaQueryListEvent) {
  isMobile.value = event.matches;
  if (!event.matches) closeMobile();
}

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
  sessionSearch.value = "";
  closeMobile();
}

function openSession(session: AssistantSession) {
  router.push({ path: "/coach", query: { session: session.id, ...(session.mode === "profile" ? { mode: "profile" } : {}) } });
  closeMobile();
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
  const next = remaining.find(item => item.id === store.activeId) || remaining[0] || createAssistantSession("consult");
  const sessions = remaining.length ? remaining : [next];
  writeAssistantSessionStore(user.userId, { version: 3, activeId: next.id, sessions });
  if (route.path === "/coach" && activeSessionId.value === session.id) {
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
  closeMobile();
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
  go(path);
};

const viewport = window.matchMedia("(max-width: 900px)");
watch(() => user.userId, loadRecentSessions);
watch(() => route.fullPath, closeMobile);
onMounted(() => {
  loadRecentSessions();
  viewport.addEventListener("change", handleViewport);
  window.addEventListener("assistant-sessions-updated", loadRecentSessions);
  window.addEventListener("storage", loadRecentSessions);
});
onBeforeUnmount(() => {
  viewport.removeEventListener("change", handleViewport);
  window.removeEventListener("assistant-sessions-updated", loadRecentSessions);
  window.removeEventListener("storage", loadRecentSessions);
});
</script>

<template>
  <aside id="app-sidebar" class="sidebar" :class="{ open: app.mobileSidebarOpen, 'is-compact': isCompact }" :inert="isMobile && !app.mobileSidebarOpen" aria-label="工作台导航" @keydown.esc="closeMobile">
    <div class="brand">
      <div class="brand-mark"><el-icon><Opportunity /></el-icon></div>
      <div class="brand-text"><b>AI 求职助手</b><span>你的求职成长工作台</span></div>
      <el-tooltip :content="isCompact ? '展开侧栏' : '收起侧栏'" placement="right" :disabled="isMobile">
        <button class="sidebar-toggle" :aria-label="isMobile ? '关闭导航' : isCompact ? '展开侧栏' : '收起侧栏'" :aria-expanded="!isCompact" aria-controls="sidebar-content" @click="isMobile ? closeMobile() : app.toggleSidebar()">
          <el-icon><component :is="isMobile ? Close : isCompact ? ArrowRight : ArrowLeft" /></el-icon>
        </button>
      </el-tooltip>
    </div>
    <div class="sidebar-create">
      <el-tooltip content="新建对话" placement="right" :disabled="!isCompact">
        <button class="assistant-new-button" aria-label="新建对话" @click="newConversation">
          <el-icon><EditPen /></el-icon><span>新建对话</span>
        </button>
      </el-tooltip>
    </div>
    <div id="sidebar-content" class="sidebar-content">
      <nav class="nav-list" aria-label="求职工作台">
        <div class="nav-section-label">求职工作台</div>
        <el-tooltip v-for="[path, label, icon] in workflowItems" :key="path" :content="label" placement="right" :disabled="!isCompact">
          <router-link :to="path" :aria-label="label" :class="{ active: route.path === path || route.path.startsWith(`${path}/`) }" :aria-current="route.path === path || route.path.startsWith(`${path}/`) ? 'page' : undefined" @click="closeMobile">
            <el-icon><component :is="icon" /></el-icon><span>{{ label }}</span>
          </router-link>
        </el-tooltip>
      </nav>
      <section class="assistant-history" aria-label="历史对话">
        <div class="assistant-history-heading"><span>历史对话</span><span class="assistant-history-count">{{ recentSessions.length }}</span></div>
        <label v-if="recentSessions.length" class="assistant-history-search">
          <el-icon><Search /></el-icon>
          <input v-model="sessionSearch" type="search" placeholder="搜索对话" aria-label="搜索历史对话" />
        </label>
        <div class="assistant-history-list" tabindex="0" aria-label="历史对话列表">
          <div v-for="session in filteredSessions" :key="session.id" class="assistant-history-item" :class="{ active: route.path === '/coach' && activeSessionId === session.id }">
            <button class="assistant-history-open" :title="session.title" :aria-current="route.path === '/coach' && activeSessionId === session.id ? 'page' : undefined" @click="openSession(session)">
              <el-icon><ChatDotRound /></el-icon>
              <span class="assistant-history-title">{{ session.title }}</span>
              <time :datetime="session.updatedAt">{{ formatSessionTime(session.updatedAt) }}</time>
            </button>
            <button class="assistant-history-delete" :aria-label="`删除对话：${session.title}`" title="删除对话" @click="removeSession(session)"><el-icon><Delete /></el-icon></button>
          </div>
          <p v-if="!recentSessions.length" class="assistant-history-empty">还没有对话记录<span>从上方新建一次对话吧</span></p>
          <p v-else-if="!filteredSessions.length" class="assistant-history-empty">没有找到相关对话<span>换个关键词试试</span></p>
        </div>
      </section>
      <el-tooltip content="继续最近的对话" placement="right" :disabled="!isCompact">
        <button class="sidebar-chat-shortcut" aria-label="继续最近的对话" :class="{ active: route.path === '/coach' }" @click="recentSessions.length ? openSession(recentSessions.find(item => item.id === activeSessionId) || recentSessions[0]) : newConversation()"><el-icon><ChatDotRound /></el-icon></button>
      </el-tooltip>
    </div>
    <div class="sidebar-foot">
      <el-dropdown class="user-menu" trigger="click" placement="top-start" @command="accountCommand">
        <button class="user-mini" aria-label="打开个人菜单" :title="isCompact ? user.user?.name || '个人菜单' : undefined">
          <el-avatar :size="34">{{ user.user?.name?.slice(0, 1) || "学" }}</el-avatar>
          <div><b>{{ user.user?.name || "学生" }}</b><span>{{ user.user?.major || "尚未填写专业" }}</span></div>
          <el-icon class="user-menu-arrow"><ArrowDown /></el-icon>
        </button>
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

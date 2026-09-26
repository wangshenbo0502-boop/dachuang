<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { onBeforeRouteLeave, useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Briefcase,
  CopyDocument,
  DataAnalysis,
  Delete,
  Document,
  EditPen,
  MagicStick,
  Plus,
  Promotion,
  RefreshRight,
  TrendCharts,
  UserFilled,
  VideoPause,
} from "@element-plus/icons-vue";
import { api } from "@/api";
import { useProfileStore } from "@/stores/profile";
import { useUserStore } from "@/stores/user";
import {
  createAssistantId,
  createAssistantSession,
  readAssistantSessionStore,
  writeAssistantSessionStore,
  type AssistantMessage,
  type AssistantMode,
  type AssistantSession,
  type AssistantSuggestedAction,
} from "@/utils/assistantSessions";
import { consumeSse } from "@/utils/sse";
import type { ChatMessage, ChatTurnResponse, StudentProfile } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";
import ProfileDraftPanel from "@/components/assistant/ProfileDraftPanel.vue";

const route = useRoute();
const router = useRouter();
const user = useUserStore();
const profiles = useProfileStore();
const sessions = ref<AssistantSession[]>([]);
const activeId = ref("");
const transientSession = ref(createAssistantSession(route.query.mode === "profile" ? "profile" : "consult"));
const input = ref("");
const reviewInput = ref("");
const loading = ref(false);
const syncing = ref(false);
const draftDrawer = ref(false);
const chatBody = ref<HTMLElement>();
let activeController: AbortController | null = null;
let requestVersion = 0;

const modeOptions = [
  { label: "求职咨询", value: "consult" },
  { label: "完善档案", value: "profile" },
];
const actionLabels = {
  profile: "继续完善档案", resume: "去优化简历", analysis: "去做 AI 画像", growth: "去看成长规划", jobs: "去匹配岗位",
} as const;
const actionPaths = {
  profile: "/coach?mode=profile", resume: "/resume", analysis: "/analysis", growth: "/growth", jobs: "/jobs",
} as const;
const activeSession = computed(() => sessions.value.find(item => item.id === activeId.value) || transientSession.value);
const mode = computed<AssistantMode>({
  get: () => activeSession.value.mode,
  set: value => {
    activeSession.value.mode = value;
    input.value = "";
    if (value === "profile") ensureProfileGreeting();
    touchSession();
    persist();
    syncRoute();
    scrollBottom();
  },
});
const consultMessages = computed<AssistantMessage[]>({
  get: () => activeSession.value.consultMessages,
  set: value => { activeSession.value.consultMessages = value; },
});
const profileMessages = computed<AssistantMessage[]>({
  get: () => activeSession.value.profileMessages,
  set: value => { activeSession.value.profileMessages = value; },
});
const draft = computed<Record<string, any>>({
  get: () => activeSession.value.draft,
  set: value => { activeSession.value.draft = value; },
});
const target = computed<string>({
  get: () => activeSession.value.target,
  set: value => { activeSession.value.target = value; },
});
const suggestedAction = computed<AssistantSuggestedAction | null>({
  get: () => activeSession.value.suggestedAction,
  set: value => { activeSession.value.suggestedAction = value; },
});
const messages = computed(() => mode.value === "consult" ? consultMessages.value : profileMessages.value);
const hasDraft = computed(() => Object.values(draft.value).some(value =>
  Array.isArray(value) ? value.length > 0 : typeof value === "string" && value.trim(),
));

function createMessage(role: ChatMessage["role"], content: string, failed = false): AssistantMessage {
  return { role, content, failed, id: createAssistantId(), createdAt: new Date().toISOString() };
}

function normalizeMessages(value: unknown): AssistantMessage[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap(item => {
    if (!item || typeof item !== "object") return [];
    const raw = item as Partial<AssistantMessage>;
    if ((raw.role !== "user" && raw.role !== "assistant") || typeof raw.content !== "string") return [];
    const normalized = createMessage(raw.role, raw.content, Boolean(raw.failed));
    if (typeof raw.id === "string" && raw.id) normalized.id = raw.id;
    if (typeof raw.createdAt === "string" && raw.createdAt) normalized.createdAt = raw.createdAt;
    return [normalized];
  });
}

function normalizeSession(value: Partial<AssistantSession>): AssistantSession {
  const fallback = createAssistantSession(value.mode === "profile" ? "profile" : "consult");
  return {
    ...fallback,
    id: typeof value.id === "string" && value.id ? value.id : fallback.id,
    title: typeof value.title === "string" && value.title.trim() ? value.title.trim().slice(0, 28) : "新对话",
    mode: value.mode === "profile" ? "profile" : "consult",
    target: typeof value.target === "string" ? value.target : "",
    consultMessages: normalizeMessages(value.consultMessages),
    profileMessages: normalizeMessages(value.profileMessages),
    draft: value.draft && typeof value.draft === "object" ? value.draft : {},
    suggestedAction: value.suggestedAction || null,
    createdAt: typeof value.createdAt === "string" ? value.createdAt : fallback.createdAt,
    updatedAt: typeof value.updatedAt === "string" ? value.updatedAt : fallback.updatedAt,
  };
}

function ensureProfileGreeting() {
  if (!profileMessages.value.length) {
    profileMessages.value.push(createMessage(
      "assistant",
      "我们可以慢慢把就业档案聊完整。你想回答多少都可以，也可以随时说“跳过”或直接确认当前草稿。先从你最想找的岗位或方向开始：你希望毕业后做什么？",
    ));
  }
}

function touchSession() {
  activeSession.value.updatedAt = new Date().toISOString();
}

function updateSessionTitle(content: string) {
  if (activeSession.value.title !== "新对话") return;
  const title = content.replace(/\s+/g, " ").trim();
  if (title) activeSession.value.title = title.length > 22 ? `${title.slice(0, 22)}…` : title;
}

function persist() {
  if (!user.userId || !sessions.value.length) return;
  writeAssistantSessionStore(user.userId, { version: 3, activeId: activeId.value, sessions: sessions.value });
}

function syncRoute() {
  const query: Record<string, string> = { session: activeId.value };
  if (mode.value === "profile") query.mode = "profile";
  if (route.query.session === query.session && route.query.mode === query.mode) return;
  router.replace({ path: "/coach", query });
}

function restore() {
  if (!user.userId) return;
  const saved = readAssistantSessionStore(user.userId);
  if (saved?.sessions.length) {
    sessions.value = saved.sessions.map(normalizeSession);
    const requestedId = typeof route.query.session === "string" ? route.query.session : "";
    activeId.value = sessions.value.some(item => item.id === requestedId)
      ? requestedId
      : sessions.value.some(item => item.id === saved.activeId) ? saved.activeId : sessions.value[0].id;
  } else {
    const migrated = createAssistantSession(route.query.mode === "profile" ? "profile" : "consult");
    try {
      const old = JSON.parse(localStorage.getItem(`ai-career-assistant-v2-${user.userId}`) || "null");
      const legacy = JSON.parse(localStorage.getItem(`career-copilot-chat-${user.userId}`) || "null");
      if (old?.version === 2) {
        migrated.mode = old.mode === "profile" ? "profile" : "consult";
        migrated.target = old.consult?.target || "";
        migrated.consultMessages = normalizeMessages(old.consult?.messages);
        migrated.profileMessages = normalizeMessages(old.profile?.messages);
        migrated.draft = old.profile?.draft && typeof old.profile.draft === "object" ? old.profile.draft : {};
        migrated.suggestedAction = old.consult?.suggestedAction || null;
      } else if (legacy) {
        migrated.target = legacy.target || "";
        migrated.consultMessages = normalizeMessages(legacy.messages);
      }
    } catch {
      // Invalid legacy data is ignored; a fresh session is still available.
    }
    const firstUserMessage = [...migrated.consultMessages, ...migrated.profileMessages].find(item => item.role === "user");
    if (firstUserMessage) {
      const title = firstUserMessage.content.replace(/\s+/g, " ").trim();
      migrated.title = title.length > 22 ? `${title.slice(0, 22)}…` : title || "新对话";
    }
    sessions.value = [migrated];
    activeId.value = migrated.id;
  }
  if (route.query.mode === "profile") activeSession.value.mode = "profile";
  ensureProfileGreeting();
  persist();
  syncRoute();
}

function startNewConversation() {
  stop();
  const session = createAssistantSession("consult");
  sessions.value.unshift(session);
  activeId.value = session.id;
  input.value = "";
  reviewInput.value = "";
  persist();
  syncRoute();
  scrollBottom();
}

function activateSession(id: string) {
  if (!id || id === activeId.value) return;
  const local = sessions.value.find(item => item.id === id);
  if (!local && user.userId) {
    const saved = readAssistantSessionStore(user.userId);
    if (saved) sessions.value = saved.sessions.map(normalizeSession);
  }
  const next = sessions.value.find(item => item.id === id);
  if (!next) return;
  stop();
  activeId.value = next.id;
  input.value = "";
  reviewInput.value = "";
  if (route.query.mode === "profile") next.mode = "profile";
  ensureProfileGreeting();
  persist();
  syncRoute();
  scrollBottom();
}

function mergeDraft(next: Record<string, unknown>, targetDraft = draft.value) {
  for (const [key, value] of Object.entries(next || {})) {
    if (Array.isArray(value) && value.length) {
      const existing = Array.isArray(targetDraft[key]) ? targetDraft[key] : [];
      const identity = (item: any) => String(item?.name || `${item?.company || ""}-${item?.position || ""}`).trim().toLocaleLowerCase();
      const merged = [...existing];
      for (const item of value) {
        const itemIdentity = identity(item);
        const index = merged.findIndex((old: any) => itemIdentity && identity(old) === itemIdentity);
        if (index >= 0) merged[index] = { ...merged[index], ...item };
        else merged.push(item);
      }
      targetDraft[key] = merged;
    } else if (typeof value === "string" && value.trim()) {
      targetDraft[key] = value.trim();
    }
  }
}

function apiMessages(items: AssistantMessage[]): ChatMessage[] {
  return items.filter(item => item.content.trim()).slice(-40).map(({ role, content }) => ({ role, content }));
}

async function scrollBottom() {
  await nextTick();
  if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight;
}

function getUserId() {
  const id = Number(user.userId);
  if (Number.isInteger(id) && id > 0) return id;
  ElMessage.warning("登录状态已失效，请重新登录");
  router.replace({ path: "/login", query: { redirect: route.fullPath } });
  return null;
}

async function sendConsult(content: string, existingUser?: AssistantMessage): Promise<boolean> {
  const userId = getUserId();
  if (!userId) return false;
  const session = activeSession.value;
  const conversation = session.consultMessages;
  const userMessage = existingUser || createMessage("user", content);
  if (!existingUser) conversation.push(userMessage);
  userMessage.failed = false;
  const responseMessage = createMessage("assistant", "");
  conversation.push(responseMessage);
  updateSessionTitle(content);
  touchSession();
  persist();
  loading.value = true;
  const version = ++requestVersion;
  const controller = new AbortController();
  activeController = controller;
  let streamError = "";
  await scrollBottom();
  try {
    await consumeSse<{ suggested_action?: AssistantSuggestedAction | null }>(
      "/chat/conversation-stream",
      { user_id: userId, target_job: session.target.trim(), messages: apiMessages(conversation) },
      {
        chunk(chunk) {
          if (version !== requestVersion) return;
          responseMessage.content += chunk;
          scrollBottom();
        },
        complete(result) {
          if (version === requestVersion) session.suggestedAction = result?.suggested_action || null;
        },
        error(message) {
          if (version === requestVersion) streamError = message;
        },
      },
      controller.signal,
    );
    if (streamError) throw new Error(streamError);
    if (!responseMessage.content.trim()) throw new Error("AI 没有返回有效内容，请重试");
    session.updatedAt = new Date().toISOString();
    persist();
    return true;
  } catch (error) {
    const canceled = (error as Error).name === "AbortError";
    if (!responseMessage.content.trim() || streamError) {
      const responseIndex = conversation.findIndex(item => item.id === responseMessage.id);
      if (responseIndex >= 0) conversation.splice(responseIndex, 1);
    }
    if (!canceled) {
      userMessage.failed = true;
      ElMessage.error(error instanceof Error ? error.message : "AI 暂时无法回复，请稍后重试");
    }
    persist();
    return false;
  } finally {
    if (version === requestVersion) loading.value = false;
    if (activeController === controller) activeController = null;
    await scrollBottom();
  }
}

async function sendProfile(content: string): Promise<boolean> {
  const userId = getUserId();
  if (!userId) return false;
  const session = activeSession.value;
  const conversation = session.profileMessages;
  const userMessage = createMessage("user", content);
  conversation.push(userMessage);
  updateSessionTitle(content);
  touchSession();
  persist();
  loading.value = true;
  const version = ++requestVersion;
  const controller = new AbortController();
  activeController = controller;
  await scrollBottom();
  try {
    const response: ChatTurnResponse = await api.chatProfileTurn(
      { user_id: userId, messages: apiMessages(conversation) },
      controller.signal,
    );
    if (version !== requestVersion) return false;
    conversation.push(createMessage("assistant", response.reply));
    mergeDraft(response.extracted, session.draft);
    session.updatedAt = new Date().toISOString();
    persist();
    return true;
  } catch (error) {
    const canceled = (error as Error).name === "CanceledError" || (error as Error).name === "AbortError";
    if (!canceled) userMessage.failed = true;
    if (!canceled) {
      ElMessage.error(error instanceof Error ? error.message : "AI 暂时无法继续整理档案");
    }
    persist();
    return false;
  } finally {
    if (version === requestVersion) loading.value = false;
    if (activeController === controller) activeController = null;
    await scrollBottom();
  }
}

async function send(content?: string) {
  const text = (content ?? input.value).trim();
  if (!text || loading.value) return;
  input.value = "";
  if (mode.value === "consult") await sendConsult(text);
  else await sendProfile(text);
}

function stop() {
  if (!activeController) return;
  if (mode.value === "consult") {
    const last = consultMessages.value.at(-1);
    if (last?.role === "assistant" && last.content.trim()) last.content += "\n\n（已停止生成）";
  }
  activeController.abort();
  requestVersion += 1;
  loading.value = false;
  activeController = null;
  touchSession();
  persist();
}

async function retry(index: number) {
  const item = messages.value[index];
  if (!item?.failed || loading.value) return;
  messages.value.splice(index, 1);
  persist();
  if (mode.value === "consult") await sendConsult(item.content);
  else await sendProfile(item.content);
}

async function regenerate(index: number) {
  if (mode.value !== "consult" || loading.value || index !== consultMessages.value.length - 1) return;
  const answer = consultMessages.value[index];
  if (answer?.role !== "assistant") return;
  let userIndex = index - 1;
  while (userIndex >= 0 && consultMessages.value[userIndex]?.role !== "user") userIndex -= 1;
  const userMessage = consultMessages.value[userIndex];
  if (!userMessage) return;
  consultMessages.value.splice(index, 1);
  suggestedAction.value = null;
  persist();
  await sendConsult(userMessage.content, userMessage);
}

async function copyReply(content: string) {
  try {
    await navigator.clipboard.writeText(content);
    ElMessage.success("回答已复制");
  } catch {
    ElMessage.error("复制失败，请手动选择文字复制");
  }
}

async function requestChange() {
  const content = reviewInput.value.trim();
  if (!content || loading.value) return;
  const success = await sendProfile(content);
  if (success) reviewInput.value = "";
}

async function confirmSync() {
  const userId = getUserId();
  if (!userId || !hasDraft.value) return;
  syncing.value = true;
  try {
    const result = await api.syncChatProfile({ user_id: userId, profile: draft.value });
    profiles.profile = result.profile as StudentProfile;
    user.user = result.profile as StudentProfile;
    draft.value = {};
    profileMessages.value.push(createMessage("assistant", "已按你的确认更新就业档案。我们还可以继续聊，之后识别出的新内容仍会先放进草稿。"));
    touchSession();
    persist();
    draftDrawer.value = false;
    if (result.skipped.length) {
      ElMessage.warning(`档案已更新；${result.skipped.join("；")}，这些内容需要继续补充后才能保存。`);
    } else {
      ElMessage.success("档案已更新");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "档案同步失败");
  } finally {
    syncing.value = false;
  }
}

async function clearCurrent() {
  try {
    await ElMessageBox.confirm(
      mode.value === "profile" ? "将清空当前档案访谈和未保存草稿，是否继续？" : "将清空当前求职咨询记录，是否继续？",
      "确认清空",
      { type: "warning", confirmButtonText: "清空", cancelButtonText: "取消" },
    );
  } catch { return; }
  stop();
  if (mode.value === "consult") {
    consultMessages.value = [];
    suggestedAction.value = null;
  } else {
    profileMessages.value = [];
    draft.value = {};
    reviewInput.value = "";
    ensureProfileGreeting();
  }
  input.value = "";
  activeSession.value.title = "新对话";
  touchSession();
  persist();
  await scrollBottom();
}

function formatTime(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
}

function beforeUnload(event: BeforeUnloadEvent) {
  if (!hasDraft.value) return;
  event.preventDefault();
  event.returnValue = "";
}

watch(() => route.query.session, value => {
  if (typeof value === "string") activateSession(value);
});
watch(() => route.query.mode, value => {
  if (value === "profile" && mode.value !== "profile") mode.value = "profile";
});

onBeforeRouteLeave(() => {
  if (!hasDraft.value) return true;
  return window.confirm("档案草稿还没有写入正式档案。离开后草稿仍会保存在当前浏览器，确定离开吗？");
});

onMounted(async () => {
  restore();
  try {
    await profiles.load(user.userId!, true);
  } catch (error) {
    ElMessage.warning(error instanceof Error ? error.message : "当前档案加载失败，AI 仍可继续对话");
  }
  window.addEventListener("beforeunload", beforeUnload);
  await scrollBottom();
});

onBeforeUnmount(() => {
  activeController?.abort();
  window.removeEventListener("beforeunload", beforeUnload);
});
</script>

<template>
  <div class="assistant-page">
    <PageHeader title="AI求职助手" description="求职问题和档案整理，都可以在这里完成。">
      <div class="assistant-page-actions">
        <el-button class="assistant-header-new" :icon="Plus" @click="startNewConversation">新对话</el-button>
        <el-segmented v-model="mode" :options="modeOptions" :disabled="loading" />
        <el-button :icon="Delete" text @click="clearCurrent">清空当前对话</el-button>
      </div>
    </PageHeader>

    <div class="assistant-workspace" :class="{ 'profile-mode': mode === 'profile' }">
      <section class="assistant-chat-panel">
        <header class="assistant-chat-header">
          <div class="conversation-title">
            <div class="conversation-avatar"><el-icon><MagicStick /></el-icon></div>
            <div>
              <h2>{{ mode === "consult" ? "聊聊你的求职问题" : "一起完善就业档案" }}</h2>
              <p>{{ mode === "consult" ? "简历、面试、岗位选择和成长方向，都可以从这里开始" : "对话采集信息，草稿确认后再写入正式档案" }}</p>
            </div>
          </div>
          <el-input v-if="mode === 'consult'" v-model="target" class="conversation-target" placeholder="可选：目标岗位" @change="persist" />
          <el-button v-else class="mobile-draft-button" :icon="EditPen" @click="draftDrawer = true">查看草稿</el-button>
        </header>

        <div ref="chatBody" class="assistant-chat-body">
          <div v-if="mode === 'consult' && !consultMessages.length" class="conversation-empty">
            <div class="conversation-empty-icon"><el-icon><MagicStick /></el-icon></div>
            <h3>今天想聊什么？</h3>
            <p>可以从一个具体问题开始，也可以直接讲讲你的经历和目标。</p>
            <div class="conversation-suggestions">
              <button @click="send('我不知道自己的优势是什么，能帮我梳理一下吗？')">梳理我的优势</button>
              <button @click="send('我想找实习，但不知道应该从哪里开始。')">寻找实习方向</button>
              <button @click="send('如何把项目经历写得更有说服力？')">优化项目表达</button>
            </div>
          </div>

          <div v-for="(message, index) in messages" :key="message.id" class="chat-message" :class="[message.role, { failed: message.failed }]">
            <div class="message-avatar"><el-icon><component :is="message.role === 'assistant' ? MagicStick : UserFilled" /></el-icon></div>
            <div class="message-content">
              <div v-if="message.content" class="message-bubble">{{ message.content }}</div>
              <div v-else class="message-bubble loading-dots">AI 正在思考<span>.</span><span>.</span><span>.</span></div>
              <div class="message-meta">
                <span>{{ formatTime(message.createdAt) }}</span>
                <span v-if="message.failed" class="message-error">发送失败</span>
                <el-button v-if="message.role === 'assistant' && message.content" text :icon="CopyDocument" @click="copyReply(message.content)">复制</el-button>
                <el-button v-if="mode === 'consult' && message.role === 'assistant' && message.content && index === messages.length - 1" text :icon="RefreshRight" @click="regenerate(index)">重新生成</el-button>
                <el-button v-if="message.failed" text :icon="RefreshRight" @click="retry(index)">重试</el-button>
              </div>
            </div>
          </div>
        </div>

        <footer class="assistant-compose">
          <el-input
            v-model="input"
            type="textarea"
            :rows="2"
            resize="none"
            maxlength="4000"
            :disabled="loading"
            :placeholder="mode === 'consult' ? '输入你想聊的内容...' : '直接回答，也可以说“跳过”或继续补充其他经历'"
            @keydown.enter.exact.prevent="send()"
          />
          <el-button v-if="loading" circle :icon="VideoPause" aria-label="停止生成" title="停止生成" @click="stop" />
          <el-button v-else type="primary" circle :icon="Promotion" :disabled="!input.trim()" aria-label="发送消息" title="发送消息" @click="send()" />
        </footer>

        <div v-if="mode === 'consult' && suggestedAction" class="conversation-next-step">
          <span>基于这段对话，下一步可以：</span>
          <button @click="router.push(actionPaths[suggestedAction])">
            <el-icon><component :is="suggestedAction === 'profile' ? EditPen : suggestedAction === 'resume' ? Document : suggestedAction === 'analysis' ? DataAnalysis : suggestedAction === 'growth' ? TrendCharts : Briefcase" /></el-icon>
            {{ actionLabels[suggestedAction] }}
          </button>
        </div>
        <p class="conversation-footnote">对话会保存在这个浏览器中，可从左侧最近对话继续上次的内容。</p>
      </section>

      <aside v-if="mode === 'profile'" class="profile-draft-panel desktop-draft-panel">
        <ProfileDraftPanel v-model:review-input="reviewInput" :draft="draft" :loading="loading" :syncing="syncing" @change="requestChange" @confirm="confirmSync" />
      </aside>
    </div>

    <el-drawer v-model="draftDrawer" title="待确认档案草稿" size="92%" append-to-body>
      <ProfileDraftPanel v-model:review-input="reviewInput" :draft="draft" :loading="loading" :syncing="syncing" @change="requestChange" @confirm="confirmSync" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { ArrowLeft, Check, MagicStick, Promotion, Refresh, UserFilled } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { api } from "@/api";
import { useUserStore } from "@/stores/user";
import { useProfileStore } from "@/stores/profile";
import type { ChatMessage, ChatTurnResponse, StudentProfile } from "@/types/api";

const router = useRouter();
const user = useUserStore();
const profiles = useProfileStore();
const messages = ref<ChatMessage[]>([]);
const input = ref("");
const reviewInput = ref("");
const draft = ref<Record<string, any>>({});
const loading = ref(false);
const syncing = ref(false);
const finished = ref(false);
const questionNumber = ref(0);
const chatBody = ref<HTMLElement>();

const fields = [
  ["name", "姓名"], ["school", "学校"], ["major", "专业"], ["grade", "年级"],
  ["target_city", "目标城市"], ["target_salary", "期望薪资"], ["bio", "个人优势"],
] as const;
const listFields = [
  ["skills", "技能"], ["projects", "项目"], ["competitions", "竞赛"], ["internships", "实习"],
] as const;

function mergeDraft(next: Record<string, unknown>) {
  for (const [key, value] of Object.entries(next || {})) {
    if (Array.isArray(value) && value.length) {
      const existing = Array.isArray(draft.value[key]) ? draft.value[key] : [];
      const identity = (item: any) => item?.name || `${item?.company || ""}-${item?.position || ""}`;
      const merged = [...existing];
      for (const item of value) {
        const index = merged.findIndex((old: any) => identity(old) && identity(old) === identity(item));
        if (index >= 0) merged[index] = { ...merged[index], ...item };
        else merged.push(item);
      }
      draft.value[key] = merged;
    } else if (typeof value === "string" && value.trim()) draft.value[key] = value.trim();
  }
}

async function scrollBottom() {
  await nextTick();
  if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight;
}

function start() {
  if (messages.value.length) return;
  messages.value.push({ role: "assistant", content: "我们用最多 10 个问题把你的就业档案聊完整。不用填表，知道什么就说什么，不确定的内容可以直接说跳过。先从你想找的岗位或方向开始：你希望毕业后做什么？" });
  scrollBottom();
}

async function ask(text?: string) {
  const content = (text ?? input.value).trim();
  if (!content || loading.value || finished.value) return;
  input.value = "";
  messages.value.push({ role: "user", content });
  loading.value = true;
  await scrollBottom();
  try {
    const response: ChatTurnResponse = await api.chatProfileTurn({ user_id: user.userId, messages: messages.value });
    messages.value.push({ role: "assistant", content: response.reply });
    questionNumber.value = response.question_number;
    finished.value = response.finished;
    mergeDraft(response.extracted);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "AI 暂时无法继续访谈");
  } finally {
    loading.value = false;
    await scrollBottom();
  }
}

async function requestChange() {
  const content = reviewInput.value.trim();
  if (!content || loading.value) return;
  reviewInput.value = "";
  finished.value = false;
  await ask(content);
  finished.value = true;
}

async function confirmSync() {
  if (!Object.keys(draft.value).length) return ElMessage.info("暂时没有检测到新的档案信息");
  syncing.value = true;
  try {
    const updated = await api.syncChatProfile({ user_id: user.userId, profile: draft.value });
    profiles.profile = updated;
    user.user = updated;
    ElMessage.success("档案已更新，AI 分析和简历功能会使用最新资料");
    router.push("/profile");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "档案同步失败");
  } finally { syncing.value = false; }
}

function reset() {
  messages.value = [];
  draft.value = {};
  finished.value = false;
  questionNumber.value = 0;
  input.value = "";
  start();
}

onMounted(async () => {
  await profiles.load(user.userId!, true);
  const current = profiles.profile as StudentProfile | null;
  if (current) {
    draft.value = { name: current.name, school: current.school, major: current.major, grade: current.grade };
  }
  start();
});
</script>

<template>
  <div class="profile-assistant-page">
    <div class="profile-assistant-head">
      <div><el-button text :icon="ArrowLeft" @click="router.push('/profile')">返回档案</el-button><span class="assistant-kicker">PROFILE COPILOT</span><h1>和 AI 聊聊，档案会自己变完整</h1><p>最多 10 个问题。你只需要回答和确认，AI 会把自然对话整理成可用于分析、匹配和简历的资料。</p></div>
      <div class="assistant-progress"><strong>{{ questionNumber }}<small>/10</small></strong><span>访谈进度</span><el-progress :percentage="questionNumber * 10" :show-text="false" :stroke-width="7" /></div>
    </div>
    <div class="profile-assistant-layout">
      <section class="profile-chat-panel">
        <header><div class="assistant-avatar"><el-icon><MagicStick /></el-icon></div><div><b>档案 AI 助手</b><span>只记录你明确说过的事实</span></div><el-button text :icon="Refresh" @click="reset">重新开始</el-button></header>
        <div ref="chatBody" class="profile-chat-body">
          <div v-for="(message, index) in messages" :key="index" class="chat-message" :class="message.role"><div class="message-avatar"><el-icon><MagicStick v-if="message.role === 'assistant'" /><UserFilled v-else /></el-icon></div><div class="message-bubble">{{ message.content }}</div></div>
          <div v-if="loading" class="chat-message assistant"><div class="message-avatar"><el-icon><MagicStick /></el-icon></div><div class="message-bubble loading-dots">AI 正在整理<span>.</span><span>.</span><span>.</span></div></div>
        </div>
        <footer><el-input v-model="input" type="textarea" :rows="2" resize="none" :disabled="loading || finished" placeholder="直接回答当前问题，也可以说“跳过”" @keydown.enter.exact.prevent="ask()" /><el-button type="primary" circle :icon="Promotion" :loading="loading" :disabled="!input.trim() || finished" @click="ask()" /></footer>
      </section>
      <aside class="profile-draft-panel">
        <div class="draft-heading"><div><span class="assistant-kicker">REVIEW BEFORE SAVE</span><h2>AI 整理出的档案</h2></div><el-tag effect="plain" type="success">仅待确认</el-tag></div>
        <p class="draft-hint">AI 不会直接修改你的档案。确认内容无误后，再点击底部按钮同步。</p>
        <div class="draft-content">
          <div v-for="[key, label] in fields" :key="key" v-show="draft[key]" class="draft-row"><span>{{ label }}</span><b>{{ draft[key] }}</b></div>
          <div v-for="[key, label] in listFields" :key="key" v-show="draft[key]?.length" class="draft-section"><span>{{ label }} · {{ draft[key]?.length }} 项</span><div class="draft-tags"><el-tag v-for="(item, index) in draft[key]" :key="index" size="small">{{ item.name || item.company }}</el-tag></div></div>
          <el-empty v-if="!Object.keys(draft).some(key => draft[key] && (!Array.isArray(draft[key]) || draft[key].length))" description="回答后，AI 会在这里整理你的资料" :image-size="70" />
        </div>
        <div class="draft-review"><el-input v-model="reviewInput" type="textarea" :rows="2" placeholder="想改成什么？例如：项目里的角色不是负责人，而是前端开发" /><el-button plain :disabled="!reviewInput.trim()" :loading="loading" @click="requestChange">让 AI 按这句话修改</el-button></div>
        <el-button type="primary" class="draft-confirm" :icon="Check" :loading="syncing" :disabled="!finished" @click="confirmSync">确认并更新我的档案</el-button>
      </aside>
    </div>
  </div>
</template>

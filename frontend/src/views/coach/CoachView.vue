<script setup lang="ts">
import { nextTick, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { MagicStick, Promotion, Refresh, UserFilled, UserFilled as ProfileIcon, Document, DataAnalysis, TrendCharts, Briefcase } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useUserStore } from "@/stores/user";
import type { ChatMessage } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";

const user = useUserStore();
const storageKey = () => `career-copilot-chat-${user.userId}`;
const target = ref("");
const input = ref("");
const messages = ref<ChatMessage[]>([]);
const loading = ref(false);
const chatBody = ref<HTMLElement>();
const suggestedAction = ref<"profile" | "resume" | "analysis" | "growth" | "jobs" | null>(null);
const actionLabels = { profile: "去完善档案", resume: "去优化简历", analysis: "去做 AI 画像", growth: "去看成长规划", jobs: "去匹配岗位" } as const;
const actionPaths = { profile: "/profile", resume: "/resume", analysis: "/analysis", growth: "/growth", jobs: "/jobs" } as const;

function persist() {
  localStorage.setItem(storageKey(), JSON.stringify({ target: target.value, messages: messages.value }));
}

async function scrollToBottom() {
  await nextTick();
  if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight;
}

async function send(content?: string) {
  const text = (content ?? input.value).trim();
  if (!text || loading.value) return;
  input.value = "";
  messages.value.push({ role: "user", content: text });
  persist();
  loading.value = true;
  await scrollToBottom();
  try {
    const context = target.value.trim() ? [{ role: "user" as const, content: `当前目标岗位：${target.value.trim()}` }, ...messages.value] : messages.value;
    const result = await api.chatConversation({ user_id: user.userId, messages: context });
    messages.value.push({ role: "assistant", content: result.reply });
    suggestedAction.value = result.suggested_action || null;
    persist();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "AI 暂时无法回复，请稍后重试");
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
}

function reset() {
  messages.value = [];
  input.value = "";
  localStorage.removeItem(storageKey());
  suggestedAction.value = null;
}

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey()) || "null");
    target.value = saved?.target || "";
    messages.value = Array.isArray(saved?.messages) ? saved.messages : [];
  } catch { /* ignore malformed local history */ }
  scrollToBottom();
});
</script>

<template>
  <div class="conversation-page">
    <PageHeader title="AI求职教练" description="随时和 AI 聊聊求职、学习、项目经历和职业方向。">
      <el-button text :icon="Refresh" @click="reset">清空对话</el-button>
    </PageHeader>

    <section class="conversation-shell">
      <header class="conversation-header">
        <div class="conversation-title"><div class="conversation-avatar"><el-icon><MagicStick /></el-icon></div><div><h2>AI 求职助手</h2><p>你的经历、困惑和下一步，都可以从这里开始</p></div></div>
        <el-input v-model="target" class="conversation-target" placeholder="可选：告诉 AI 你的目标岗位" @change="persist" />
      </header>
      <div ref="chatBody" class="conversation-body">
        <div v-if="!messages.length" class="conversation-empty">
          <div class="conversation-empty-icon"><el-icon><MagicStick /></el-icon></div>
          <h3>今天想聊什么？</h3>
          <p>可以问我简历、面试、岗位选择，也可以直接讲讲你的经历。</p>
          <div class="conversation-suggestions"><button @click="send('我不知道自己的优势是什么，能帮我梳理一下吗？')">梳理我的优势</button><button @click="send('我想找实习，但不知道应该从哪里开始。')">寻找实习方向</button><button @click="send('如何把项目经历写得更有说服力？')">优化项目表达</button></div>
        </div>
        <div v-for="(message, index) in messages" :key="index" class="chat-message" :class="message.role"><div class="message-avatar"><el-icon><component :is="message.role === 'assistant' ? MagicStick : UserFilled" /></el-icon></div><div class="message-bubble">{{ message.content }}</div></div>
        <div v-if="loading" class="chat-message assistant"><div class="message-avatar"><el-icon><MagicStick /></el-icon></div><div class="message-bubble loading-dots">AI 正在思考<span>.</span><span>.</span><span>.</span></div></div>
      </div>
      <footer class="conversation-compose"><el-input v-model="input" type="textarea" :rows="2" resize="none" :disabled="loading" placeholder="输入你想聊的内容..." @keydown.enter.exact.prevent="send()" /><el-button type="primary" circle :icon="Promotion" :loading="loading" :disabled="!input.trim()" aria-label="发送消息" @click="send()" /></footer>
      <div v-if="suggestedAction" class="conversation-next-step"><span>基于刚才的对话，下一步可以：</span><button @click="$router.push(actionPaths[suggestedAction!])"><el-icon><component :is="suggestedAction === 'profile' ? ProfileIcon : suggestedAction === 'resume' ? Document : suggestedAction === 'analysis' ? DataAnalysis : suggestedAction === 'growth' ? TrendCharts : Briefcase" /></el-icon>{{ actionLabels[suggestedAction] }}</button></div>
      <p class="conversation-footnote">聊天内容保存在当前浏览器。AI 会参考你的就业档案，但只有你确认后，档案和简历才会更新。</p>
    </section>
  </div>
</template>

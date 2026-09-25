<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { ArrowRight, MagicStick, Promotion, Refresh } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useUserStore } from "@/stores/user";
import type { ChatMessage, ChatTurnResponse, ResumeResponse } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";
import SectionPanel from "@/components/common/SectionPanel.vue";
import StateView from "@/components/common/StateView.vue";

const user = useUserStore();
const target = ref("");
const original = ref("");
const result = ref<ResumeResponse | null>(null);
const loading = ref(true);
const running = ref(false);
const loadingHistory = ref(false);
const messages = ref<ChatMessage[]>([]);
const input = ref("");
const questionNumber = ref(0);
const finished = ref(false);
const extracted = ref<Record<string, unknown>>({});
const error = ref("");
const interviewBody = ref<HTMLElement>();

const isFirstRun = computed(() => !result.value);
const progress = computed(() => Math.min(questionNumber.value * 10, 100));
const storageKey = () => `career-copilot-chat-${user.userId}`;

function mergeExtracted(next: Record<string, unknown>) {
  for (const [key, value] of Object.entries(next || {})) {
    if (Array.isArray(value) && value.length) extracted.value[key] = value;
    else if (typeof value === "string" && value.trim()) extracted.value[key] = value;
  }
}

async function scrollInterview() {
  await nextTick();
  if (interviewBody.value) interviewBody.value.scrollTop = interviewBody.value.scrollHeight;
}

async function load() {
  loading.value = true;
  try {
    const history = await api.resumes(user.userId!);
    if (history[0]) {
      result.value = await api.resumeDetail(history[0].id);
      target.value = result.value.target_job;
    }
    const saved = JSON.parse(localStorage.getItem(storageKey()) || "null");
    if (Array.isArray(saved?.messages)) messages.value = saved.messages;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "简历记录加载失败";
  } finally { loading.value = false; }
}

function startInterview() {
  if (!target.value.trim()) return ElMessage.warning("请先填写目标岗位");
  if (messages.value.length) return;
  messages.value.push({ role: "assistant", content: `我们先用几分钟建立你的第一版简历。最多 10 个问题，不需要准备初稿。先说说你做过的一个项目：项目目标是什么，你具体负责哪部分？` });
  scrollInterview();
}

async function answerInterview() {
  const text = input.value.trim();
  if (!text || running.value || questionNumber.value >= 10) return;
  input.value = "";
  messages.value.push({ role: "user", content: text });
  running.value = true;
  try {
    const response: ChatTurnResponse = await api.chatTurn({ user_id: user.userId, target_job: target.value, messages: messages.value });
    messages.value.push({ role: "assistant", content: response.reply });
    questionNumber.value = response.question_number;
    finished.value = response.finished;
    mergeExtracted(response.extracted);
  } catch (e) { ElMessage.error(e instanceof Error ? e.message : "访谈暂时无法继续"); }
  finally { running.value = false; await scrollInterview(); }
}

async function generateInitial() {
  if (!messages.value.length || (!finished.value && questionNumber.value < 10)) return ElMessage.info("请先完成访谈，至少回答当前问题");
  running.value = true;
  try {
    result.value = await api.chatResume({ user_id: user.userId, target_job: target.value, messages: messages.value, extracted: extracted.value });
    ElMessage.success("初始简历已生成，接下来可以持续补充优化");
  } catch (e) { ElMessage.error(e instanceof Error ? e.message : "初始简历生成失败"); }
  finally { running.value = false; }
}

async function optimize() {
  if (!target.value.trim()) return ElMessage.warning("请填写目标岗位");
  if (!original.value.trim() && !messages.value.length) return ElMessage.info("请先输入想补充的内容，或前往 AI 求职教练聊天");
  running.value = true;
  try {
    const transcript = messages.value.map((message) => `${message.role}: ${message.content}`).join("\n");
    result.value = await api.resume({ user_id: user.userId, target_job: target.value, original_resume: `${original.value.trim()}\n\nAI对话补充：\n${transcript}`.slice(0, 10000) });
    original.value = "";
    ElMessage.success("简历已根据新内容优化");
  } catch (e) { ElMessage.error(e instanceof Error ? e.message : "简历优化失败"); }
  finally { running.value = false; }
}

async function useChatContext() {
  const saved = JSON.parse(localStorage.getItem(storageKey()) || "null");
  messages.value = Array.isArray(saved?.messages) ? saved.messages : messages.value;
  if (!messages.value.length) return ElMessage.info("AI 对话页还没有可用的聊天内容");
  ElMessage.success("已读取 AI 对话内容，可以点击优化简历");
}

function resetInterview() {
  messages.value = [];
  extracted.value = {};
  questionNumber.value = 0;
  finished.value = false;
  result.value = null;
}

onMounted(load);
</script>

<template>
  <div class="resume-workspace">
    <PageHeader title="AI简历优化" :description="isFirstRun ? '不用上传初稿，AI 通过最多 10 个问题帮你建立第一版简历。' : '你的简历会随着新经历和 AI 对话持续变得更准确、更有竞争力。'"><el-button v-if="isFirstRun && messages.length" text :icon="Refresh" @click="resetInterview">重新开始访谈</el-button><el-button v-else-if="!isFirstRun" type="primary" :icon="MagicStick" :loading="running" @click="optimize">立即优化</el-button></PageHeader>
    <StateView :loading="loading" :error="error" @retry="load"><template #content>
      <div v-if="isFirstRun">
        <section class="resume-interview-hero"><div><span class="resume-kicker">FIRST RESUME</span><h2>先把经历聊清楚，再生成你的第一版简历</h2><p>AI 会主动追问项目、技能和成果，最多 10 个问题。每个回答都会成为简历的真实素材。</p></div><div class="resume-interview-progress"><strong>{{ questionNumber }}<small>/10</small></strong><span>访谈进度</span><el-progress :percentage="progress" :show-text="false" :stroke-width="7" /></div></section>
        <div class="resume-interview-card"><header><div><h3>AI 简历访谈</h3><p>目标岗位决定简历重点，请先告诉 AI 你想申请什么。</p></div><el-tag type="info" effect="plain">{{ finished ? '可以生成' : '最多 10 问' }}</el-tag></header><div ref="interviewBody" class="interview-body"><div v-if="!messages.length" class="interview-empty"><el-icon><MagicStick /></el-icon><b>从目标岗位开始</b><p>不需要上传初稿，也不需要提前组织语言。</p><div class="suggestion-row"><button @click="target = '前端开发工程师'; startInterview()">前端开发工程师</button><button @click="target = 'Java 后端开发'; startInterview()">Java 后端开发</button><button @click="target = '产品经理'; startInterview()">产品经理</button></div></div><div v-for="(message, index) in messages" :key="index" class="chat-message" :class="message.role"><div class="message-avatar"><el-icon><MagicStick /></el-icon></div><div class="message-bubble">{{ message.content }}</div></div><div v-if="running" class="chat-message assistant"><div class="message-avatar"><el-icon><MagicStick /></el-icon></div><div class="message-bubble loading-dots">AI 正在整理<span>.</span><span>.</span><span>.</span></div></div></div><div class="interview-controls"><div class="interview-target"><el-input v-model="target" placeholder="目标岗位，例如：前端开发工程师" :disabled="!!messages.length"/><el-button type="primary" :disabled="!!messages.length" @click="startInterview">开始访谈</el-button></div><div class="interview-input"><el-input v-model="input" type="textarea" :rows="2" resize="none" :disabled="!messages.length || running || questionNumber >= 10" placeholder="直接回答当前问题..." @keydown.enter.exact.prevent="answerInterview"/><el-button type="primary" circle :icon="Promotion" :loading="running" :disabled="!input.trim()" @click="answerInterview"/></div></div></div>
        <div class="resume-interview-actions"><el-button type="primary" :icon="MagicStick" :loading="running" :disabled="!finished && questionNumber < 10" @click="generateInitial">生成我的第一版简历</el-button><span>生成后可以继续补充，不满意的内容随时重新优化。</span></div>
      </div>
      <div v-else class="resume-result-layout"><section><div class="resume-current-card"><div class="resume-card-heading"><div><span class="resume-kicker">CURRENT VERSION</span><h2>{{ result?.target_job }}简历</h2><p>最近更新：{{ result?.created_at || '刚刚' }}</p></div><div class="resume-score"><strong>{{ result?.result.resume_score }}</strong><span>综合评分</span></div></div><div class="resume-summary"><span>个人简介</span><p>{{ result?.result.personal_summary || '暂无个人简介' }}</p></div><h3>项目经历优化</h3><div v-for="item in result?.result.optimized_projects" :key="item.project_name" class="resume-compare"><b>{{ item.project_name }}</b><del>{{ item.original }}</del><p>{{ item.optimized }}</p><div class="tag-row"><el-tag v-for="tag in item.highlight_tags" :key="tag" size="small">{{ tag }}</el-tag></div></div><h3>整体建议</h3><ul class="result-list"><li v-for="item in result?.result.overall_suggestions" :key="item">{{ item }}</li></ul></div></section><aside class="resume-improve-panel"><SectionPanel title="继续优化" subtitle="告诉 AI 新经历，或者读取 AI 对话页内容"><el-input v-model="original" type="textarea" :rows="9" maxlength="10000" show-word-limit placeholder="例如：我刚完成了一个校园二手交易项目，负责商品搜索和推荐功能……"/><div class="resume-improve-actions"><el-button plain :icon="ArrowRight" @click="useChatContext">读取 AI 对话内容</el-button><el-button type="primary" :icon="MagicStick" :loading="running" @click="optimize">根据补充内容优化</el-button></div></SectionPanel><SectionPanel title="优化目标"><el-input v-model="target" placeholder="目标岗位"/><p class="side-note">每次优化都会生成一条新的简历记录，旧版本仍然保留。</p></SectionPanel></aside></div>
    </template></StateView>
  </div>
</template>

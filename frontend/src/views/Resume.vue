<!--
  文件名称：Resume.vue
  文件作用：简历优化页 —— 输入目标岗位，AI 优化项目与技能描述并给出建议。
-->
<template>
  <div class="page resume-page">
    <p v-reveal class="section-kicker">Resume Optimization</p>
    <h1 v-reveal class="section-title">简历<span class="accent">优化</span></h1>
    <p v-reveal class="section-sub">针对目标岗位，让 AI 用 STAR 法则改写项目与技能描述，提升简历竞争力。</p>

    <section v-reveal class="glass panel">
      <div class="two-col">
        <div class="field">
          <label>目标岗位 *</label>
          <input v-model="targetJob" class="input" placeholder="如 Java后端开发工程师" />
        </div>
        <div class="field">
          <label>数据来源</label>
          <div class="source-hint">
            <span v-if="hasUser" class="tag cyan">使用档案 #{{ store.currentUserId }} {{ store.profile?.name }}</span>
            <span v-else class="tag amber">未创建档案，将按空资料处理</span>
          </div>
        </div>
      </div>
      <div class="field">
        <label>原始简历文本（可选，将作为优化参考）</label>
        <textarea v-model="originalResume" class="textarea" placeholder="粘贴你的现有简历内容，或留空由 AI 基于档案生成"></textarea>
      </div>
      <div class="panel-actions">
        <button class="btn btn-primary" :disabled="optimizing" @click="run">
          {{ optimizing ? "优化中…" : "开始优化" }}
        </button>
        <span v-if="hasUser" class="hint">基于档案经历自动优化</span>
      </div>
    </section>

    <Loading v-if="optimizing" text="AI 正在优化你的简历…" />

    <template v-else-if="result">
      <section v-reveal class="glass panel">
        <div class="report-top">
          <div class="score-block">
            <div class="big-number">{{ result.result.resume_score }}</div>
            <div class="score-label">简历评分</div>
          </div>
          <div class="report-summary">
            <span class="tag cyan">{{ result.target_job }}</span>
            <span v-if="result.is_mock" class="tag amber">Mock 演示结果</span>
            <p class="summary-text">{{ result.result.personal_summary }}</p>
          </div>
        </div>

        <div class="divider"></div>

        <div v-if="result.result.optimized_projects.length" class="report-section">
          <h4>项目描述优化</h4>
          <div class="opt-list">
            <div v-for="(p, i) in result.result.optimized_projects" :key="i" class="opt-card">
              <h5>{{ p.project_name }}</h5>
              <div class="before">原：{{ p.original }}</div>
              <div class="after">改：{{ p.optimized }}</div>
              <div class="tag-row">
                <span v-for="t in p.highlight_tags" :key="t" class="tag violet">{{ t }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="result.result.optimized_skills.length" class="report-section">
          <h4>技能描述优化</h4>
          <div class="opt-list">
            <div v-for="(s, i) in result.result.optimized_skills" :key="i" class="opt-card">
              <div class="before">原：{{ s.original }}</div>
              <div class="after">改：{{ s.optimized }}</div>
            </div>
          </div>
        </div>

        <div v-if="result.result.overall_suggestions.length" class="report-section">
          <h4>整体建议</h4>
          <ul class="bullet-list">
            <li v-for="(s, i) in result.result.overall_suggestions" :key="i">{{ s }}</li>
          </ul>
        </div>
      </section>
    </template>

    <section v-if="history.length" v-reveal class="glass panel">
      <h2 class="panel-title">历史记录</h2>
      <div class="history-list">
        <button v-for="h in history" :key="h.id" class="history-item" @click="loadHistoryItem(h.id)">
          <span class="tag cyan">{{ h.target_job }}</span>
          <b>{{ h.resume_score }} 分</b>
          <span class="muted">{{ h.created_at }}</span>
        </button>
      </div>
    </section>

    <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import Loading from "@/components/common/Loading.vue";
import { useUserStore } from "@/store/user";
import { optimizeResume, getResumeOptimization, getResumeHistory } from "@/api/resume";
import type { ResumeHistoryItem, ResumeOptimizationResponse } from "@/api/types";

const store = useUserStore();
const hasUser = computed(() => store.profile !== null);

const targetJob = ref("");
const originalResume = ref("");
const optimizing = ref(false);
const result = ref<ResumeOptimizationResponse | null>(null);
const history = ref<ResumeHistoryItem[]>([]);
const errorMsg = ref("");

async function run() {
  errorMsg.value = "";
  if (!targetJob.value.trim()) {
    errorMsg.value = "请填写目标岗位";
    return;
  }
  optimizing.value = true;
  try {
    const res = await optimizeResume({
      user_id: store.currentUserId ?? undefined,
      target_job: targetJob.value.trim(),
      original_resume: originalResume.value.trim() || undefined,
    });
    result.value = res.data;
    loadHistory();
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "优化失败";
  } finally {
    optimizing.value = false;
  }
}

async function loadHistory() {
  if (!store.currentUserId) return;
  try {
    const res = await getResumeHistory(store.currentUserId);
    history.value = res.data;
  } catch {
    history.value = [];
  }
}

async function loadHistoryItem(id: number) {
  errorMsg.value = "";
  try {
    const res = await getResumeOptimization(id);
    result.value = res.data;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载失败";
  }
}

onMounted(() => {
  if (store.currentUserId) {
    store.fetchProfile().then(() => loadHistory());
  }
});
</script>

<style scoped>
.panel {
  padding: 26px 28px;
  margin-bottom: 26px;
}
.panel-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 18px;
}
.panel-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}
.source-hint {
  display: flex;
  align-items: center;
  min-height: 44px;
}
.hint {
  font-size: 13px;
  color: var(--text-2);
}

.report-top {
  display: flex;
  gap: 28px;
  align-items: flex-start;
  flex-wrap: wrap;
}
.score-block {
  text-align: center;
  min-width: 140px;
}
.score-label {
  color: var(--text-2);
  font-size: 13px;
  margin-top: 8px;
}
.report-summary {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
}
.summary-text {
  color: var(--text-1);
  font-size: 14px;
  line-height: 1.8;
}
.report-section {
  margin-bottom: 22px;
}
.report-section h4 {
  font-size: 14px;
  color: var(--cyan);
  letter-spacing: 1px;
  margin-bottom: 12px;
}

.opt-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.opt-card {
  padding: 16px 18px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: rgba(8, 11, 24, 0.4);
}
.opt-card h5 {
  font-size: 15px;
  margin-bottom: 8px;
}
.before {
  color: var(--text-2);
  font-size: 13.5px;
  margin-bottom: 6px;
}
.after {
  color: var(--text-0);
  font-size: 13.5px;
  margin-bottom: 10px;
  line-height: 1.7;
}
.bullet-list {
  padding-left: 20px;
  color: var(--text-1);
  font-size: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.history-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: rgba(8, 11, 24, 0.4);
  color: var(--text-1);
  font-size: 13.5px;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.25s;
}
.history-item:hover {
  border-color: var(--cyan);
}
.history-item b {
  color: var(--text-0);
  margin-left: auto;
}
.muted {
  color: var(--text-2);
  font-size: 12px;
}
</style>
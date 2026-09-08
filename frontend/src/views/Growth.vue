<!--
  文件名称：Growth.vue
  文件作用：成长规划页 —— 基于目标岗位生成能力差距、学习路线与资源推荐。
-->
<template>
  <div class="page growth-page">
    <p v-reveal class="section-kicker">Growth Planning</p>
    <h1 v-reveal class="section-title">成长<span class="accent">规划</span></h1>
    <p v-reveal class="section-sub">围绕目标岗位，AI 为你梳理能力差距、阶段路线、实战项目与学习资源。</p>

    <section v-reveal class="glass panel">
      <div class="two-col">
        <div class="field">
          <label>目标岗位 *</label>
          <input v-model="targetJob" class="input" placeholder="如 AI应用开发工程师" />
        </div>
        <div class="field">
          <label>数据来源</label>
          <div class="source-hint">
            <span v-if="hasUser" class="tag cyan">使用档案 #{{ store.currentUserId }} {{ store.profile?.name }}</span>
            <span v-else class="tag amber">未创建档案，将按空资料处理</span>
          </div>
        </div>
      </div>
      <button class="btn btn-primary" :disabled="generating" @click="run">
        {{ generating ? "生成中…" : "生成成长规划" }}
      </button>
    </section>

    <Loading v-if="generating" text="AI 正在规划你的成长路线…" />

    <template v-else-if="result">
      <section v-reveal class="glass panel">
        <div class="panel-head">
          <h2 class="panel-title">规划概览</h2>
          <div class="tag-row">
            <span class="tag cyan">{{ result.target_job }}</span>
            <span v-if="result.is_mock" class="tag amber">Mock 演示结果</span>
          </div>
        </div>
        <p class="summary-text">{{ result.result.current_situation }}</p>
        <p v-if="result.result.expected_timeline" class="timeline-tip">
          预计周期：<b>{{ result.result.expected_timeline }}</b>
        </p>
      </section>

      <section v-if="result.result.ability_gaps.length" v-reveal class="glass panel">
        <h2 class="panel-title">能力差距</h2>
        <div class="grid-cards">
          <div v-for="g in result.result.ability_gaps" :key="g.skill" class="gap-card glass">
            <div class="gap-head">
              <h3>{{ g.skill }}</h3>
            </div>
            <div class="tag-row">
              <span class="tag" :class="importanceClass(g.importance)">{{ g.importance }}</span>
              <span class="tag violet">{{ g.difficulty }} 难度</span>
            </div>
            <p class="gap-desc">{{ g.description }}</p>
          </div>
        </div>
      </section>

      <section v-if="result.result.learning_roadmap.length" v-reveal class="glass panel">
        <h2 class="panel-title">学习路线</h2>
        <div class="roadmap">
          <div v-for="(s, i) in result.result.learning_roadmap" :key="i" class="road-node">
            <div class="road-dot">{{ i + 1 }}</div>
            <div class="road-card glass">
              <h3>{{ s.stage }}</h3>
              <p class="road-focus">{{ s.focus }}</p>
              <ul class="bullet-list">
                <li v-for="t in s.tasks" :key="t">{{ t }}</li>
              </ul>
              <p class="road-milestone">里程碑：{{ s.milestone }}</p>
            </div>
          </div>
        </div>
      </section>

      <section v-if="result.result.recommended_projects.length" v-reveal class="glass panel">
        <h2 class="panel-title">实战项目推荐</h2>
        <div class="grid-cards">
          <div v-for="p in result.result.recommended_projects" :key="p.name" class="proj-card glass">
            <h3>{{ p.name }}</h3>
            <span class="tag amber">{{ p.difficulty }}</span>
            <p class="gap-desc">{{ p.description }}</p>
            <div class="tag-row">
              <span v-for="t in p.tech_stack" :key="t" class="chip">{{ t }}</span>
            </div>
          </div>
        </div>
      </section>

      <section v-reveal class="two-col-wider">
        <div v-if="result.result.recommended_resources.length" class="glass panel">
          <h2 class="panel-title">学习资源</h2>
          <ul class="bullet-list">
            <li v-for="r in result.result.recommended_resources" :key="r">{{ r }}</li>
          </ul>
        </div>
        <div v-if="result.result.interview_prep_tips.length" class="glass panel">
          <h2 class="panel-title">面试准备</h2>
          <ul class="bullet-list">
            <li v-for="t in result.result.interview_prep_tips" :key="t">{{ t }}</li>
          </ul>
        </div>
      </section>
    </template>

    <section v-if="history.length" v-reveal class="glass panel">
      <h2 class="panel-title">历史记录</h2>
      <div class="history-list">
        <button v-for="h in history" :key="h.id" class="history-item" @click="loadHistoryItem(h.id)">
          <span class="tag cyan">{{ h.target_job }}</span>
          <span>{{ h.expected_timeline }}</span>
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
import { generatePlan, getPlan, getPlanHistory } from "@/api/growth";
import type { GrowthHistoryItem, GrowthPlanResponse } from "@/api/types";

const store = useUserStore();
const hasUser = computed(() => store.profile !== null);

const targetJob = ref("");
const generating = ref(false);
const result = ref<GrowthPlanResponse | null>(null);
const history = ref<GrowthHistoryItem[]>([]);
const errorMsg = ref("");

function importanceClass(v: string) {
  if (v === "必须") return "red";
  if (v === "加分") return "green";
  return "";
}

async function run() {
  errorMsg.value = "";
  if (!targetJob.value.trim()) {
    errorMsg.value = "请填写目标岗位";
    return;
  }
  generating.value = true;
  try {
    const res = await generatePlan({
      user_id: store.currentUserId ?? undefined,
      target_job: targetJob.value.trim(),
    });
    result.value = res.data;
    loadHistory();
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "生成失败";
  } finally {
    generating.value = false;
  }
}

async function loadHistory() {
  if (!store.currentUserId) return;
  try {
    const res = await getPlanHistory(store.currentUserId);
    history.value = res.data;
  } catch {
    history.value = [];
  }
}

async function loadHistoryItem(id: number) {
  errorMsg.value = "";
  try {
    const res = await getPlan(id);
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
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}
.panel-head .panel-title {
  margin-bottom: 0;
}
.source-hint {
  display: flex;
  align-items: center;
  min-height: 44px;
}
.summary-text {
  color: var(--text-1);
  font-size: 14px;
  line-height: 1.9;
}
.timeline-tip {
  margin-top: 14px;
  color: var(--text-1);
  font-size: 14px;
}
.timeline-tip b {
  color: var(--cyan);
}

.gap-card {
  padding: 18px 20px;
}
.gap-head h3 {
  font-size: 17px;
  margin-bottom: 10px;
}
.gap-desc {
  color: var(--text-1);
  font-size: 13.5px;
  margin-top: 10px;
  line-height: 1.7;
}

.roadmap {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding-left: 8px;
}
.road-node {
  position: relative;
  padding-left: 34px;
  padding-bottom: 16px;
}
.road-node::before {
  content: "";
  position: absolute;
  left: 13px;
  top: 30px;
  bottom: 0;
  width: 2px;
  background: linear-gradient(var(--border-strong), transparent);
}
.road-node:last-child::before {
  display: none;
}
.road-dot {
  position: absolute;
  left: 0;
  top: 2px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--grad-neon);
  color: #05070f;
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--glow-blue);
}
.road-card {
  padding: 16px 18px;
}
.road-card h3 {
  font-size: 16px;
  margin-bottom: 6px;
}
.road-focus {
  color: var(--cyan);
  font-size: 13px;
  margin-bottom: 8px;
}
.road-milestone {
  margin-top: 10px;
  color: var(--amber);
  font-size: 13px;
}

.proj-card {
  padding: 18px 20px;
}
.proj-card h3 {
  font-size: 16px;
  margin-bottom: 10px;
}
.proj-card .tag {
  margin-bottom: 10px;
}

.two-col-wider {
  display: grid;
  gap: 22px;
  grid-template-columns: 1fr 1fr;
  align-items: start;
}
.two-col-wider .panel {
  margin-bottom: 0;
}
@media (max-width: 860px) {
  .two-col-wider {
    grid-template-columns: 1fr;
  }
  .two-col-wider .panel {
    margin-bottom: 26px;
  }
}

.bullet-list {
  padding-left: 20px;
  color: var(--text-1);
  font-size: 14px;
  display: flex;
  flex-direction: column;
  gap: 7px;
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
.history-item .muted {
  margin-left: auto;
  color: var(--text-2);
  font-size: 12px;
}
</style>
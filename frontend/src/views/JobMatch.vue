<!--
  文件名称：JobMatch.vue
  文件作用：岗位匹配页 —— 岗位库搜索/详情 + 技能匹配结果。
-->
<template>
  <div class="page job-page">
    <p v-reveal class="section-kicker">Job Matching</p>
    <h1 v-reveal class="section-title">岗位<span class="accent">匹配</span></h1>
    <p v-reveal class="section-sub">搜索岗位库，或用你的技能与岗位需求智能比对，输出匹配度与差距。</p>

    <div class="match-grid">
      <!-- 左侧：岗位库 -->
      <section v-reveal class="glass panel">
        <h2 class="panel-title">岗位库</h2>
        <div class="search-row">
          <input
            v-model="keyword"
            class="input"
            placeholder="搜索岗位，如 Java、前端、AI…"
            @keyup.enter="searchJobs"
          />
          <select v-model="category" class="select cat-select" @change="searchJobs">
            <option value="">全部分类</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
          <button class="btn btn-primary" @click="searchJobs">搜索</button>
        </div>

        <div v-if="loadingJobs" class="empty"><Loading text="加载岗位中…" /></div>
        <div v-else-if="jobs.length" class="job-list">
          <button
            v-for="job in jobs"
            :key="job.job_id"
            class="job-card glass"
            @click="openDetail(job.job_id)"
          >
            <div class="job-head">
              <span class="job-title">{{ job.title }}</span>
              <span class="tag cyan">{{ job.category }}</span>
            </div>
            <p class="job-snippet">{{ job.snippet }}</p>
            <div class="tag-row">
              <span v-for="t in job.tags.slice(0, 4)" :key="t" class="chip">{{ t }}</span>
            </div>
          </button>
          <div class="pager">
            <button class="btn btn-ghost btn-sm" :disabled="page <= 1" @click="changePage(-1)">上一页</button>
            <span class="pager-info">{{ page }} / {{ totalPages }}</span>
            <button class="btn btn-ghost btn-sm" :disabled="page >= totalPages" @click="changePage(1)">下一页</button>
          </div>
        </div>
        <div v-else class="empty">未找到相关岗位</div>
      </section>

      <!-- 右侧：技能匹配 -->
      <section v-reveal="'80ms'" class="glass panel">
        <h2 class="panel-title">技能匹配</h2>
        <div class="field">
          <label>你的技能（逗号分隔，1-50 项）</label>
          <textarea
            v-model="skillsInput"
            class="textarea"
            placeholder="Java, Spring Boot, MySQL, Redis, Git"
          ></textarea>
          <div class="actions-inline">
            <button class="btn btn-ghost btn-sm" :disabled="!hasUser" @click="importSkills">
              从我的档案导入
            </button>
          </div>
        </div>
        <div class="field">
          <label>目标分类（可选）</label>
          <select v-model="matchCategory" class="select">
            <option value="">不限</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="field">
          <label>返回数量</label>
          <input v-model.number="topK" type="number" min="1" max="20" class="input" />
        </div>
        <button class="btn btn-primary" :disabled="matching" @click="runMatch">
          {{ matching ? "匹配中…" : "开始匹配" }}
        </button>
        <p v-if="lastRecordId" class="hint" style="margin-top: 10px">
          已保存匹配记录 #{{ lastRecordId }}
        </p>

        <Loading v-if="matching" text="AI 正在计算匹配度…" />

        <div v-else-if="matchResult" class="match-results">
          <div
            v-for="m in matchResult.matches"
            :key="m.job_id"
            class="match-card glass"
          >
            <div class="match-head">
              <span class="job-title">{{ m.title }}</span>
              <span class="tag cyan">{{ m.category }}</span>
            </div>
            <div class="score-line">
              <div class="score-track">
                <div
                  class="score-fill"
                  :class="scoreClass(m.match_score)"
                  :style="{ width: m.match_score + '%' }"
                ></div>
              </div>
              <b class="score-num">{{ m.match_score }}</b>
            </div>
            <div class="match-meta">
              <div class="tag-row">
                <span v-for="s in m.matched_skills" :key="s" class="chip green-hit">✓ {{ s }}</span>
              </div>
              <div v-if="m.missing_skills.length" class="tag-row">
                <span v-for="s in m.missing_skills" :key="s" class="chip miss">△ {{ s }}</span>
              </div>
            </div>
            <p v-if="m.match_reason" class="match-reason">{{ m.match_reason }}</p>
            <div v-if="m.learning_suggestions?.length" class="match-extra">
              <h5>学习建议</h5>
              <ul class="bullet-list">
                <li v-for="s in m.learning_suggestions" :key="s">{{ s }}</li>
              </ul>
            </div>
          </div>
        </div>
        <div v-else class="empty">输入技能后点击「开始匹配」</div>
      </section>
    </div>

    <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

    <!-- 岗位详情弹窗 -->
    <div v-if="detail" class="modal-mask" @click.self="detail = null">
      <div class="modal glass">
        <div class="modal-head">
          <div>
            <h3 class="modal-title">{{ detail.title }}</h3>
            <div class="tag-row" style="margin-top: 8px">
              <span class="tag cyan">{{ detail.category }}</span>
              <span v-for="t in detail.tags" :key="t" class="chip">{{ t }}</span>
            </div>
          </div>
          <button class="btn btn-ghost btn-sm" @click="detail = null">关闭</button>
        </div>
        <div class="modal-body job-content" v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import Loading from "@/components/common/Loading.vue";
import { useUserStore } from "@/store/user";
import { getJobList, getJobDetail, startMatch } from "@/api/jobMatch";
import type { JobDetail, JobListItem, MatchResult } from "@/api/types";

const store = useUserStore();
const hasUser = computed(() => store.profile !== null);

const categories = ["前端", "后端", "AI", "数据", "移动端", "运维", "测试", "产品", "运营", "安全"];

/* 岗位库 */
const keyword = ref("");
const category = ref("");
const jobs = ref<JobListItem[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 9;
const loadingJobs = ref(false);
const detail = ref<JobDetail | null>(null);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)));

/* 匹配 */
const skillsInput = ref("");
const matchCategory = ref("");
const topK = ref(5);
const matching = ref(false);
const matchResult = ref<MatchResult | null>(null);
const lastRecordId = ref<number | null>(null);
const errorMsg = ref("");

function scoreClass(score: number) {
  if (score >= 70) return "high";
  if (score >= 40) return "mid";
  return "low";
}

async function searchJobs() {
  loadingJobs.value = true;
  page.value = 1;
  try {
    const res = await getJobList({ keyword: keyword.value, category: category.value || undefined, page: 1, page_size: pageSize });
    jobs.value = res.data.items;
    total.value = res.data.total;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载失败";
  } finally {
    loadingJobs.value = false;
  }
}

async function changePage(delta: number) {
  page.value += delta;
  loadingJobs.value = true;
  try {
    const res = await getJobList({ keyword: keyword.value, category: category.value || undefined, page: page.value, page_size: pageSize });
    jobs.value = res.data.items;
    total.value = res.data.total;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载失败";
  } finally {
    loadingJobs.value = false;
  }
}

async function openDetail(jobId: string) {
  errorMsg.value = "";
  try {
    const res = await getJobDetail(jobId);
    detail.value = res.data;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载详情失败";
  }
}

function importSkills() {
  const names = (store.profile?.skills ?? []).map((s) => s.name);
  skillsInput.value = names.join(", ");
}

function parseSkills(): string[] {
  return skillsInput.value
    .split(/[,，]/)
    .map((s) => s.trim())
    .filter(Boolean)
    .slice(0, 50);
}

async function runMatch() {
  errorMsg.value = "";
  const skills = parseSkills();
  if (!skills.length) {
    errorMsg.value = "请输入至少一项技能";
    return;
  }
  matching.value = true;
  try {
    const res = await startMatch({
      skills,
      job_category: matchCategory.value || null,
      top_k: topK.value,
      user_id: store.currentUserId ?? null,
    });
    matchResult.value = res.data;
    lastRecordId.value = res.data.record_id;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "匹配失败";
  } finally {
    matching.value = false;
  }
}

/* 简易 Markdown 渲染（内容来自自有知识库，先转义再轻量渲染） */
const renderedContent = computed(() => {
  if (!detail.value) return "";
  return renderMarkdown(detail.value.content);
});

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderMarkdown(md: string): string {
  const lines = md.split("\n");
  let html = "";
  let inList = false;
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (line.startsWith("### ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<h3>${escapeHtml(line.slice(4))}</h3>`;
    } else if (line.startsWith("## ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<h2>${escapeHtml(line.slice(3))}</h2>`;
    } else if (line.startsWith("# ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<h1>${escapeHtml(line.slice(2))}</h1>`;
    } else if (/^[-*]\s+/.test(line)) {
      if (!inList) { html += "<ul>"; inList = true; }
      html += `<li>${escapeHtml(line.replace(/^[-*]\s+/, ""))}</li>`;
    } else if (line.trim() === "") {
      if (inList) { html += "</ul>"; inList = false; }
    } else {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<p>${escapeHtml(line)}</p>`;
    }
  }
  if (inList) html += "</ul>";
  return html;
}

onMounted(searchJobs);
</script>

<style scoped>
.match-grid {
  display: grid;
  gap: 22px;
  grid-template-columns: 1.05fr 0.95fr;
  align-items: start;
}
@media (max-width: 960px) {
  .match-grid {
    grid-template-columns: 1fr;
  }
}

.panel {
  padding: 24px 26px;
}
.panel-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 18px;
}
.search-row {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}
.search-row .input {
  flex: 1;
}
.cat-select {
  flex: 0 0 120px;
}

.job-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.job-card {
  text-align: left;
  padding: 16px 18px;
  cursor: pointer;
}
.job-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}
.job-title {
  font-weight: 700;
  font-size: 15.5px;
}
.job-snippet {
  color: var(--text-1);
  font-size: 13px;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-top: 16px;
}
.pager-info {
  color: var(--text-2);
  font-size: 13px;
}

.actions-inline {
  margin-top: 8px;
}
.match-results {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
}
.match-card {
  padding: 16px 18px;
}
.match-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.score-line {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.score-track {
  flex: 1;
  height: 8px;
  background: rgba(91, 124, 255, 0.12);
  border-radius: 999px;
  overflow: hidden;
}
.score-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.score-fill.high {
  background: linear-gradient(90deg, var(--cyan), var(--green));
}
.score-fill.mid {
  background: linear-gradient(90deg, var(--blue), var(--amber));
}
.score-fill.low {
  background: linear-gradient(90deg, var(--amber), var(--red));
}
.score-num {
  font-family: var(--font-mono);
  font-size: 20px;
  min-width: 46px;
  text-align: right;
}
.match-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
}
.chip.green-hit {
  border-color: rgba(52, 211, 153, 0.4);
  color: var(--green);
}
.chip.miss {
  border-color: rgba(251, 191, 36, 0.4);
  color: var(--amber);
}
.match-reason {
  color: var(--text-1);
  font-size: 13px;
  line-height: 1.7;
}
.match-extra {
  margin-top: 10px;
}
.match-extra h5 {
  font-size: 13px;
  color: var(--cyan);
  margin-bottom: 6px;
}
.bullet-list {
  padding-left: 18px;
  color: var(--text-1);
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 弹窗 */
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(4, 5, 14, 0.7);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.modal {
  width: min(760px, 100%);
  max-height: 84vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 22px 24px;
  border-bottom: 1px solid var(--border);
}
.modal-title {
  font-size: 20px;
}
.modal-body {
  overflow-y: auto;
  padding: 22px 24px;
}
.job-content :deep(h1) {
  font-size: 22px;
  margin-bottom: 14px;
}
.job-content :deep(h2) {
  font-size: 17px;
  margin: 18px 0 8px;
  color: var(--cyan);
}
.job-content :deep(h3) {
  font-size: 15px;
  margin: 14px 0 6px;
  color: var(--text-0);
}
.job-content :deep(p),
.job-content :deep(li) {
  color: var(--text-1);
  font-size: 14px;
  line-height: 1.8;
}
.job-content :deep(ul) {
  padding-left: 20px;
  margin: 6px 0;
}
.hint {
  font-size: 12.5px;
  color: var(--text-2);
}
</style>
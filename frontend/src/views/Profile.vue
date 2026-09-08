<!--
  文件名称：Profile.vue
  文件作用：AI 就业画像页 —— 学生资料 + 学习经历管理 + 画像报告 + 历史记录。
-->
<template>
  <div class="page profile-page">
    <p v-reveal class="section-kicker">Profile Analysis</p>
    <h1 v-reveal class="section-title">AI 就业<span class="accent">画像</span></h1>
    <p v-reveal class="section-sub">维护你的资料与学习经历，让 AI 生成技术能力评估与竞争力画像。</p>

    <!-- 基本信息 -->
    <section v-reveal class="glass panel">
      <h2 class="panel-title">基本资料</h2>
      <div class="two-col">
        <div class="field">
          <label>姓名 *</label>
          <input v-model="form.name" class="input" placeholder="张三" />
        </div>
        <div class="field">
          <label>学校 *</label>
          <input v-model="form.school" class="input" placeholder="某大学" />
        </div>
        <div class="field">
          <label>专业 *</label>
          <input v-model="form.major" class="input" placeholder="计算机科学与技术" />
        </div>
        <div class="field">
          <label>年级 *</label>
          <input v-model="form.grade" class="input" placeholder="大三" />
        </div>
        <div class="field">
          <label>意向城市</label>
          <input v-model="form.target_city" class="input" placeholder="杭州" />
        </div>
        <div class="field">
          <label>期望薪资</label>
          <input v-model="form.target_salary" class="input" placeholder="15k-20k" />
        </div>
      </div>
      <div class="field">
        <label>自我评价</label>
        <textarea v-model="form.bio" class="textarea" placeholder="一句话介绍你的技术方向与优势"></textarea>
      </div>
      <div class="panel-actions">
        <button class="btn btn-primary" :disabled="savingBasic" @click="saveBasic">
          {{ profile ? "更新资料" : "创建档案" }}
        </button>
        <span v-if="profile" class="hint">当前档案 #{{ profile.id }} — {{ profile.name }}</span>
        <span v-else class="hint">尚未创建档案，创建后才能生成画像</span>
      </div>
    </section>

    <!-- 学习经历 -->
    <section v-reveal class="glass panel">
      <h2 class="panel-title">学习经历</h2>
      <div class="tabs">
        <button
          v-for="t in tabs"
          :key="t.key"
          class="tab"
          :class="{ active: activeTab === t.key }"
          @click="activeTab = t.key"
        >
          {{ t.label }}
        </button>
      </div>

      <!-- 技能 -->
      <div v-show="activeTab === 'skills'" class="tab-body">
        <div v-if="skills.length" class="exp-list">
          <div v-for="(s, i) in skills" :key="i" class="exp-row">
            <span class="exp-main">{{ s.name }}</span>
            <span class="tag cyan">{{ s.proficiency }}</span>
            <span class="exp-desc">{{ s.description }}</span>
            <button class="btn btn-ghost btn-sm" @click="skills.splice(i, 1)">移除</button>
          </div>
        </div>
        <div v-else class="empty">暂无技能，添加几项吧</div>
        <div class="add-row">
          <input v-model="newSkill.name" class="input" placeholder="技能名，如 Java" />
          <select v-model="newSkill.proficiency" class="select">
            <option v-for="p in proficiencies" :key="p" :value="p">{{ p }}</option>
          </select>
          <input v-model="newSkill.description" class="input" placeholder="简述（可选）" />
          <button class="btn" @click="addSkill">添加</button>
        </div>
        <button class="btn btn-primary btn-sm" @click="saveSkills">保存技能（整组替换）</button>
      </div>

      <!-- 项目 -->
      <div v-show="activeTab === 'projects'" class="tab-body">
        <div v-if="projects.length" class="exp-list">
          <div v-for="(p, i) in projects" :key="i" class="exp-row">
            <span class="exp-main">{{ p.name }} <em>/ {{ p.role }}</em></span>
            <span class="exp-desc">{{ p.description }}</span>
            <div class="tag-row">
              <span v-for="t in p.tech_stack" :key="t" class="tag violet">{{ t }}</span>
            </div>
            <button class="btn btn-ghost btn-sm" @click="projects.splice(i, 1)">移除</button>
          </div>
        </div>
        <div v-else class="empty">暂无项目经历</div>
        <div class="add-row">
          <input v-model="newProject.name" class="input" placeholder="项目名" />
          <input v-model="newProject.role" class="input" placeholder="担任角色" />
          <input v-model="newProject.tech" class="input" placeholder="技术栈，逗号分隔" />
        </div>
        <div class="field">
          <label>项目描述</label>
          <textarea v-model="newProject.description" class="textarea" placeholder="负责的模块与成果"></textarea>
        </div>
        <button class="btn" @click="addProject">添加项目</button>
        <button class="btn btn-primary btn-sm" @click="saveProjects">保存项目（整组替换）</button>
      </div>

      <!-- 竞赛 -->
      <div v-show="activeTab === 'competitions'" class="tab-body">
        <div v-if="competitions.length" class="exp-list">
          <div v-for="(c, i) in competitions" :key="i" class="exp-row">
            <span class="exp-main">{{ c.name }}</span>
            <span class="tag amber">{{ c.level }}</span>
            <span class="tag green">{{ c.award }}</span>
            <span class="exp-desc">{{ c.description }}</span>
            <button class="btn btn-ghost btn-sm" @click="competitions.splice(i, 1)">移除</button>
          </div>
        </div>
        <div v-else class="empty">暂无竞赛经历</div>
        <div class="add-row">
          <input v-model="newComp.name" class="input" placeholder="竞赛名，如 蓝桥杯" />
          <input v-model="newComp.level" class="input" placeholder="级别，如 省级" />
          <input v-model="newComp.award" class="input" placeholder="奖项，如 二等奖" />
        </div>
        <div class="field">
          <label>说明</label>
          <textarea v-model="newComp.description" class="textarea" placeholder="组别/方向/收获"></textarea>
        </div>
        <button class="btn" @click="addCompetition">添加竞赛</button>
        <button class="btn btn-primary btn-sm" @click="saveCompetitions">保存竞赛（整组替换）</button>
      </div>

      <!-- 实习 -->
      <div v-show="activeTab === 'internships'" class="tab-body">
        <div v-if="internships.length" class="exp-list">
          <div v-for="(it, i) in internships" :key="i" class="exp-row">
            <span class="exp-main">{{ it.company }} <em>/ {{ it.position }}</em></span>
            <span class="exp-desc">{{ it.description }}</span>
            <div v-if="it.tech_stack" class="tag-row">
              <span v-for="t in it.tech_stack" :key="t" class="tag violet">{{ t }}</span>
            </div>
            <button class="btn btn-ghost btn-sm" @click="internships.splice(i, 1)">移除</button>
          </div>
        </div>
        <div v-else class="empty">暂无实习经历</div>
        <div class="add-row">
          <input v-model="newIntern.company" class="input" placeholder="公司" />
          <input v-model="newIntern.position" class="input" placeholder="岗位" />
          <input v-model="newIntern.tech" class="input" placeholder="技术栈，逗号分隔" />
        </div>
        <div class="field">
          <label>描述</label>
          <textarea v-model="newIntern.description" class="textarea" placeholder="参与的工作与产出"></textarea>
        </div>
        <button class="btn" @click="addInternship">添加实习</button>
        <button class="btn btn-primary btn-sm" @click="saveInternships">保存实习（整组替换）</button>
      </div>
    </section>

    <!-- AI 画像报告 -->
    <section v-reveal class="glass panel">
      <div class="panel-head">
        <h2 class="panel-title">AI 画像报告</h2>
        <button class="btn btn-primary" :disabled="!profile || analyzing" @click="generate">
          {{ analyzing ? "分析中…" : "生成画像" }}
        </button>
      </div>

      <Loading v-if="analyzing" text="AI 正在评估你的竞争力…" />

      <div v-else-if="report" class="report">
        <div class="report-top">
          <div class="score-block">
            <div class="big-number">{{ report.result.comprehensive_score }}</div>
            <div class="score-label">综合竞争力</div>
          </div>
          <div class="report-summary">
            <span class="tag cyan">{{ report.result.technical_direction }}</span>
            <span class="tag violet">{{ report.result.current_level }}</span>
            <span v-if="report.is_mock" class="tag amber">Mock 演示结果</span>
            <p class="summary-text">{{ report.result.profile_summary }}</p>
          </div>
        </div>

        <div class="divider"></div>

        <div class="report-section">
          <h4>能力评估</h4>
          <div class="gauges">
            <div v-for="item in assessmentList" :key="item.key" class="gauge">
              <div class="gauge-head">
                <span>{{ item.label }}</span>
                <b>{{ item.value }}</b>
              </div>
              <div class="gauge-track">
                <div class="gauge-fill" :style="{ width: item.value + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="report-section">
          <h4>核心优势</h4>
          <div class="tag-row">
            <span v-for="a in report.result.core_advantages" :key="a" class="tag green">{{ a }}</span>
          </div>
        </div>

        <div class="report-section">
          <h4>推荐方向</h4>
          <div class="directions">
            <div v-for="d in report.result.recommended_directions" :key="d.job_title" class="direction glass">
              <span>{{ d.job_title }}</span>
              <b>{{ d.match_rate }}%</b>
            </div>
          </div>
        </div>

        <div class="report-section">
          <h4>待提升项</h4>
          <ul class="bullet-list">
            <li v-for="a in report.result.areas_to_improve" :key="a">{{ a }}</li>
          </ul>
        </div>
      </div>

      <div v-else class="empty">点击「生成画像」获取 AI 评估报告</div>
    </section>

    <!-- 历史记录 -->
    <section v-if="history.length" v-reveal class="glass panel">
      <h2 class="panel-title">历史记录</h2>
      <div class="history-list">
        <button
          v-for="h in history"
          :key="h.id"
          class="history-item"
          @click="loadHistoryItem(h.id)"
        >
          <span class="tag cyan">{{ h.target_job || "综合画像" }}</span>
          <span>{{ h.technical_direction }}</span>
          <b>{{ h.comprehensive_score }} 分</b>
          <span class="muted">{{ h.created_at }}</span>
        </button>
      </div>
    </section>

    <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import Loading from "@/components/common/Loading.vue";
import { useUserStore } from "@/store/user";
import { startAnalysis, getAnalysis, getAnalysisHistory } from "@/api/analysis";
import {
  replaceSkills,
  replaceProjects,
  replaceCompetitions,
  replaceInternships,
} from "@/api/user";
import type {
  AnalysisHistoryItem,
  CompetitionItem,
  InternshipItem,
  ProfileAnalysisResponse,
  ProjectItem,
  SkillItem,
  UserCreate,
} from "@/api/types";

const store = useUserStore();
const profile = computed(() => store.profile);
const userId = computed(() => store.currentUserId);

const proficiencies = ["了解", "熟悉", "掌握", "精通"];
const tabs = [
  { key: "skills", label: "技能" },
  { key: "projects", label: "项目" },
  { key: "competitions", label: "竞赛" },
  { key: "internships", label: "实习" },
];
const activeTab = ref("skills");

const form = reactive<UserCreate>({
  name: "",
  school: "",
  major: "",
  grade: "",
  bio: "",
  email: "",
  phone: "",
  target_city: "",
  target_salary: "",
});

const skills = ref<SkillItem[]>([]);
const projects = ref<ProjectItem[]>([]);
const competitions = ref<CompetitionItem[]>([]);
const internships = ref<InternshipItem[]>([]);

const newSkill = reactive({ name: "", proficiency: "熟悉", description: "" });
const newProject = reactive({ name: "", role: "", tech: "", description: "" });
const newComp = reactive({ name: "", level: "", award: "", description: "" });
const newIntern = reactive({ company: "", position: "", tech: "", description: "" });

const savingBasic = ref(false);
const analyzing = ref(false);
const report = ref<ProfileAnalysisResponse | null>(null);
const history = ref<AnalysisHistoryItem[]>([]);
const errorMsg = ref("");

const assessmentList = computed(() => {
  const s = report.value?.result.skill_assessment;
  if (!s) return [];
  return [
    { key: "programming_foundation", label: "编程基础", value: s.programming_foundation },
    { key: "framework_usage", label: "框架使用", value: s.framework_usage },
    { key: "database_skill", label: "数据库", value: s.database_skill },
    { key: "engineering_practice", label: "工程实践", value: s.engineering_practice },
    { key: "project_experience", label: "项目经验", value: s.project_experience },
  ];
});

function splitTech(input: string): string[] {
  return input
    .split(/[,，]/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function populateFromProfile() {
  if (!profile.value) return;
  form.name = profile.value.name;
  form.school = profile.value.school;
  form.major = profile.value.major;
  form.grade = profile.value.grade;
  form.bio = profile.value.bio ?? "";
  form.email = profile.value.email ?? "";
  form.phone = profile.value.phone ?? "";
  form.target_city = profile.value.target_city ?? "";
  form.target_salary = profile.value.target_salary ?? "";
  skills.value = [...profile.value.skills];
  projects.value = [...profile.value.projects];
  competitions.value = [...profile.value.competitions];
  internships.value = [...profile.value.internships];
}

async function saveBasic() {
  errorMsg.value = "";
  if (!form.name || !form.school || !form.major || !form.grade) {
    errorMsg.value = "请填写姓名、学校、专业、年级";
    return;
  }
  savingBasic.value = true;
  try {
    if (profile.value && profile.value.id) {
      await store.updateProfile(profile.value.id, { ...form });
    } else {
      await store.register({ ...form });
    }
    populateFromProfile();
    if (userId.value) loadHistory();
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "保存失败";
  } finally {
    savingBasic.value = false;
  }
}

function addSkill() {
  if (!newSkill.name.trim()) return;
  skills.value.push({ name: newSkill.name.trim(), proficiency: newSkill.proficiency, description: newSkill.description.trim() });
  newSkill.name = "";
  newSkill.description = "";
}
function addProject() {
  if (!newProject.name.trim() || !newProject.role.trim()) return;
  projects.value.push({
    name: newProject.name.trim(),
    role: newProject.role.trim(),
    description: newProject.description.trim(),
    tech_stack: splitTech(newProject.tech),
  });
  newProject.name = "";
  newProject.role = "";
  newProject.tech = "";
  newProject.description = "";
}
function addCompetition() {
  if (!newComp.name.trim()) return;
  competitions.value.push({
    name: newComp.name.trim(),
    level: newComp.level.trim() || "校级",
    award: newComp.award.trim() || "参与奖",
    description: newComp.description.trim(),
  });
  newComp.name = "";
  newComp.level = "";
  newComp.award = "";
  newComp.description = "";
}
function addInternship() {
  if (!newIntern.company.trim() || !newIntern.position.trim()) return;
  internships.value.push({
    company: newIntern.company.trim(),
    position: newIntern.position.trim(),
    description: newIntern.description.trim(),
    tech_stack: splitTech(newIntern.tech),
  });
  newIntern.company = "";
  newIntern.position = "";
  newIntern.tech = "";
  newIntern.description = "";
}

async function guardAndRun(fn: () => Promise<void>) {
  errorMsg.value = "";
  if (!userId.value) {
    errorMsg.value = "请先创建档案";
    return;
  }
  try {
    await fn();
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "操作失败";
  }
}

const saveSkills = () =>
  guardAndRun(async () => {
    await replaceSkills(userId.value!, skills.value);
    await store.fetchProfile(userId.value!);
  });
const saveProjects = () =>
  guardAndRun(async () => {
    await replaceProjects(userId.value!, projects.value);
    await store.fetchProfile(userId.value!);
  });
const saveCompetitions = () =>
  guardAndRun(async () => {
    await replaceCompetitions(userId.value!, competitions.value);
    await store.fetchProfile(userId.value!);
  });
const saveInternships = () =>
  guardAndRun(async () => {
    await replaceInternships(userId.value!, internships.value);
    await store.fetchProfile(userId.value!);
  });

async function generate() {
  errorMsg.value = "";
  if (!userId.value) {
    errorMsg.value = "请先创建档案";
    return;
  }
  analyzing.value = true;
  try {
    const res = await startAnalysis({ user_id: userId.value });
    report.value = res.data;
    loadHistory();
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "生成失败";
  } finally {
    analyzing.value = false;
  }
}

async function loadHistory() {
  if (!userId.value) return;
  try {
    const res = await getAnalysisHistory(userId.value);
    history.value = res.data;
  } catch {
    history.value = [];
  }
}

async function loadHistoryItem(id: number) {
  errorMsg.value = "";
  try {
    const res = await getAnalysis(id);
    report.value = res.data;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载失败";
  }
}

onMounted(async () => {
  if (userId.value) {
    await store.fetchProfile(userId.value);
    populateFromProfile();
    loadHistory();
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
  margin-bottom: 20px;
  letter-spacing: 0.5px;
}
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.panel-head .panel-title {
  margin-bottom: 0;
}
.panel-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 4px;
}
.hint {
  font-size: 13px;
  color: var(--text-2);
}

.tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.tab {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-1);
  cursor: pointer;
  font-size: 13.5px;
  transition: all 0.25s;
}
.tab.active {
  color: var(--text-0);
  border-color: var(--cyan);
  background: rgba(34, 211, 238, 0.1);
  box-shadow: var(--glow-cyan);
}

.tab-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.exp-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.exp-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: rgba(8, 11, 24, 0.4);
}
.exp-main {
  font-weight: 600;
}
.exp-main em {
  font-style: normal;
  color: var(--text-2);
  font-weight: 400;
}
.exp-desc {
  color: var(--text-1);
  font-size: 13px;
  flex: 1 1 100%;
}
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.add-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.add-row .input {
  flex: 1;
  min-width: 140px;
}
.add-row .select {
  flex: 0 0 140px;
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

.gauges {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.gauge-head {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-1);
  margin-bottom: 6px;
}
.gauge-head b {
  color: var(--text-0);
}
.gauge-track {
  height: 8px;
  background: rgba(91, 124, 255, 0.12);
  border-radius: 999px;
  overflow: hidden;
}
.gauge-fill {
  height: 100%;
  background: var(--grad-neon);
  border-radius: 999px;
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.directions {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}
.direction {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
}
.direction b {
  font-family: var(--font-mono);
  color: var(--cyan);
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
<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { MagicStick, Search, Document, Plus } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useProfileStore } from "@/stores/profile";
import { useUserStore } from "@/stores/user";
import { err } from "@/utils/format";
import type { JobBrief, MatchedJob } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";
import StateView from "@/components/common/StateView.vue";

const router = useRouter();
const route = useRoute();
const user = useUserStore();
const profiles = useProfileStore();
const filters = reactive({ keyword: "", category: "" });
const jobs = ref<JobBrief[]>([]);
const matches = ref<MatchedJob[]>([]);
const matchMode = ref(false);
const loading = ref(false);
const matching = ref(false);
const error = ref("");
const total = ref(0);
const onlyMatched = ref(false);
const sort = ref("score");
const page = ref(1);
const categories = ["前端", "后端", "AI", "数据", "测试", "运维", "产品", "安全"];

const visibleJobs = computed<Array<JobBrief | MatchedJob>>(() => {
  if (!matchMode.value) return jobs.value;
  const values = matches.value.filter(job => !onlyMatched.value || job.match_score >= 75);
  return [...values].sort((a, b) => sort.value === "gap" ? a.missing_skills.length - b.missing_skills.length : b.match_score - a.match_score);
});

function isMatched(job: JobBrief | MatchedJob): job is MatchedJob { return "matched_skills" in job; }
function skillsFor(job: JobBrief | MatchedJob) {
  if (isMatched(job)) {
    return [...job.matched_skills.slice(0, 4).map(skill => ({ name: skill, state: "matched" })),
      ...job.missing_skills.slice(0, 4).map(skill => ({ name: skill, state: "missing" }))];
  }
  return (job.required_skills || job.tags).slice(0, 8).map(skill => ({ name: skill, state: "unknown" }));
}

function openJob(jobId: string) {
  router.push({ path: `/jobs/${encodeURIComponent(jobId)}`, query: route.query });
}

function matchScore(job: JobBrief | MatchedJob) {
  return isMatched(job) ? job.match_score : null;
}

function recommendation(job: MatchedJob) {
  if (job.match_score >= 75) return { label: "技能较匹配，核对条件后投递", type: "success" as const };
  if (job.match_score >= 50) return { label: "补强后投递", type: "warning" as const };
  return { label: "先补能力", type: "info" as const };
}

async function load() {
  loading.value = true;
  error.value = "";
  matches.value = [];
  matchMode.value = false;
  try {
    const response = await api.jobs({ ...filters, page: page.value, page_size: 30 });
    jobs.value = response.items;
    total.value = response.total;
  } catch (e) {
    error.value = err(e);
  } finally {
    loading.value = false;
  }
}

async function match() {
  matching.value = true;
  error.value = "";
  try {
    await profiles.load(user.userId!);
    const skills = profiles.profile?.skills.filter(item => item.proficiency !== "未知").map(item => item.name) || [];
    if (!skills.length) { ElMessage.warning("请先填写技能和熟练程度"); return; }
    const response = await api.match({
      skills,
      job_category: filters.category || undefined,
      top_k: 10,
      user_id: user.userId,
    });
    matches.value = response.matches;
    matchMode.value = true;
    filters.keyword = "";
    if (!response.matches.length) ElMessage.info("暂时没有找到匹配岗位，可以先扩大分类或补充技能");
  } catch (e) {
    error.value = err(e);
  } finally {
    matching.value = false;
  }
}
async function addGap(job: MatchedJob) {
  try {
    for (const skill of job.missing_skills.slice(0, 5)) await api.addGrowthTask({ title: `完成 ${skill} 实践并补充成果`, target_job: job.title, resource_query: skill });
    ElMessage.success("技能缺口已加入成长任务");
  } catch (e) { ElMessage.error(err(e)); }
}
function search() { page.value = 1; onlyMatched.value = false; load(); }

function resetMatches() {
  matches.value = [];
  matchMode.value = false;
  onlyMatched.value = false;
}

onMounted(() => {
  if (typeof route.query.keyword === "string") filters.keyword = route.query.keyword;
  if (typeof route.query.category === "string") filters.category = route.query.category;
  load();
});
</script>

<template>
  <div class="jobs-page">
    <PageHeader title="IT 岗位匹配">
      <el-button type="primary" :icon="MagicStick" :loading="matching" :disabled="loading" @click="match">智能匹配</el-button>
    </PageHeader>

    <div class="filter-bar">
      <el-input v-model="filters.keyword" placeholder="搜索岗位名称或技术栈" :prefix-icon="Search" clearable @keyup.enter="search" />
      <el-select v-model="filters.category" placeholder="全部 IT 方向" clearable @change="search">
        <el-option v-for="category in categories" :key="category" :label="category" :value="category" />
      </el-select>
      <el-button type="primary" :disabled="matching" @click="search">搜索</el-button>
      <el-checkbox v-model="onlyMatched" :disabled="!matches.length">仅看匹配度 75% 以上</el-checkbox>
      <el-select v-if="matches.length" v-model="sort"><el-option value="score" label="匹配度优先" /><el-option value="gap" label="缺口最少" /></el-select>
    </div>

    <div v-if="matchMode" class="result-notice">
      <div><b>已按档案技能完成匹配</b><span>技能记录为用户自述，非能力认证；学历、城市等硬条件仍需对照招聘公告确认。</span></div>
      <el-button link type="primary" @click="resetMatches">返回全部岗位</el-button>
    </div>

    <StateView :loading="loading" :error="error" :empty="!visibleJobs.length" empty-text="没有找到相关 IT 岗位" @retry="load">
      <template #content>
        <div class="job-result-caption">共找到 {{ matchMode ? visibleJobs.length : total }} 个岗位</div>
        <div class="job-grid">
          <article v-for="job in visibleJobs" :key="job.job_id" class="job-card" @click="openJob(job.job_id)">
            <header>
              <div>
                <el-tag size="small" effect="plain">{{ job.category || "IT 技术岗位" }}</el-tag>
                <h3>{{ job.title }}</h3>
              </div>
              <div v-if="matchScore(job) !== null" class="job-score">
                <strong>{{ matchScore(job) }}<small>%</small></strong>
                <span>匹配度</span>
              </div>
            </header>
            <p>{{ job.snippet || "暂无岗位摘要，请进入详情查看岗位要求。" }}</p>

            <template v-if="isMatched(job)">
              <div class="job-recommendation">
                <el-tag :type="recommendation(job).type" effect="plain">{{ recommendation(job).label }}</el-tag>
                <span>{{ job.missing_skills.length ? `还差 ${job.missing_skills.length} 项技能证据` : "暂无明显技能缺口" }}</span>
              </div>
              <div class="job-skill-heading">岗位技能要求</div>
              <div class="job-skill-list">
                <el-tag v-for="skill in skillsFor(job)" :key="`${skill.state}-${skill.name}`" size="small" :type="skill.state === 'matched' ? 'success' : skill.state === 'missing' ? 'warning' : 'info'">
                  {{ skill.state === "matched" ? "✓ " : skill.state === "missing" ? "△ " : "" }}{{ skill.name }}
                </el-tag>
              </div>
              <p v-if="job.match_reason" class="job-match-reason">{{ job.match_reason }}</p>
              <el-progress :percentage="job.match_score" :stroke-width="7" :show-text="false" />
            </template>
            <template v-else>
              <div class="job-skill-heading">岗位技术标签</div>
              <div class="job-skill-list">
                <el-tag v-for="skill in skillsFor(job)" :key="skill.name" size="small" type="info">{{ skill.name }}</el-tag>
              </div>
            </template>
            <div v-if="job.preferred_skills?.length" class="job-skill-heading">加分技能</div>
            <div v-if="job.preferred_skills?.length" class="job-skill-list">
              <el-tag v-for="skill in job.preferred_skills" :key="skill" size="small" effect="plain">{{ skill }}</el-tag>
            </div>
            <div class="job-match-reason">
              <template v-if="job.hard_requirements && Object.keys(job.hard_requirements).length">
                <span v-for="(value, key) in job.hard_requirements" :key="key">{{ key }}：{{ value }}（待确认） · </span>
              </template>
              <span v-else>学历、城市、毕业时间等硬条件：待核对招聘原文</span>
            </div>
            <div class="job-actions" @click.stop><el-button text :icon="Document" @click="router.push({ path: '/resume', query: { job_id: job.job_id, target_job: job.title } })">生成岗位简历</el-button><el-button v-if="isMatched(job) && job.missing_skills.length" text :icon="Plus" @click="addGap(job)">加入成长任务</el-button></div>
            <footer>查看岗位详情 <span>→</span></footer>
          </article>
        </div>
        <el-pagination v-if="!matchMode && total > 30" v-model:current-page="page" :page-size="30" :total="total" layout="prev, pager, next" @current-change="load" />
      </template>
    </StateView>
  </div>
</template>

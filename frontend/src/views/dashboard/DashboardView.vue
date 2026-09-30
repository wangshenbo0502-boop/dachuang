<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight, Refresh, Search, TrendCharts } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useUserStore } from "@/stores/user";
import { useProfileStore } from "@/stores/profile";
import type { AnalysisResponse, GrowthResponse, JobBrief } from "@/types/api";
import { err } from "@/utils/format";
import JobCoverageChart from "@/components/charts/JobCoverageChart.vue";

const router = useRouter();
const user = useUserStore();
const profiles = useProfileStore();
const analysis = ref<AnalysisResponse | null>(null);
const growth = ref<GrowthResponse | null>(null);
const jobs = ref<JobBrief[]>([]);
const loading = ref(true);
const errors = ref<string[]>([]);
const profile = computed(() => profiles.profile);
const directions = computed(() => analysis.value?.result.recommended_directions.slice(0, 3) ?? []);
const match = computed(() => directions.value.length ? directions.value[0].match_rate : null);
const categories = ["前端", "后端", "AI", "数据", "测试", "运维", "产品", "安全"];
const coverage = computed(() => categories.map(label => ({
  label,
  count: jobs.value.filter(job => job.category === label).length,
})).filter(item => item.count > 0).sort((a, b) => b.count - a.count));
const hour = new Date().getHours();
const greeting = hour < 11 ? "早上好" : hour < 18 ? "下午好" : "晚上好";
const topics = [
  { title: "AI 岗位与技能", query: "AI岗位技能要求", category: "jobs" },
  { title: "秋招与求职准备", query: "秋招求职准备", category: "market" },
  { title: "毕业生就业政策", query: "高校毕业生就业政策", category: "policies" },
  { title: "技术栈需求", query: "技术栈技能要求", category: "skills" },
];
const suggestions = computed(() => {
  const gaps = growth.value?.result.ability_gaps.slice(0, 2).map(gap => gap.skill) ?? [];
  if (gaps.length) return gaps;
  return analysis.value?.result.areas_to_improve.slice(0, 2) ?? [];
});
const resources = computed(() => growth.value?.result.recommended_resources.slice(0, 3) ?? []);

function openResource(query: string, category?: string) {
  router.push({ path: "/resources", query: { query, ...(category ? { category } : {}) } });
}

async function loadJobs(): Promise<JobBrief[]> {
  const first = await api.jobs({ page: 1, page_size: 50 });
  const pages = Math.ceil(first.total / 50);
  if (pages <= 1) return first.items;
  const remaining = await Promise.all(Array.from({ length: pages - 1 }, (_, index) =>
    api.jobs({ page: index + 2, page_size: 50 })));
  return [first, ...remaining].flatMap(page => page.items);
}

async function load() {
  loading.value = true;
  errors.value = [];
  const [profileResult, analysisResult, growthResult, jobResult] = await Promise.allSettled([
    profiles.load(user.userId!, true), api.analyses(user.userId!),
    api.growths(user.userId!), loadJobs(),
  ]);
  for (const result of [profileResult, analysisResult, growthResult, jobResult]) {
    if (result.status === "rejected") errors.value.push(err(result.reason));
  }
  if (analysisResult.status === "fulfilled") {
    analysis.value = null;
    if (analysisResult.value[0]) {
      try { analysis.value = await api.analysisDetail(analysisResult.value[0].id); }
      catch (e) { errors.value.push(err(e)); }
    }
  }
  if (growthResult.status === "fulfilled") {
    growth.value = null;
    if (growthResult.value[0]) {
      try { growth.value = await api.growthDetail(growthResult.value[0].id); }
      catch (e) { errors.value.push(err(e)); }
    }
  }
  jobs.value = jobResult.status === "fulfilled" ? jobResult.value : [];
  loading.value = false;
}

onMounted(load);
</script>

<template>
  <div class="career-dashboard" v-loading="loading">
    <div class="career-heading">
      <div><span class="career-kicker">我的就业工作台</span><h2>{{ greeting }}，{{ profile?.name || user.user?.name || "同学" }}</h2><p>你的就业准备正在持续进化</p></div>
      <el-tooltip content="刷新首页数据"><el-button :icon="Refresh" circle aria-label="刷新首页数据" @click="load" /></el-tooltip>
    </div>
    <el-alert v-if="errors.length" class="career-alert" type="warning" :closable="false" title="部分数据暂时无法加载" :description="[...new Set(errors)].join('；')" />

    <section class="career-metrics" aria-label="我的数据">
      <button type="button" @click="router.push('/analysis')"><span>就业竞争力</span><strong>{{ analysis?.result.comprehensive_score ?? "—" }}<small v-if="analysis"> / 100</small></strong><em>{{ analysis ? "最近一次就业画像" : "生成就业画像" }} <el-icon><ArrowRight /></el-icon></em></button>
      <button type="button" @click="router.push('/profile')"><span>档案完整度</span><strong>{{ profiles.completeness ?? "—" }}<small v-if="profiles.completeness !== null">%</small></strong><em>查看我的档案 <el-icon><ArrowRight /></el-icon></em></button>
      <button type="button" @click="router.push('/jobs')"><span>推荐方向匹配度</span><strong>{{ match ?? "—" }}<small v-if="match !== null">%</small></strong><em>{{ directions[0]?.job_title || "查看岗位方向" }} <el-icon><ArrowRight /></el-icon></em></button>
    </section>

    <div class="career-section-head"><div><span>市场数据</span><h3>岗位与市场观察</h3></div><small>岗位分布来自本项目知识库，不代表招聘需求增幅</small></div>
    <div class="career-market-grid">
      <section class="career-surface career-chart-section">
        <div class="career-surface-head"><div><h4>岗位方向覆盖</h4><p>知识库收录岗位数量 · 按方向统计</p></div><el-icon><TrendCharts /></el-icon></div>
        <JobCoverageChart v-if="coverage.length" :items="coverage" />
        <div v-else class="career-empty">暂无岗位分布数据。<button type="button" @click="router.push('/jobs')">查看岗位库 <el-icon><ArrowRight /></el-icon></button></div>
      </section>
      <section class="career-surface career-topics-section">
        <div class="career-surface-head"><div><h4>就业与技术动态</h4><p>从知识库探索相关专题</p></div><el-icon><Search /></el-icon></div>
        <button v-for="topic in topics" :key="topic.title" class="career-topic" type="button" @click="openResource(topic.query, topic.category)"><span>{{ topic.title }}</span><el-icon><ArrowRight /></el-icon></button>
      </section>
    </div>

    <div class="career-section-head"><div><span>AI 建议</span><h3>接下来可以做什么</h3></div><button type="button" @click="router.push('/growth')">查看成长规划 <el-icon><ArrowRight /></el-icon></button></div>
    <section class="career-advice">
      <div><span class="career-step">01 / 当前重点</span><h4>{{ suggestions[0] || "完善个人就业档案" }}</h4><p>{{ growth?.result.learning_roadmap[0]?.focus || (analysis ? "查看画像短板，制定下一步学习计划。" : "补充技能和项目经历，生成更贴合你的就业画像。") }}</p></div>
      <div><span class="career-step">02 / 后续行动</span><h4>{{ suggestions[1] || (growth ? "推进阶段学习任务" : "生成就业画像") }}</h4><p>{{ growth?.result.learning_roadmap[0]?.tasks[0] || "结合个人经历和目标岗位，明确下一步准备方向。" }}</p></div>
      <button type="button" class="career-advice-action" @click="router.push(growth || analysis ? '/growth' : '/analysis')">{{ growth ? "继续成长计划" : analysis ? "制定成长计划" : "开始就业分析" }} <el-icon><ArrowRight /></el-icon></button>
    </section>

    <div class="career-section-head"><div><span>我的数据</span><h3>为你推荐的岗位方向</h3></div><button type="button" @click="router.push('/jobs')">查看岗位 <el-icon><ArrowRight /></el-icon></button></div>
    <div v-if="directions.length" class="career-directions"><button v-for="(direction, index) in directions" :key="direction.job_title" type="button" @click="router.push({ path: '/jobs', query: { keyword: direction.job_title } })"><span>0{{ index + 1 }} / 推荐方向</span><h4>{{ direction.job_title }}</h4><div><strong>{{ direction.match_rate }}%</strong><small>画像匹配度</small></div><el-progress :percentage="direction.match_rate" :show-text="false" :stroke-width="5" /></button></div>
    <div v-else class="career-inline-empty">生成就业画像后，这里会显示与你的能力更匹配的方向。<button type="button" @click="router.push('/analysis')">生成画像 <el-icon><ArrowRight /></el-icon></button></div>

    <div class="career-section-head"><div><span>就业资源</span><h3>推荐学习资源</h3></div><button type="button" @click="router.push('/resources')">浏览资源库 <el-icon><ArrowRight /></el-icon></button></div>
    <div v-if="resources.length" class="career-resources"><button v-for="(resource, index) in resources" :key="index" type="button" @click="openResource(resource)"><span>{{ String(index + 1).padStart(2, '0') }}</span><strong>{{ resource }}</strong><el-icon><ArrowRight /></el-icon></button></div>
    <div v-else class="career-inline-empty">完成成长规划后，这里会展示适合你的学习资源。<button type="button" @click="router.push('/growth')">查看成长规划 <el-icon><ArrowRight /></el-icon></button></div>
  </div>
</template>

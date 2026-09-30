<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight, Refresh, Search, Document, MagicStick, Reading, Aim, TopRight } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useUserStore } from "@/stores/user";
import { useProfileStore } from "@/stores/profile";
import type { AnalysisResponse, GrowthResponse, JobBrief, KnowledgeResult } from "@/types/api";
import { resourceDate, resourceTitle, resourceUrl } from "@/utils/resources";
import { err } from "@/utils/format";
import JobDirectionMap from "@/components/charts/JobDirectionMap.vue";

const router = useRouter();
const user = useUserStore();
const profiles = useProfileStore();
const analysis = ref<AnalysisResponse | null>(null);
const growth = ref<GrowthResponse | null>(null);
const jobs = ref<JobBrief[]>([]);
const loading = ref(false);
const errors = ref<string[]>([]);
const jobsError = ref("");
const news = ref<KnowledgeResult[]>([]);
const newsError = ref("");
const newsLoading = ref(false);
const fetchedAt = ref("");
const selectedCategory = ref("");
const selectedSkill = ref("");
const keyword = ref("");
const profile = computed(() => profiles.profile);
const directions = computed(() => analysis.value?.result.recommended_directions.slice(0, 3) ?? []);
const categories = computed(() => [...new Set(jobs.value.map(job => job.category || "其他"))]);
const selectedJobs = computed(() => selectedCategory.value
  ? jobs.value.filter(job => (job.category || "其他") === selectedCategory.value) : jobs.value);
const coverage = computed(() => categories.value.map(label => ({
  label, count: jobs.value.filter(job => (job.category || "其他") === label).length,
})).sort((a, b) => b.count - a.count));
const skillStats = computed(() => {
  const counts = new Map<string, { name: string; count: number }>();
  for (const job of selectedJobs.value) {
    // Count a skill once per job, including repeated entries with different casing.
    const seen = new Set<string>();
    for (const value of job.required_skills || []) {
      const name = value.trim();
      const key = name.toLocaleLowerCase();
      if (!key || seen.has(key)) continue;
      seen.add(key);
      const item = counts.get(key) || { name, count: 0 };
      item.count++;
      counts.set(key, item);
    }
  }
  return [...counts.values()].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
});
const skillSampleCount = computed(() => selectedJobs.value.filter(job => job.required_skills?.some(skill => skill.trim())).length);
const totalSkillSamples = computed(() => jobs.value.filter(job => job.required_skills?.some(skill => skill.trim())).length);
const activeSkill = computed(() => skillStats.value.find(skill => skill.name === selectedSkill.value) || skillStats.value[0]);
const evidenceJobs = computed(() => activeSkill.value
  ? selectedJobs.value.filter(job => job.required_skills?.some(skill => skill.trim().toLocaleLowerCase() === activeSkill.value!.name.toLocaleLowerCase()))
  : selectedJobs.value);
const companionSkills = computed(() => {
  const counts = new Map<string, { name: string; count: number }>();
  for (const job of evidenceJobs.value) {
    const seen = new Set<string>();
    for (const value of job.required_skills || []) {
      const name = value.trim();
      const key = name.toLocaleLowerCase();
      if (!key || seen.has(key) || key === activeSkill.value?.name.toLocaleLowerCase()) continue;
      seen.add(key);
      const item = counts.get(key) || { name, count: 0 };
      item.count++;
      counts.set(key, item);
    }
  }
  return [...counts.values()].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name)).slice(0, 3);
});
const leadingDirection = computed(() => coverage.value[0]);
watch(selectedCategory, () => { selectedSkill.value = ""; });
const hour = new Date().getHours();
const greeting = hour < 11 ? "早上好" : hour < 18 ? "下午好" : "晚上好";
const dateLabel = new Date().toLocaleDateString("zh-CN", { month: "long", day: "numeric", weekday: "long" });
const newsDate = computed(() => {
  const date = new Date(fetchedAt.value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleString("zh-CN", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" });
});
const nextActions = computed(() => [
  {
    icon: Aim, label: "方向定位",
    title: directions.value[0]?.job_title || "找到适合你的技术方向",
    description: directions.value.length
      ? `最近画像匹配度 ${directions.value[0].match_rate}%。${analysis.value?.result.profile_summary || "结合岗位要求，进一步确认求职方向。"}`
      : "补充技术栈与项目经历，生成就业画像，对照岗位要求确认求职方向。",
    action: analysis.value ? "查看就业画像" : "开始就业分析", path: "/analysis",
  },
  {
    icon: Reading, label: "能力进阶",
    title: growth.value?.result.ability_gaps[0]?.skill
      ? `重点补强 ${growth.value.result.ability_gaps[0].skill}` : "把学习变成可展示的成果",
    description: growth.value?.result.learning_roadmap[0]?.tasks[0]
      || analysis.value?.result.areas_to_improve[0]
      || "围绕目标岗位制定学习任务，积累项目、面试练习和实践记录。",
    action: growth.value ? "继续成长任务" : "制定成长计划", path: "/growth",
  },
  {
    icon: Document, label: "求职准备",
    title: growth.value?.result.recommended_resources[0] || "让简历回应岗位要求",
    description: growth.value?.result.recommended_resources.length
      ? "结合成长规划中的学习资源，补齐技术证据，再把真实成果更新到简历。"
      : "用真实的项目贡献与技术实践组织简历内容，再针对目标岗位调整重点。",
    action: growth.value?.result.recommended_resources.length ? "查看相关资源" : "打磨我的简历",
    path: growth.value?.result.recommended_resources.length ? "/resources" : "/resume",
    query: growth.value?.result.recommended_resources[0],
  },
]);

function openJobs(value = keyword.value) {
  router.push({ path: "/jobs", query: { ...(value.trim() ? { keyword: value.trim() } : {}), ...(selectedCategory.value ? { category: selectedCategory.value } : {}) } });
}
function openResource(query: string) {
  router.push({ path: "/resources", query: { query } });
}
async function loadNews() {
  newsLoading.value = true;
  newsError.value = "";
  news.value = [];
  fetchedAt.value = "";
  try {
    const response = await api.resourceHome();
    news.value = response.items.slice(0, 3);
    fetchedAt.value = response.fetched_at;
    if (response.unavailable_sources.length) newsError.value = "部分资讯源暂不可用，以下为已获取的内容。";
    if (!news.value.length) newsError.value = "近期资讯暂不可用，仍可搜索技术资源。";
  } catch (e) { newsError.value = err(e); }
  finally { newsLoading.value = false; }
}
async function loadJobs(): Promise<JobBrief[]> {
  const first = await api.jobs({ page: 1, page_size: 50 });
  const pages = Math.ceil(first.total / 50);
  const remaining = await Promise.all(Array.from({ length: Math.max(0, pages - 1) }, (_, index) =>
    api.jobs({ page: index + 2, page_size: 50 })));
  return [...new Map([first, ...remaining].flatMap(page => page.items).map(job => [job.job_id, job])).values()];
}
async function load() {
  if (loading.value) return;
  loading.value = true;
  errors.value = [];
  jobsError.value = "";
  const newsRequest = loadNews();
  try {
    const [profileResult, analysisResult, growthResult, jobResult] = await Promise.allSettled([
      profiles.load(user.userId!, true), api.analyses(user.userId!),
      api.growths(user.userId!), loadJobs(),
    ]);
    for (const result of [profileResult, analysisResult, growthResult]) {
      if (result.status === "rejected") errors.value.push(err(result.reason));
    }
    analysis.value = null;
    growth.value = null;
    if (analysisResult.status === "fulfilled" && analysisResult.value[0]) {
      try { analysis.value = await api.analysisDetail(analysisResult.value[0].id); }
      catch (e) { errors.value.push(err(e)); }
    }
    if (growthResult.status === "fulfilled" && growthResult.value[0]) {
      try { growth.value = await api.growthDetail(growthResult.value[0].id); }
      catch (e) { errors.value.push(err(e)); }
    }
    jobs.value = jobResult.status === "fulfilled" ? jobResult.value : [];
    if (jobResult.status === "rejected") jobsError.value = err(jobResult.reason);
    if (!categories.value.includes(selectedCategory.value)) selectedCategory.value = "";
  } finally {
    await newsRequest;
    loading.value = false;
  }
}
onMounted(load);
</script>

<template>
  <div class="it-home" :aria-busy="loading">
    <section class="personal-overview" aria-label="个人求职概览">
      <div class="career-heading">
        <p>{{ greeting }}，{{ profile?.name || user.user?.name || "求职者" }}<span>今天也离理想岗位近一步。</span></p>
        <div class="heading-tools"><time>{{ dateLabel }}</time><el-tooltip content="刷新首页数据"><el-button :icon="Refresh" :loading="loading" circle aria-label="刷新首页数据" @click="load" /></el-tooltip></div>
      </div>
      <div class="personal-banner">
        <img class="circuit-image" src="/images/circuit-board.jpg" alt="" fetchpriority="high" />
        <div class="banner-copy">
          <span class="eyebrow">BUILD YOUR NEXT CHAPTER</span>
          <h2>IT 求职工作台<span>看见行业，找到你的下一站。</span></h2>
          <div class="banner-actions">
            <el-button class="resume-button" :icon="Document" @click="router.push('/resume')">我的简历</el-button>
            <button class="banner-link" @click="router.push('/profile')">完善个人档案 <el-icon><ArrowRight /></el-icon></button>
          </div>
        </div>
        <span class="banner-index">CAREER / TECH / FUTURE</span>
      </div>
      <div class="personal-status">
        <button @click="router.push('/profile')"><span>档案完整度</span><strong>{{ profiles.completeness ?? "—" }}<small v-if="profiles.completeness !== null">%</small></strong><i class="completion-track"><i :style="{ width: `${profiles.completeness || 0}%` }" /></i></button>
        <button @click="router.push('/profile')"><span>我的技术积累</span><strong>{{ profile?.skills.length ?? "—" }}<small>项技能</small><b>/</b>{{ profile?.projects.length ?? "—" }}<small>个项目</small></strong></button>
        <button @click="router.push(analysis ? '/analysis' : '/profile')"><span>{{ analysis ? "当前求职方向" : "意向城市" }}</span><strong class="status-direction" :title="analysis?.result.technical_direction || profile?.target_city">{{ analysis?.result.technical_direction || profile?.target_city || "待完善" }}</strong></button>
        <button class="status-action" @click="router.push('/applications')"><span>我的投递</span><strong>查看求职进展 <el-icon><ArrowRight /></el-icon></strong></button>
      </div>
      <el-alert v-if="errors.length" type="warning" :closable="false" title="部分个人数据暂时无法加载" :description="[...new Set(errors)].join('；')" />
    </section>

    <section class="industry-section" aria-labelledby="industry-heading">
      <header class="section-heading">
        <div><span class="eyebrow">INDUSTRY INTELLIGENCE</span><h2 id="industry-heading">IT 行业观察<span class="section-tag">岗位与技术</span></h2></div>
        <form class="industry-search" role="search" @submit.prevent="openJobs()">
          <el-icon><Search /></el-icon><input v-model="keyword" aria-label="搜索岗位或技能" placeholder="搜索岗位、技术或技能" type="search" maxlength="100" />
          <button type="submit" aria-label="搜索岗位"><el-icon><ArrowRight /></el-icon></button>
        </form>
      </header>
      <div class="industry-summary">
        <div><span>收录岗位样本</span><strong>{{ loading && !jobs.length ? "—" : jobsError ? "—" : jobs.length }}<small>个</small></strong></div>
        <div><span>覆盖技术方向</span><strong>{{ jobsError ? "—" : categories.length }}<small>类</small></strong></div>
        <div><span>{{ selectedCategory || "全部方向" }}必需技能</span><strong>{{ jobsError ? "—" : skillStats.length }}<small>项</small></strong></div>
        <div><span>已标注必需技能</span><strong>{{ jobsError ? "—" : totalSkillSamples }}<small>/ {{ jobs.length }} 个样本</small></strong></div>
        <p>统计范围：当前岗位知识库<br />非全网招聘规模或实时热度</p>
      </div>
      <div v-if="jobsError" class="section-empty" role="status"><p>岗位统计暂时无法加载：{{ jobsError }}</p><el-button :icon="Refresh" :loading="loading" @click="load">重新加载</el-button></div>
      <div v-else class="market-analysis" v-loading="loading && !jobs.length">
        <div class="distribution">
          <div class="subheading"><div><span class="chart-eyebrow">01 / TECH LANDSCAPE</span><h3>IT 岗位版图</h3></div><button v-if="coverage.length" class="map-reset" :class="{ active: !selectedCategory }" :aria-pressed="!selectedCategory" @click="selectedCategory = ''">全部方向</button></div>
          <p v-if="leadingDirection" class="map-insight"><strong>{{ leadingDirection.label }}</strong> 收录最多<span>{{ leadingDirection.count }} 个样本 · 占比 {{ Math.round(leadingDirection.count / jobs.length * 100) }}%</span></p>
          <JobDirectionMap v-if="coverage.length" :items="coverage" :selected="selectedCategory" @select="selectedCategory = $event" />
          <div v-else class="section-empty"><p>{{ loading ? "正在获取岗位样本…" : "暂无岗位样本" }}</p><router-link v-if="!loading" to="/jobs">浏览岗位库 <el-icon><ArrowRight /></el-icon></router-link></div>
        </div>
        <div class="skill-demand">
          <div class="subheading"><div><span class="chart-eyebrow">02 / SKILL SIGNALS</span><h3>{{ selectedCategory || "跨方向" }}高频技能</h3></div><button class="text-link" @click="openJobs('')">查看岗位 <el-icon><TopRight /></el-icon></button></div>
          <div v-if="activeSkill" class="skill-insight" aria-live="polite">
            <div><strong>{{ activeSkill.name }}</strong><span>{{ activeSkill.count }} / {{ selectedJobs.length }} 个样本要求这项技能</span></div>
            <b>{{ Math.round(activeSkill.count / selectedJobs.length * 100) }}<small>%</small></b>
          </div>
          <div v-if="skillStats.length" class="skill-grid" role="group" aria-label="查看技能证据">
            <button v-for="(skill, index) in skillStats.slice(0, 6)" :key="skill.name" class="skill-tile" :class="{ active: activeSkill?.name === skill.name }" :aria-pressed="activeSkill?.name === skill.name" :aria-label="`分析 ${skill.name} 技能要求`" @click="selectedSkill = skill.name">
              <span class="tile-rank">{{ String(index + 1).padStart(2, '0') }}</span><strong :title="skill.name">{{ skill.name }}</strong>
              <span class="tile-coverage"><span>{{ skill.count }} 个岗位</span><b>{{ Math.round(skill.count / selectedJobs.length * 100) }}<small>%</small></b></span>
              <span class="tile-dots" aria-hidden="true"><i v-for="dot in 10" :key="dot" :class="{ filled: dot <= Math.round(skill.count / selectedJobs.length * 10) }" /></span>
            </button>
          </div>
          <div v-else class="section-empty"><p>{{ loading ? "正在统计技能要求…" : "该方向暂无明确标注的必需技能" }}</p></div>
          <div v-if="activeSkill" class="skill-pairing"><span>常与它一起出现</span><div v-if="companionSkills.length"><span v-for="skill in companionSkills" :key="skill.name" :title="`${skill.count} 个岗位同时要求 ${activeSkill.name} 和 ${skill.name}`">{{ skill.name }}<small>{{ skill.count }}</small></span></div><p v-else>暂无共同要求的技能记录</p></div>
          <p class="data-note">{{ selectedCategory || "全部方向" }}共 {{ selectedJobs.length }} 个岗位样本，{{ skillSampleCount }} 个已标注必需技能；比例按该方向全部样本计算。</p>
        </div>
      </div>
      <div v-if="!jobsError && evidenceJobs.length" class="job-evidence">
        <div class="evidence-intro"><span class="chart-eyebrow">FROM SKILLS TO ROLES</span><h3>{{ activeSkill ? `哪些岗位要求 ${activeSkill.name}？` : `${selectedCategory || '全部方向'}岗位样本` }}</h3><button class="text-link" @click="openJobs(activeSkill?.name || '')">查看 {{ evidenceJobs.length }} 个相关岗位 <el-icon><ArrowRight /></el-icon></button></div>
        <router-link v-for="job in evidenceJobs.slice(0, 2)" :key="job.job_id" class="evidence-job" :to="`/jobs/${encodeURIComponent(job.job_id)}`">
          <span>{{ job.category || "其他" }}<el-icon><TopRight /></el-icon></span>
          <h4 :title="job.title">{{ job.title }}</h4>
          <div><span v-for="skill in [...new Set(job.required_skills || [])].slice(0, 4)" :key="skill" :class="{ highlighted: skill.trim().toLocaleLowerCase() === activeSkill?.name.toLocaleLowerCase() }">{{ skill }}</span><span v-if="!job.required_skills?.length">技能要求待补充</span></div>
        </router-link>
      </div>

      <div class="news-heading subheading"><div><h3>近期技术动态</h3><span>{{ newsDate ? `资讯获取于 ${newsDate}` : "技术生态与官方资讯" }}</span></div><router-link class="text-link" to="/resources">全部资讯 <el-icon><ArrowRight /></el-icon></router-link></div>
      <p v-if="newsError" class="news-notice" role="status">{{ newsError }} <button v-if="!newsLoading" class="text-link" @click="loadNews">重试</button></p>
      <div class="industry-news" v-loading="newsLoading">
        <article v-for="(item, index) in news" :key="item.doc_id || resourceTitle(item)" class="news-item">
          <div class="news-meta"><span>{{ item.source || "技术资讯" }}</span><span>{{ String(index + 1).padStart(2, '0') }}</span></div>
          <h4><a v-if="resourceUrl(item)" :href="resourceUrl(item)" target="_blank" rel="noopener noreferrer">{{ resourceTitle(item) }} <el-icon><TopRight /></el-icon></a><button v-else @click="openResource(resourceTitle(item))">{{ resourceTitle(item) }}</button></h4>
          <p>{{ item.content }}</p>
          <footer><time>{{ resourceDate(item) }}</time><button class="text-link" @click="openResource(resourceTitle(item))">相关解读 <el-icon><ArrowRight /></el-icon></button></footer>
        </article>
        <div v-if="!news.length" class="news-empty"><el-icon><Reading /></el-icon><p>{{ newsLoading ? "正在获取技术资讯…" : "暂时没有可展示的资讯" }}</p><router-link to="/resources">搜索技术资源 <el-icon><ArrowRight /></el-icon></router-link></div>
      </div>
    </section>

    <section class="ai-section" aria-labelledby="ai-heading">
      <header class="section-heading">
        <div><span class="eyebrow">YOUR NEXT MOVE</span><h2 id="ai-heading"><el-icon><MagicStick /></el-icon>你的下一步</h2></div>
        <span class="ai-source">{{ analysis || growth ? (analysis?.is_mock || growth?.is_mock ? "示例模式 · 建议仅供参考" : "基于最近的就业画像与成长记录") : "完成就业分析后，获取个性化 AI 建议" }}</span>
      </header>
      <div class="ai-actions">
        <article v-for="(action, index) in nextActions" :key="action.label">
          <div class="action-eyebrow"><el-icon><component :is="action.icon" /></el-icon><span>{{ action.label }}</span><small>0{{ index + 1 }}</small></div>
          <h3 :title="action.title">{{ action.title }}</h3><p :title="action.description">{{ action.description }}</p>
          <button class="text-link" @click="router.push({ path: action.path, query: action.query ? { query: action.query } : {} })">{{ action.action }} <el-icon><ArrowRight /></el-icon></button>
        </article>
      </div>
    </section>
    <footer class="home-footer"><span>IT CAREER WORKSPACE</span><span>从了解行业，到成为行业的一员。</span></footer>
  </div>
</template>

<style scoped lang="scss" src="./dashboard.scss" />

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Plus, Search } from "@element-plus/icons-vue";
import { api } from "@/api";
import { err } from "@/utils/format";
import type { MarketContext } from "@/types/api";
const props = defineProps<{ target: string }>();
const router = useRouter();
const data = ref<MarketContext | null>(null);
const loading = ref(false);
const error = ref("");
let requestId = 0;
async function load() {
  const id = ++requestId;
  loading.value = true; error.value = "";
  try { const result = await api.marketContext(props.target); if (id === requestId) data.value = result; }
  catch (e) { if (id === requestId) error.value = err(e); }
  finally { if (id === requestId) loading.value = false; }
}
async function addTask(skill: string, title: string) {
  try { await api.addGrowthTask({ title, target_job: props.target, resource_query: skill }); ElMessage.success("已加入成长任务"); }
  catch (e) { ElMessage.error(err(e)); }
}
watch(() => props.target, load, { immediate: true });
</script>
<template>
  <section class="market-context" v-loading="loading">
    <div class="career-section-head"><div><span>岗位事实与档案对照</span><h3>企业需要什么样的人</h3></div><el-button :icon="Search" @click="router.push({ path: '/jobs', query: { keyword: target } })">查看岗位</el-button></div>
    <el-alert v-if="error" :title="error" type="warning" :closable="false"><el-button text @click="load">重试</el-button></el-alert>
    <template v-else-if="data">
      <p class="muted">{{ data.scope }} 样本 {{ data.sample_count }} 个。</p>
      <el-empty v-if="!data.skills.length" description="暂无该方向的结构化岗位要求" />
      <div v-else class="skill-matrix">
        <article v-for="row in data.skills" :key="row.skill">
          <div><h4>{{ row.skill }}</h4><small>{{ row.count }} / {{ data.sample_count }} 个样本提及</small><el-progress :percentage="row.coverage" :stroke-width="5" /></div>
          <div><el-tag :type="row.evidence.length ? 'success' : 'warning'">{{ row.status }}</el-tag><p>{{ row.evidence.join("；") || "档案中暂无对应技能或项目记录" }}</p><small>来源：<button v-for="source in row.sources.slice(0, 2)" :key="source.job_id" class="text-link" @click="router.push(`/jobs/${encodeURIComponent(source.job_id)}`)">{{ source.title }}</button></small></div>
          <el-button text :icon="Plus" @click="addTask(row.skill, row.action)">加入成长任务</el-button>
        </article>
      </div>
      <div class="market-job-samples"><article v-for="job in data.jobs.slice(0, 3)" :key="job.job_id"><h4>{{ job.title }}</h4><p>{{ job.snippet }}</p><small>{{ job.source || "岗位知识库" }} · {{ job.published_at || "未标注发布日期" }}</small><p v-if="Object.keys(job.hard_requirements || {}).length">硬条件：{{ Object.entries(job.hard_requirements || {}).map(([key, value]) => `${key}: ${value}`).join("；") }}</p><p v-else class="muted">学历、城市等硬条件待招聘方确认</p></article></div>
    </template>
  </section>
</template>

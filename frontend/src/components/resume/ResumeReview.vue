<script setup lang="ts">
import { computed, ref, watch } from "vue";
type ProjectReview = { project_name: string; original: string; optimized: string; source_experience_id?: number; fact_warnings?: string[]; review_status?: string; accepted?: boolean };
const props = defineProps<{ suggestion: Record<string, unknown>; saving: boolean }>();
const emit = defineEmits<{ accept: [value: Record<string, unknown>]; cancel: [] }>();
const summary = ref("");
const confirmSummary = ref(false);
const projects = ref<ProjectReview[]>([]);
const confirmed = computed(() => projects.value.some(item => item.accepted) || confirmSummary.value);
watch(() => props.suggestion, value => {
  summary.value = String(value.personal_summary || "");
  projects.value = (Array.isArray(value.optimized_projects) ? value.optimized_projects : []).map(item => ({ ...item, accepted: false }));
  confirmSummary.value = false;
}, { immediate: true });
function accept() {
  emit("accept", {
    ...props.suggestion,
    personal_summary: confirmSummary.value ? summary.value : "",
    summary_confirmed: confirmSummary.value,
    optimized_projects: projects.value.filter(item => item.accepted).map(({ accepted, ...item }) => ({ ...item, review_status: "confirmed" })),
    optimized_skills: [],
  });
}
</script>
<template>
  <section class="resume-review">
    <h3>AI 改写审核</h3><p class="muted">模型评分 {{ suggestion.resume_score ?? "-" }} / 100 · 表达建议，非事实认证</p>
    <el-form label-position="top"><el-form-item label="个人简介"><el-input v-model="summary" type="textarea" :rows="3" @input="confirmSummary = false" /><el-checkbox v-model="confirmSummary" :disabled="!summary.trim()">已核对简介中的全部事实</el-checkbox></el-form-item></el-form>
    <article v-for="(item, index) in projects" :key="index" class="review-row">
      <h4>{{ item.project_name }}</h4><small>档案项目 {{ item.source_experience_id ? `#${item.source_experience_id}` : "（原始输入）" }}</small>
      <div class="review-columns"><div><b>原文</b><p>{{ item.original || "尚未填写项目说明" }}</p></div><div><b>改写草稿</b><el-input v-model="item.optimized" type="textarea" :rows="5" @input="item.accepted = false" /></div></div>
      <p v-for="warning in item.fact_warnings || []" :key="warning" class="fact-warning">{{ warning }}</p>
      <el-checkbox v-model="item.accepted">已核对职责、技术和结果，采纳此项</el-checkbox>
    </article>
    <ul><li v-for="tip in (suggestion.overall_suggestions as string[] || [])" :key="tip">{{ tip }}</li></ul>
    <div class="resource-actions"><el-button @click="emit('cancel')">放弃草稿</el-button><el-button type="primary" :disabled="!confirmed" :loading="saving" @click="accept">写入已确认内容</el-button></div>
  </section>
</template>

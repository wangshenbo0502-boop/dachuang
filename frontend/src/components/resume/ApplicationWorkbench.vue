<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Check, Promotion, Refresh } from "@element-plus/icons-vue";
import { api } from "@/api";
import { err } from "@/utils/format";
import type { JobBrief, JobDetail, JobApplication, ResumeVersion } from "@/types/api";
const props = defineProps<{ version: ResumeVersion }>();
const emit = defineEmits<{ job: [id: string] }>();
const route = useRoute();
const router = useRouter();
const jobs = ref<JobBrief[]>([]);
const jobId = ref("");
const job = ref<JobDetail | null>(null);
const bossUrl = ref("");
const greeting = ref("");
const application = ref<JobApplication | null>(null);
const loading = ref(false);
const saving = ref(false);
const error = ref("");
const status = ref("");
let sequence = 0;
const skills = computed(() => props.version.profile.skills.filter(item => props.version.selected_skills.includes(item.id!)).map(item => item.name));
const requirements = computed(() => job.value?.required_skills?.length ? job.value.required_skills : job.value?.tags || []);
const missing = computed(() => requirements.value.filter(skill => !skills.value.some(value => value.toLowerCase() === skill.toLowerCase())));
async function chooseJob() {
  const id = ++sequence;
  application.value = null; status.value = ""; job.value = null; error.value = ""; bossUrl.value = ""; emit("job", jobId.value);
  if (!jobId.value) return;
  loading.value = true;
  try {
    const detail = await api.job(jobId.value);
    if (id !== sequence) return;
    job.value = detail;
    greeting.value = `您好，我是${props.version.profile.name}，关注贵司的${detail.title}岗位。${skills.value.length ? `我的简历包含${skills.value.slice(0, 4).join("、")}相关记录。` : ""}希望有机会进一步交流，谢谢。`;
  } catch (e) { if (id === sequence) error.value = err(e); }
  finally { if (id === sequence) loading.value = false; }
}
async function loadJobs() {
  loading.value = true;
  try {
    const first = await api.jobs({ page: 1, page_size: 50 });
    let all = first.items;
    for (let page = 2; page <= Math.ceil(first.total / 50); page++) all = all.concat((await api.jobs({ page, page_size: 50 })).items);
    jobs.value = all;
    const requested = typeof route.query.job_id === "string" ? route.query.job_id : "";
    jobId.value = all.find(item => item.job_id === requested && item.title === props.version.target_job)?.job_id || all.find(item => item.title === props.version.target_job)?.job_id || "";
    await chooseJob();
  } catch (e) { error.value = err(e); }
  finally { loading.value = false; }
}
function validUrl() {
  try { const url = new URL(bossUrl.value); return url.protocol === "https:" && (url.hostname === "zhipin.com" || url.hostname.endsWith(".zhipin.com")) && !!url.pathname.replaceAll("/", "") && (!url.port || url.port === "443") && !url.username && !url.password; }
  catch { return false; }
}
async function prepare(prefill = false) {
  if (!job.value) return ElMessage.warning("请选择目标岗位");
  if (!validUrl()) return ElMessage.warning("请填写 HTTPS 的 BOSS 直聘具体岗位链接");
  saving.value = true; error.value = "";
  try {
    if (!application.value) application.value = await api.createApplication({ job_id: job.value.job_id, job_title: job.value.title, boss_url: bossUrl.value, greeting: greeting.value, resume_version_id: props.version.id });
    if (!["prepared", "opened"].includes(application.value.status)) {
      status.value = "该岗位已有投递结果，请到投递记录继续跟进";
      return;
    }
    if (prefill) {
      const response = await api.startApplicationAutomation(application.value.id);
      status.value = response.message;
    } else status.value = "投递材料已保存，尚未发送";
  } catch (e) { error.value = err(e); }
  finally { saving.value = false; }
}
async function confirm() {
  if (!application.value) return;
  saving.value = true;
  try { application.value = await api.updateApplication(application.value.id, { status: "applied" }); status.value = "已记录为用户确认投递"; }
  catch (e) { error.value = err(e); }
  finally { saving.value = false; }
}
watch(() => props.version.id, () => { application.value = null; status.value = ""; loadJobs(); }, { immediate: true });
</script>
<template>
  <section class="application-workbench" v-loading="loading">
    <div class="career-section-head"><div><span>当前简历 · {{ version.name }}</span><h3>投递工作台</h3></div><el-button text @click="router.push('/applications')">投递记录</el-button></div>
    <el-alert v-if="error" :title="error" type="warning" :closable="false" />
    <el-form label-position="top" class="form-grid">
      <el-form-item label="目标岗位"><el-select v-model="jobId" filterable :disabled="saving" placeholder="选择 IT 岗位" @change="chooseJob"><el-option v-for="item in jobs" :key="item.job_id" :value="item.job_id" :label="item.title" /></el-select></el-form-item>
      <el-form-item label="BOSS 直聘岗位链接"><el-input v-model="bossUrl" :disabled="!!application || saving" placeholder="https://www.zhipin.com/job_detail/..." /></el-form-item>
      <div v-if="job" class="full"><div class="tag-row"><el-tag v-for="skill in requirements" :key="skill" :type="missing.includes(skill) ? 'warning' : 'success'">{{ skill }}</el-tag></div><p class="muted">关键词覆盖：{{ requirements.length - missing.length }} / {{ requirements.length }}。仅按当前简历技能名称对照，硬条件与实际熟练程度待确认。</p></div>
      <el-form-item label="开场白（可编辑）" class="full"><el-input v-model="greeting" type="textarea" :rows="3" maxlength="2000" :disabled="!!application || saving" /></el-form-item>
    </el-form>
    <p class="muted">预填不会自动发送或上传简历。请在招聘页面核对材料并确认最终提交；登录、验证码由你接管。</p>
    <div class="resource-actions"><el-button :loading="saving" :disabled="!job || !!application" @click="prepare(false)">保存投递材料</el-button><el-button type="primary" :icon="Promotion" :loading="saving" :disabled="!job || application?.status === 'applied'" @click="prepare(true)">打开页面并预填</el-button><el-button v-if="application && application.status !== 'applied'" :icon="Check" :loading="saving" @click="confirm">我已在招聘页面发送</el-button><el-button v-if="!jobs.length" :icon="Refresh" @click="loadJobs">重新加载岗位</el-button></div>
    <el-alert v-if="status" :title="status" type="info" :closable="false" />
  </section>
</template>

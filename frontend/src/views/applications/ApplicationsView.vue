<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { Check, CopyDocument, Link, Promotion, Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { api } from "@/api";
import { err, fmt } from "@/utils/format";
import type { ApplicationStatus, JobApplication } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";
import StateView from "@/components/common/StateView.vue";

const applications = ref<JobApplication[]>([]);
const router = useRouter();
const loading = ref(true);
const error = ref("");
const query = ref("");
const activeStatus = ref<"all" | ApplicationStatus>("all");
const feedbackOpen = ref(false);
const editing = ref<JobApplication | null>(null);
const saving = ref(false);
const feedback = reactive({ status: "applied" as ApplicationStatus, note: "", task: "" });
const statusOptions: Array<{ value: "all" | ApplicationStatus; label: string }> = [
  { value: "all", label: "全部" }, { value: "prepared", label: "待投递" },
  { value: "opened", label: "已打开" }, { value: "applied", label: "已投递" },
  { value: "replied", label: "已回复" }, { value: "interview", label: "面试中" },
  { value: "closed", label: "已结束" },
];
const statusMeta: Record<ApplicationStatus, { label: string; type: "info" | "success" | "warning" | "danger" }> = {
  prepared: { label: "待投递", type: "warning" }, opened: { label: "已打开", type: "info" },
  applied: { label: "已投递", type: "success" }, replied: { label: "已回复", type: "success" },
  interview: { label: "面试中", type: "success" }, closed: { label: "已结束", type: "info" },
};
const filtered = computed(() => {
  const keyword = query.value.trim().toLocaleLowerCase();
  return applications.value.filter(item => {
    const statusOk = activeStatus.value === "all" || item.status === activeStatus.value;
    const textOk = !keyword || `${item.job_title} ${item.job_id} ${item.note}`.toLocaleLowerCase().includes(keyword);
    return statusOk && textOk;
  });
});
const counts = computed(() => ({
  all: applications.value.length,
  prepared: applications.value.filter(item => item.status === "prepared").length,
  applied: applications.value.filter(item => ["applied", "replied", "interview"].includes(item.status)).length,
  interview: applications.value.filter(item => item.status === "interview").length,
}));
function statusLabel(status: ApplicationStatus) { return statusMeta[status]?.label || status; }
function statusType(status: ApplicationStatus) { return statusMeta[status]?.type || "info"; }
async function load() {
  loading.value = true; error.value = "";
  try {
    applications.value = await api.applications();
  } catch (e) { error.value = err(e); } finally { loading.value = false; }
}
function openBoss(item: JobApplication) {
  window.open(item.boss_url, "_blank", "noopener,noreferrer");
  if (item.status === "prepared") updateStatus(item, "opened");
}
async function updateStatus(item: JobApplication, status: ApplicationStatus) {
  try {
    const updated = await api.updateApplication(item.id, { status });
    const index = applications.value.findIndex(row => row.id === item.id);
    if (index >= 0) applications.value[index] = updated;
    ElMessage.success(`已更新为${statusLabel(status)}`);
  } catch (e) { ElMessage.error(err(e)); }
}
async function copyGreeting(item: JobApplication) {
  try { await navigator.clipboard.writeText(item.greeting); ElMessage.success("开场白已复制"); }
  catch { ElMessage.warning("无法访问剪贴板，请在简历工作台查看开场白"); }
}
async function startAutomation(item: JobApplication) {
  try {
    const result = await api.startApplicationAutomation(item.id);
    const index = applications.value.findIndex(row => row.id === item.id);
    if (index >= 0) applications.value[index] = { ...applications.value[index], automation_status: result.status, automation_error: "" };
    ElMessage.success(result.message);
  } catch (e) { ElMessage.error(err(e)); }
}
async function confirmApplied(item: JobApplication) {
  try {
    const updated = await api.updateApplication(item.id, { status: "applied", note: "用户已在 BOSS 页面确认发送" });
    const index = applications.value.findIndex(row => row.id === item.id);
    if (index >= 0) applications.value[index] = updated;
    ElMessage.success("已记录为已投递");
  } catch (e) { ElMessage.error(err(e)); }
}
onMounted(load);
function goToJobs() {
  router.push("/resume");
}
function openFeedback(item: JobApplication) {
  editing.value = item;
  Object.assign(feedback, { status: item.status, note: item.note || "", task: "" });
  feedbackOpen.value = true;
}
async function saveFeedback() {
  if (!editing.value) return;
  saving.value = true;
  try {
    const updated = await api.updateApplication(editing.value.id, { status: feedback.status, note: feedback.note });
    applications.value = applications.value.map(item => item.id === updated.id ? updated : item);
    if (feedback.task.trim()) await api.addGrowthTask({ title: feedback.task.trim(), target_job: updated.job_title, source_key: `application:${updated.id}:${feedback.task.trim()}`, resource_query: feedback.task.trim() });
    feedbackOpen.value = false;
    ElMessage.success("投递反馈已保存");
  } catch (e) { ElMessage.error(err(e)); }
  finally { saving.value = false; }
}
</script>

<template>
  <div class="applications-page">
    <PageHeader title="IT 投递记录">
      <el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button>
      <el-button type="primary" :icon="Promotion" @click="goToJobs">从简历准备投递</el-button>
    </PageHeader>
    <div class="application-stats">
      <button class="application-stat" :class="{ active: activeStatus === 'all' }" @click="activeStatus = 'all'"><span>全部记录</span><strong>{{ counts.all }}</strong></button>
      <button class="application-stat" :class="{ active: activeStatus === 'prepared' }" @click="activeStatus = 'prepared'"><span>待投递</span><strong>{{ counts.prepared }}</strong></button>
      <button class="application-stat" :class="{ active: activeStatus === 'applied' }" @click="activeStatus = 'applied'"><span>进行中</span><strong>{{ counts.applied }}</strong></button>
      <button class="application-stat" :class="{ active: activeStatus === 'interview' }" @click="activeStatus = 'interview'"><span>面试中</span><strong>{{ counts.interview }}</strong></button>
    </div>
    <div class="application-toolbar">
      <el-input v-model="query" clearable :prefix-icon="Search" placeholder="搜索岗位名称或备注" />
      <el-radio-group v-model="activeStatus">
        <el-radio-button v-for="item in statusOptions" :key="item.value" :value="item.value">{{ item.label }}</el-radio-button>
      </el-radio-group>
    </div>
    <StateView :loading="loading" :error="error" :empty="!filtered.length" empty-text="还没有投递记录" @retry="load">
      <el-button type="primary" :icon="Promotion" @click="goToJobs">从简历准备投递</el-button>
      <template #content>
        <div class="application-list">
          <article v-for="item in filtered" :key="item.id" class="application-row">
            <div class="application-main">
              <div class="application-title"><div><span class="application-platform">BOSS 直聘</span><h3>{{ item.job_title }}</h3></div><el-tag :type="statusType(item.status)" effect="plain">{{ statusLabel(item.status) }}</el-tag></div>
              <p v-if="item.note" class="application-note">{{ item.note }}</p>
              <div class="application-meta"><span>准备于 {{ fmt(item.created_at) }}</span><span v-if="item.applied_at">投递于 {{ fmt(item.applied_at) }}</span></div>
            </div>
            <div class="application-actions">
              <el-button text :icon="CopyDocument" @click="copyGreeting(item)">复制开场白</el-button>
              <el-button v-if="item.status === 'prepared' || item.status === 'opened'" type="primary" :icon="Promotion" :loading="item.automation_status === 'starting'" @click="startAutomation(item)">打开并预填</el-button>
              <el-button v-if="item.status === 'opened'" type="success" plain :icon="Check" @click="confirmApplied(item)">已确认发送</el-button>
              <el-button v-if="item.status !== 'prepared' && item.status !== 'opened'" type="primary" plain :icon="Link" @click="openBoss(item)">继续跟进</el-button>
              <el-button text @click="openFeedback(item)">记录反馈</el-button>
            </div>
            <p v-if="item.automation_error" class="application-note application-error">{{ item.automation_error }}</p>
          </article>
        </div>
      </template>
    </StateView>
    <el-dialog v-model="feedbackOpen" title="投递反馈" width="min(600px, 94vw)">
      <el-form label-position="top"><el-form-item label="当前阶段"><el-select v-model="feedback.status"><el-option v-for="option in statusOptions.filter(item => item.value !== 'all')" :key="option.value" :value="option.value" :label="option.label" /></el-select></el-form-item><el-form-item label="面试或招聘反馈"><el-input v-model="feedback.note" type="textarea" :rows="4" maxlength="3000" /></el-form-item><el-form-item label="待补强任务（选填）"><el-input v-model="feedback.task" maxlength="300" placeholder="例如：补充 SQL 索引优化实践" /></el-form-item></el-form>
      <template #footer><el-button @click="feedbackOpen = false">取消</el-button><el-button type="primary" :loading="saving" @click="saveFeedback">保存反馈</el-button></template>
    </el-dialog>
  </div>
</template>

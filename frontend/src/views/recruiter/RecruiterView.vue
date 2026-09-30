<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Search, Refresh } from '@element-plus/icons-vue';
import { recruitmentApi } from '@/api/recruitment';
import { applicationLabels, applicationTone, jobLabels, reviewTransitions } from '@/utils/recruitment';
import { err, fmt } from '@/utils/format';
import type { RecruitmentJob, RecruitmentApplication, RecruiterProfile, ReviewState } from '@/types/recruitment';
import PageHeader from '@/components/common/PageHeader.vue';
import SectionPanel from '@/components/common/SectionPanel.vue';
import StateView from '@/components/common/StateView.vue';
import ResumeSnapshot from '@/components/recruitment/ResumeSnapshot.vue';

const router = useRouter(), route = useRoute();
const tab = ref(typeof route.query.tab === 'string' ? route.query.tab : 'jobs');
const jobs = ref<RecruitmentJob[]>([]), applications = ref<RecruitmentApplication[]>([]);
const jobTotal = ref(0), applicationTotal = ref(0), jobPage = ref(1), applicationPage = ref(1);
const jobFilters = reactive({ keyword: '', status: '' });
const applicationFilters = reactive({ status: '', job_id: undefined as number | undefined });
const jobsLoading = ref(false), applicationsLoading = ref(false), profileLoading = ref(false), saving = ref(false), busy = ref(false);
const jobsError = ref(''), applicationsError = ref(''), profileError = ref('');
const profile = reactive<RecruiterProfile>({ company_name: '', industry: '', city: '', description: '', contact_name: '', contact_email: '' });
const selected = ref<RecruitmentApplication | null>(null), reviewStatus = ref<ReviewState>('reviewing'), feedback = ref('');
const reviewOptions = computed(() => selected.value ? reviewTransitions[selected.value.status] : []);
const dialogOpen = ref(false);

async function loadJobs() {
  jobsLoading.value = true; jobsError.value = '';
  try { const result = await recruitmentApi.ownedJobs({ ...jobFilters, page: jobPage.value, page_size: 10 }); jobs.value = result.items; jobTotal.value = result.total; }
  catch (e) { jobsError.value = err(e); } finally { jobsLoading.value = false; }
}
async function loadApplications() {
  applicationsLoading.value = true; applicationsError.value = '';
  try { const result = await recruitmentApi.received({ ...applicationFilters, page: applicationPage.value, page_size: 10 }); applications.value = result.items; applicationTotal.value = result.total; }
  catch (e) { applicationsError.value = err(e); } finally { applicationsLoading.value = false; }
}
async function loadProfile() {
  profileLoading.value = true; profileError.value = '';
  try { Object.assign(profile, await recruitmentApi.profile()); }
  catch (e) { profileError.value = err(e); } finally { profileLoading.value = false; }
}
async function saveProfile() {
  saving.value = true;
  try { Object.assign(profile, await recruitmentApi.saveProfile(profile)); ElMessage.success('企业资料已保存'); }
  catch (e) { ElMessage.error(err(e)); } finally { saving.value = false; }
}
async function changeStatus(job: RecruitmentJob) {
  const status = job.status === 'published' ? 'closed' : 'published';
  try { await ElMessageBox.confirm(status === 'published' ? `发布“${job.title || '未命名岗位'}”后，学生即可查看并投递。` : '下架后停止接收新投递，已有投递会保留。', status === 'published' ? '发布岗位' : '下架岗位', { confirmButtonText: status === 'published' ? '发布' : '下架', cancelButtonText: '取消', type: 'warning' }); }
  catch { return; }
  busy.value = true;
  try { await recruitmentApi.jobStatus(job.id, status); ElMessage.success(status === 'published' ? '岗位已发布' : '岗位已下架'); await loadJobs(); }
  catch (e) { ElMessage.error(err(e)); } finally { busy.value = false; }
}
async function remove(job: RecruitmentJob) {
  try { await ElMessageBox.confirm('删除后无法恢复。有投递记录的岗位不能删除，可选择下架。', '删除岗位', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }); }
  catch { return; }
  busy.value = true;
  try { await recruitmentApi.deleteJob(job.id); if (jobs.value.length === 1 && jobPage.value > 1) jobPage.value--; ElMessage.success('岗位已删除'); await loadJobs(); }
  catch (e) { ElMessage.error(err(e)); } finally { busy.value = false; }
}
function showApplications(job: RecruitmentJob) {
  applicationFilters.job_id = job.id; applicationPage.value = 1; tab.value = 'applications'; loadApplications();
}
function openApplication(item: RecruitmentApplication) {
  selected.value = item; reviewStatus.value = reviewTransitions[item.status][0] || 'reviewing'; feedback.value = item.feedback; dialogOpen.value = true;
}
async function saveReview() {
  if (!selected.value) return;
  saving.value = true;
  try { selected.value = await recruitmentApi.review(selected.value.id, { status: reviewStatus.value, feedback: feedback.value }); ElMessage.success('处理结果已保存，学生可在站内查看'); dialogOpen.value = false; await loadApplications(); }
  catch (e) { ElMessage.error(err(e)); } finally { saving.value = false; }
}
watch(tab, value => { router.replace({ query: { tab: value } }); });
watch(() => route.query.tab, value => { if (typeof value === 'string' && ['jobs', 'applications', 'profile'].includes(value)) tab.value = value; });
onMounted(() => { if (!['jobs', 'applications', 'profile'].includes(tab.value)) tab.value = 'jobs'; loadJobs(); loadApplications(); loadProfile(); });
</script>

<template>
  <div>
    <PageHeader title="招聘工作台" description="维护企业资料，发布招聘岗位，跟进学生的简历投递。">
      <el-button :icon="Refresh" @click="loadJobs(); loadApplications(); loadProfile()">刷新</el-button>
      <el-button type="primary" :icon="Plus" @click="router.push('/recruiter/jobs/new')">创建岗位</el-button>
    </PageHeader>
    <p v-if="!profileLoading && !profileError && (!profile.company_name || !profile.contact_email || !profile.contact_name)" class="callout">发布前请完善企业名称、联系人和联系邮箱。<el-button link type="primary" @click="tab = 'profile'">完善企业资料</el-button></p>
    <el-tabs v-model="tab" class="workspace-tabs">
      <el-tab-pane label="岗位管理" name="jobs">
        <div class="filter-bar">
          <el-input v-model="jobFilters.keyword" :prefix-icon="Search" placeholder="搜索岗位" clearable @keyup.enter="jobPage = 1; loadJobs()" />
          <el-select v-model="jobFilters.status" clearable placeholder="全部状态"><el-option v-for="(label, value) in jobLabels" :key="value" :label="label" :value="value" /></el-select>
          <el-button type="primary" @click="jobPage = 1; loadJobs()">搜索</el-button>
        </div>
        <StateView :loading="jobsLoading" :error="jobsError" :empty="!jobs.length" empty-text="暂无招聘岗位" @retry="loadJobs">
          <template #hint>创建岗位草稿，完善企业与岗位信息后即可发布。</template>
          <el-button type="primary" @click="router.push('/recruiter/jobs/new')">创建第一个岗位</el-button>
          <template #content>
            <SectionPanel title="我的岗位" :subtitle="`共 ${jobTotal} 个岗位`">
              <div class="mobile-list"><article v-for="job in jobs" :key="job.id" class="mobile-item">
                <div class="mobile-heading"><b>{{ job.title || '未命名草稿' }}</b><el-tag :type="job.status === 'published' ? 'success' : 'info'">{{ jobLabels[job.status] }}</el-tag></div>
                <p class="summary-text">{{ job.city || '城市待填写' }} · {{ job.employment_type }} · {{ job.salary || '薪资待填写' }}</p><p class="muted">{{ fmt(job.updated_at) }}</p>
                <div class="mobile-actions"><el-button size="small" :disabled="busy || job.status === 'published'" @click="router.push(`/recruiter/jobs/${job.id}/edit`)">编辑</el-button><el-button size="small" type="primary" plain :disabled="busy" @click="changeStatus(job)">{{ job.status === 'published' ? '下架' : '发布' }}</el-button><el-button size="small" @click="showApplications(job)">查看投递</el-button><el-button size="small" type="danger" plain :disabled="busy || job.status === 'published'" @click="remove(job)">删除</el-button></div>
              </article></div>
              <el-table class="desktop-table" :data="jobs" style="width:100%">
                <el-table-column label="岗位" min-width="190"><template #default="{ row }"><b>{{ row.title || '未命名草稿' }}</b><p class="muted">{{ row.city || '城市待填写' }} · {{ row.employment_type }} · {{ row.salary || '薪资待填写' }}</p></template></el-table-column>
                <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="row.status === 'published' ? 'success' : 'info'">{{ jobLabels[row.status as keyof typeof jobLabels] }}</el-tag></template></el-table-column>
                <el-table-column label="更新时间" min-width="165"><template #default="{ row }">{{ fmt(row.updated_at) }}</template></el-table-column>
                <el-table-column label="操作" min-width="245"><template #default="{ row }">
                  <el-button link type="primary" :disabled="busy || row.status === 'published'" @click="router.push(`/recruiter/jobs/${row.id}/edit`)">编辑</el-button>
                  <el-button link type="primary" :disabled="busy" @click="changeStatus(row)">{{ row.status === 'published' ? '下架' : '发布' }}</el-button>
                  <el-button link type="primary" @click="showApplications(row)">查看投递</el-button>
                  <el-button link type="danger" :disabled="busy || row.status === 'published'" @click="remove(row)">删除</el-button>
                </template></el-table-column>
              </el-table>
            </SectionPanel>
          </template>
        </StateView>
        <el-pagination v-if="jobTotal > 10" v-model:current-page="jobPage" :page-size="10" :total="jobTotal" layout="prev, pager, next" @current-change="loadJobs" />
      </el-tab-pane>
      <el-tab-pane label="收到的投递" name="applications">
        <div class="filter-bar">
          <el-input v-if="applicationFilters.job_id" :model-value="`岗位编号：${applicationFilters.job_id}`" readonly><template #append><el-button @click="applicationFilters.job_id = undefined; applicationPage = 1; loadApplications()">清除岗位筛选</el-button></template></el-input>
          <el-select v-model="applicationFilters.status" clearable placeholder="全部投递状态"><el-option v-for="(label, value) in applicationLabels" :key="value" :label="label" :value="value" /></el-select>
          <el-button type="primary" @click="applicationPage = 1; loadApplications()">筛选</el-button>
        </div>
        <StateView :loading="applicationsLoading" :error="applicationsError" :empty="!applications.length" empty-text="暂无符合条件的投递" @retry="loadApplications">
          <template #hint>学生向你发布的岗位投递简历后，会显示在这里。</template>
          <template #content><SectionPanel title="收到的简历" :subtitle="`共 ${applicationTotal} 份投递`">
            <div class="mobile-list"><article v-for="item in applications" :key="item.id" class="mobile-item"><div class="mobile-heading"><b>{{ item.resume_snapshot.profile.name }}</b><el-tag :type="applicationTone(item.status)">{{ applicationLabels[item.status] }}</el-tag></div><p class="summary-text">{{ item.job_title }}</p><p class="muted">{{ item.resume_snapshot.profile.school }} · {{ item.resume_snapshot.profile.major }}</p><p class="muted">{{ fmt(item.created_at) }}</p><div class="mobile-actions"><el-button size="small" type="primary" plain @click="openApplication(item)">查看简历</el-button></div></article></div>
            <el-table class="desktop-table" :data="applications" style="width:100%">
              <el-table-column label="候选人" min-width="180"><template #default="{ row }"><b>{{ row.resume_snapshot.profile.name }}</b><p class="muted">{{ row.resume_snapshot.profile.school }} · {{ row.resume_snapshot.profile.major }}</p></template></el-table-column>
              <el-table-column prop="job_title" label="投递岗位" min-width="170" />
              <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="applicationTone(row.status)">{{ applicationLabels[row.status as keyof typeof applicationLabels] }}</el-tag></template></el-table-column>
              <el-table-column label="投递时间" min-width="165"><template #default="{ row }">{{ fmt(row.created_at) }}</template></el-table-column>
              <el-table-column label="操作" width="120"><template #default="{ row }"><el-button link type="primary" @click="openApplication(row)">查看简历</el-button></template></el-table-column>
            </el-table>
          </SectionPanel></template>
        </StateView>
        <el-pagination v-if="applicationTotal > 10" v-model:current-page="applicationPage" :page-size="10" :total="applicationTotal" layout="prev, pager, next" @current-change="loadApplications" />
      </el-tab-pane>
      <el-tab-pane label="企业资料" name="profile">
        <StateView :loading="profileLoading" :error="profileError" @retry="loadProfile"><template #content>
          <SectionPanel title="企业与招聘联系人" subtitle="企业资料由招聘者填写，用于岗位展示，不代表平台已认证。">
            <el-form label-position="top" @submit.prevent="saveProfile">
              <div class="profile-grid">
                <el-form-item label="企业名称"><el-input v-model="profile.company_name" maxlength="150" placeholder="发布岗位前必填" /></el-form-item>
                <el-form-item label="所属行业"><el-input v-model="profile.industry" maxlength="80" /></el-form-item>
                <el-form-item label="企业所在城市"><el-input v-model="profile.city" maxlength="80" /></el-form-item>
                <el-form-item label="联系人"><el-input v-model="profile.contact_name" maxlength="50" placeholder="发布岗位前必填" /></el-form-item>
                <el-form-item label="联系邮箱"><el-input v-model="profile.contact_email" type="email" maxlength="100" placeholder="发布岗位前必填，学生可查看" /></el-form-item>
              </div>
              <el-form-item label="企业简介"><el-input v-model="profile.description" type="textarea" :rows="6" maxlength="10000" show-word-limit /></el-form-item>
              <el-button type="primary" native-type="submit" :loading="saving">保存企业资料</el-button>
            </el-form>
          </SectionPanel>
        </template></StateView>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="dialogOpen" title="查看投递简历" width="min(780px, 94vw)" :close-on-click-modal="false">
      <template v-if="selected">
        <p class="callout">投递岗位：{{ selected.job_title }} · {{ applicationLabels[selected.status] }}</p>
        <ResumeSnapshot :resume="selected.resume_snapshot" />
        <SectionPanel v-if="selected.note" title="求职说明"><p class="markdown-text">{{ selected.note }}</p></SectionPanel>
        <el-form v-if="reviewOptions.length" label-position="top" class="review-form">
          <el-form-item label="处理状态"><el-select v-model="reviewStatus" aria-label="处理状态"><el-option v-for="status in reviewOptions" :key="status" :value="status" :label="applicationLabels[status]" /></el-select></el-form-item>
          <el-form-item label="给学生的反馈"><el-input v-model="feedback" type="textarea" :rows="4" maxlength="2000" show-word-limit placeholder="填写面试沟通方式或处理说明，学生可在站内查看" /></el-form-item>
        </el-form>
        <p v-else class="callout">投递已结束。{{ selected.feedback || '暂无招聘反馈' }}</p>
      </template>
      <template #footer><el-button :disabled="saving" @click="dialogOpen = false">关闭</el-button><el-button v-if="reviewOptions.length" type="primary" :loading="saving" @click="saveReview">保存处理结果</el-button></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.workspace-tabs { margin-top: 22px; }
.profile-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 20px; }
.el-pagination { margin-top: 22px; justify-content: center; }
.review-form { margin-top: 24px; }
.mobile-list { display: none; }
.mobile-item + .mobile-item { margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--color-border-light); }
.mobile-heading { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.mobile-heading b { overflow-wrap: anywhere; }
.mobile-heading .el-tag { flex-shrink: 0; }
.mobile-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.mobile-actions .el-button { margin-left: 0; }
@media (max-width: 700px) { .profile-grid { grid-template-columns: 1fr; } .filter-bar { flex-wrap: wrap; } .desktop-table { display: none; } .mobile-list { display: block; } }
</style>

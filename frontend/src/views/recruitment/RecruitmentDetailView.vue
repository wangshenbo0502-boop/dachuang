<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowLeft, Promotion } from '@element-plus/icons-vue';
import { api } from '@/api';
import { recruitmentApi } from '@/api/recruitment';
import { useAuthStore } from '@/stores/auth';
import { err } from '@/utils/format';
import type { ResumeVersion } from '@/types/api';
import type { RecruitmentJob, ResumeSnapshot as SnapshotData } from '@/types/recruitment';
import StateView from '@/components/common/StateView.vue';
import SectionPanel from '@/components/common/SectionPanel.vue';
import ResumeSnapshot from '@/components/recruitment/ResumeSnapshot.vue';

const route = useRoute(), router = useRouter(), auth = useAuthStore();
const job = ref<RecruitmentJob | null>(null), loading = ref(false), error = ref('');
const dialog = ref(false), resumes = ref<ResumeVersion[]>([]), resumeId = ref<number | null>(null), note = ref('');
const resumesLoading = ref(false), resumeError = ref(''), submitting = ref(false), consent = ref(false), applied = ref(false);
const preview = computed<SnapshotData | null>(() => {
  const resume = resumes.value.find(r => r.id === resumeId.value);
  if (!resume) return null;
  const expressions = resume.optimized_content.optimized_projects;
  return { name: resume.name, target_job: resume.target_job, personal_summary: resume.personal_summary || String((resume.profile as unknown as { bio?: string }).bio || ''),
    profile: { ...resume.profile, projects: resume.profile.projects.map(project => {
      const expression = Array.isArray(expressions) ? expressions.find(item => item?.project_name === project.name && typeof item?.optimized === 'string') : null;
      return { ...project, description: expression?.optimized || project.description };
    }) } };
});
async function load() {
  loading.value = true; error.value = ''; job.value = null; applied.value = false;
  try { job.value = await recruitmentApi.job(Number(route.params.id)); }
  catch (e) { error.value = err(e); } finally { loading.value = false; }
}
async function loadResumes() {
  resumesLoading.value = true; resumeError.value = '';
  try { resumes.value = await api.resumeVersions(auth.userId!); if (!resumes.value.some(r => r.id === resumeId.value)) resumeId.value = resumes.value[0]?.id || null; }
  catch (e) { resumeError.value = err(e); } finally { resumesLoading.value = false; }
}
function startApply() { consent.value = false; dialog.value = true; loadResumes(); }
async function submit() {
  if (!resumeId.value || !consent.value || !job.value || submitting.value) return;
  submitting.value = true; resumeError.value = '';
  try {
    await recruitmentApi.apply(job.value.id, { resume_id: resumeId.value, note: note.value });
    applied.value = true; dialog.value = false; ElMessage.success('简历已投递，可在站内投递中查看进度');
  } catch (e) { resumeError.value = err(e); } finally { submitting.value = false; }
}
watch(resumeId, () => { consent.value = false; });
watch(() => route.params.id, load);
onMounted(load);
</script>

<template>
  <div>
    <div class="detail-back"><el-button :icon="ArrowLeft" text @click="router.push('/recruitment')">返回招聘岗位</el-button></div>
    <StateView :loading="loading" :error="error" :empty="!job" @retry="load"><template #content>
      <template v-if="job">
        <div class="job-detail-head">
          <div><el-tag>{{ job.category }}</el-tag><h2>{{ job.title }}</h2><p class="salary">{{ job.salary }}</p><p class="summary-text">{{ job.company_name }} · {{ job.city }} · {{ job.employment_type }} · {{ job.education }} · {{ job.experience }}</p></div>
          <div class="job-detail-actions"><el-button v-if="!applied" type="primary" :icon="Promotion" @click="startApply">投递简历</el-button><el-button v-else type="primary" plain @click="router.push('/recruitment/applications')">查看投递进度</el-button></div>
        </div>
        <div class="detail-layout">
          <div>
            <SectionPanel title="岗位职责"><p class="markdown-text">{{ job.description }}</p></SectionPanel>
            <SectionPanel title="任职要求"><p class="markdown-text">{{ job.requirements }}</p><div class="tag-row"><el-tag v-for="tag in job.tags" :key="tag" effect="plain">{{ tag }}</el-tag></div></SectionPanel>
          </div>
          <aside><SectionPanel title="企业与联系方式" subtitle="资料由招聘者填写"><h3>{{ job.company_name }}</h3><p class="summary-text">{{ job.company?.industry || '行业未填写' }} · {{ job.company?.city || '企业城市未填写' }}</p><p class="markdown-text company-intro">{{ job.company?.description || '暂无企业简介' }}</p><p>联系人：{{ job.company?.contact_name }}</p><p class="contact">联系邮箱：{{ job.company?.contact_email }}</p></SectionPanel></aside>
        </div>
      </template>
    </template></StateView>
    <el-dialog v-model="dialog" title="确认投递简历" width="min(740px, 94vw)" :close-on-click-modal="false" :show-close="!submitting" :close-on-press-escape="!submitting">
      <el-alert v-if="resumeError" :title="resumeError" type="error" :closable="false" show-icon />
      <StateView :loading="resumesLoading" :empty="!resumes.length" empty-text="还没有可投递的简历版本">
        <template #hint>先在“我的简历”创建一个版本，再选择要分享的内容。</template>
        <el-button type="primary" @click="dialog = false; router.push('/resume')">创建简历</el-button>
        <template #content>
          <el-form label-position="top" :disabled="submitting">
            <el-form-item label="选择简历版本"><el-select v-model="resumeId" aria-label="选择简历版本" style="width:100%"><el-option v-for="resume in resumes" :key="resume.id" :value="resume.id" :label="`${resume.name} · ${resume.target_job}`" /></el-select></el-form-item>
            <el-form-item label="求职说明（可选）"><el-input v-model="note" type="textarea" :rows="3" maxlength="2000" show-word-limit /></el-form-item>
          </el-form>
          <ResumeSnapshot v-if="preview" :resume="preview" />
          <el-checkbox v-model="consent" :disabled="submitting" class="consent">我确认将上方简历及联系方式分享给该岗位招聘者</el-checkbox>
        </template>
      </StateView>
      <template #footer><el-button :disabled="submitting" @click="dialog = false">取消</el-button><el-button type="primary" :disabled="!resumeId || !consent || resumesLoading" :loading="submitting" @click="submit">确认投递</el-button></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.salary { font-size: 22px; color: var(--color-primary); font-weight: 600; margin: 8px 0; }
.company-intro { margin: 18px 0; }
.contact { overflow-wrap: anywhere; }
.tag-row { margin-top: 18px; }
.consent { margin-top: 20px; height: auto; }
.consent :deep(.el-checkbox__label) { white-space: normal; }
</style>

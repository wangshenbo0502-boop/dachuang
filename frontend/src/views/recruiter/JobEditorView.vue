<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowLeft } from '@element-plus/icons-vue';
import { recruitmentApi } from '@/api/recruitment';
import { emptyJob, jobCategories } from '@/utils/recruitment';
import { err } from '@/utils/format';
import PageHeader from '@/components/common/PageHeader.vue';
import SectionPanel from '@/components/common/SectionPanel.vue';
import StateView from '@/components/common/StateView.vue';

const route = useRoute(), router = useRouter();
const id = ref(route.params.id ? Number(route.params.id) : null);
const form = reactive(emptyJob()), baseline = ref(JSON.stringify(form));
const tagText = ref(''), loading = ref(false), saving = ref(false), error = ref(typeof route.query.publish_error === 'string' ? route.query.publish_error : ''), online = ref(false);
const loadError = ref('');
const dirty = computed(() => JSON.stringify(form) !== baseline.value || tagText.value !== form.tags.join('、'));
async function load() {
  if (!id.value) return;
  loading.value = true; loadError.value = '';
  try {
    const job = await recruitmentApi.ownedJob(id.value);
    for (const key of Object.keys(form) as Array<keyof typeof form>) Object.assign(form, { [key]: job[key] });
    tagText.value = form.tags.join('、'); baseline.value = JSON.stringify(form); online.value = job.status === 'published';
  } catch (e) { loadError.value = err(e); } finally { loading.value = false; }
}
async function save(publish = false) {
  if (saving.value) return;
  if (publish) {
    try { await ElMessageBox.confirm('保存并发布后，学生即可查看该岗位和投递简历。', '发布岗位', { confirmButtonText: '保存并发布', cancelButtonText: '取消' }); }
    catch { return; }
  }
  saving.value = true; error.value = '';
  try {
    form.tags = [...new Set(tagText.value.split(/[,，、\n]/).map(v => v.trim()).filter(Boolean))];
    const job = id.value ? await recruitmentApi.saveJob(id.value, form) : await recruitmentApi.createJob(form);
    id.value = job.id; tagText.value = form.tags.join('、'); baseline.value = JSON.stringify(form);
    if (publish) await recruitmentApi.jobStatus(job.id, 'published');
    ElMessage.success(publish ? '岗位已发布' : '岗位已保存');
    await router.push('/recruiter');
  } catch (e) {
    error.value = err(e);
    if (id.value && !route.params.id) await router.replace({ path: `/recruiter/jobs/${id.value}/edit`, query: { publish_error: error.value } });
  } finally { saving.value = false; }
}
async function confirmLeave() {
  if (saving.value || !dirty.value) return true;
  try { await ElMessageBox.confirm('当前修改尚未保存，离开后将丢失。', '离开编辑页面', { confirmButtonText: '离开', cancelButtonText: '继续编辑', type: 'warning' }); return true; }
  catch { return false; }
}
onBeforeRouteLeave(confirmLeave);
onBeforeRouteUpdate(to => to.params.id === route.params.id ? true : confirmLeave());
watch(() => route.params.id, async value => {
  const nextId = value ? Number(value) : null;
  if (nextId === id.value) return;
  id.value = nextId; Object.assign(form, emptyJob()); tagText.value = ''; error.value = ''; loadError.value = ''; online.value = false;
  baseline.value = JSON.stringify(form); await load();
});
onMounted(load);
</script>

<template>
  <div>
    <PageHeader :title="id ? '编辑招聘岗位' : '创建招聘岗位'" description="先保存草稿，完善岗位和企业资料后再发布。"><el-button :icon="ArrowLeft" :disabled="saving" @click="router.push('/recruiter')">返回工作台</el-button></PageHeader>
    <StateView :loading="loading" :error="loadError" @retry="load"><template #content>
      <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" class="form-alert" />
      <SectionPanel title="岗位信息" subtitle="招聘中的岗位请先在工作台下架，再编辑内容。">
        <el-alert v-if="online" title="该岗位正在招聘，请返回工作台先下架。" type="warning" :closable="false" show-icon />
        <el-form label-position="top" :disabled="online || saving" @submit.prevent="save(false)">
          <div class="editor-grid">
            <el-form-item label="岗位名称"><el-input v-model="form.title" maxlength="150" placeholder="例如：前端开发实习生" /></el-form-item>
            <el-form-item label="岗位分类"><el-select v-model="form.category" placeholder="请选择分类"><el-option v-for="category in jobCategories" :key="category" :label="category" :value="category" /></el-select></el-form-item>
            <el-form-item label="工作城市"><el-input v-model="form.city" maxlength="80" placeholder="例如：成都" /></el-form-item>
            <el-form-item label="薪资说明"><el-input v-model="form.salary" maxlength="80" placeholder="例如：200–300 元/天，或面议" /></el-form-item>
            <el-form-item label="用工类型"><el-select v-model="form.employment_type"><el-option v-for="value in ['实习', '全职', '兼职']" :key="value" :value="value" /></el-select></el-form-item>
            <el-form-item label="学历要求"><el-select v-model="form.education"><el-option v-for="value in ['不限', '大专', '本科', '硕士', '博士']" :key="value" :value="value" /></el-select></el-form-item>
            <el-form-item label="经验要求"><el-input v-model="form.experience" maxlength="80" /></el-form-item>
            <el-form-item label="技能标签"><el-input v-model="tagText" placeholder="用逗号或顿号分隔，例如：Vue、TypeScript" /></el-form-item>
          </div>
          <el-form-item label="岗位职责"><el-input v-model="form.description" type="textarea" :rows="7" maxlength="20000" show-word-limit placeholder="说明实际工作内容" /></el-form-item>
          <el-form-item label="任职要求"><el-input v-model="form.requirements" type="textarea" :rows="7" maxlength="20000" show-word-limit placeholder="填写技能、经验与到岗要求" /></el-form-item>
          <div class="editor-actions"><el-button type="primary" plain native-type="submit" :loading="saving">保存草稿</el-button><el-button type="primary" :loading="saving" @click="save(true)">保存并发布</el-button></div>
        </el-form>
      </SectionPanel>
    </template></StateView>
  </div>
</template>

<style scoped>
.editor-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 20px; }
.el-select { width: 100%; }
.editor-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 12px; }
.form-alert { margin-bottom: 16px; }
@media (max-width: 700px) { .editor-grid { grid-template-columns: 1fr; } }
</style>

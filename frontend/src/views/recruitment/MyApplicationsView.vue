<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Refresh } from '@element-plus/icons-vue';
import { recruitmentApi } from '@/api/recruitment';
import { applicationLabels, applicationTone, canWithdraw } from '@/utils/recruitment';
import { err, fmt } from '@/utils/format';
import type { RecruitmentApplication } from '@/types/recruitment';
import PageHeader from '@/components/common/PageHeader.vue';
import SectionPanel from '@/components/common/SectionPanel.vue';
import StateView from '@/components/common/StateView.vue';
import ResumeSnapshot from '@/components/recruitment/ResumeSnapshot.vue';

const router = useRouter();
const items = ref<RecruitmentApplication[]>([]), total = ref(0), page = ref(1), loading = ref(false), busy = ref(false), error = ref('');
const selected = ref<RecruitmentApplication | null>(null), dialog = ref(false);
async function load() {
  loading.value = true; error.value = '';
  try { const result = await recruitmentApi.applications({ page: page.value, page_size: 10 }); items.value = result.items; total.value = result.total; }
  catch (e) { error.value = err(e); } finally { loading.value = false; }
}
async function withdraw(item: RecruitmentApplication) {
  try { await ElMessageBox.confirm('撤回后招聘者不能继续处理本次投递，同一岗位不能重复投递。', '撤回投递', { type: 'warning', confirmButtonText: '撤回', cancelButtonText: '取消' }); }
  catch { return; }
  busy.value = true;
  try { await recruitmentApi.withdraw(item.id); ElMessage.success('投递已撤回'); await load(); }
  catch (e) { ElMessage.error(err(e)); } finally { busy.value = false; }
}
onMounted(load);
</script>

<template>
  <div>
    <PageHeader title="我的站内投递" description="查看已分享的简历与招聘者反馈，跟踪站内招聘进度。"><el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button><el-button type="primary" :icon="Search" @click="router.push('/recruitment')">浏览招聘岗位</el-button></PageHeader>
    <StateView :loading="loading" :error="error" :empty="!items.length" empty-text="还没有站内投递记录" @retry="load">
      <template #hint>选择一个招聘岗位，使用自己的简历版本完成投递。</template>
      <el-button type="primary" @click="router.push('/recruitment')">浏览招聘岗位</el-button>
      <template #content>
        <p class="resource-count">共 {{ total }} 条投递记录</p>
        <SectionPanel v-for="item in items" :key="item.id" :title="item.job_title" :subtitle="`${item.company_name} · ${fmt(item.created_at)}`">
          <template #action><el-tag :type="applicationTone(item.status)">{{ applicationLabels[item.status] }}</el-tag></template>
          <p class="summary-text">投递简历：{{ item.resume_snapshot.name }}</p>
          <p class="callout">招聘反馈：{{ item.feedback || '暂无招聘者反馈' }}</p>
          <div class="application-actions"><el-button @click="selected = item; dialog = true">查看投递简历</el-button><el-button v-if="canWithdraw(item.status)" type="danger" plain :disabled="busy" @click="withdraw(item)">撤回投递</el-button></div>
        </SectionPanel>
      </template>
    </StateView>
    <el-pagination v-if="total > 10" v-model:current-page="page" :page-size="10" :total="total" layout="prev, pager, next" @current-change="load" />
    <el-dialog v-model="dialog" title="已投递的简历" width="min(740px, 94vw)"><ResumeSnapshot v-if="selected" :resume="selected.resume_snapshot" /><p v-if="selected?.note" class="callout">求职说明：{{ selected.note }}</p></el-dialog>
  </div>
</template>

<style scoped>
.application-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
.el-pagination { margin-top: 22px; justify-content: center; }
</style>

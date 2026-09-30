<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Document } from '@element-plus/icons-vue';
import { recruitmentApi } from '@/api/recruitment';
import { jobCategories } from '@/utils/recruitment';
import { err } from '@/utils/format';
import type { RecruitmentJob } from '@/types/recruitment';
import PageHeader from '@/components/common/PageHeader.vue';
import StateView from '@/components/common/StateView.vue';

const router = useRouter();
const jobs = ref<RecruitmentJob[]>([]), total = ref(0), page = ref(1), loading = ref(false), error = ref('');
const filters = reactive({ keyword: '', category: '', city: '' });
async function load() {
  loading.value = true; error.value = '';
  try { const result = await recruitmentApi.jobs({ ...filters, page: page.value, page_size: 12 }); jobs.value = result.items; total.value = result.total; }
  catch (e) { error.value = err(e); } finally { loading.value = false; }
}
function search() { page.value = 1; load(); }
onMounted(load);
</script>

<template>
  <div>
    <PageHeader title="招聘岗位" description="查看招聘者发布的真实招聘信息，选择简历进行站内投递。"><el-button :icon="Document" @click="router.push('/recruitment/applications')">我的站内投递</el-button></PageHeader>
    <div class="filter-bar recruitment-filters">
      <el-input v-model="filters.keyword" :prefix-icon="Search" clearable placeholder="搜索岗位、企业或技能" @keyup.enter="search" />
      <el-select v-model="filters.category" clearable placeholder="全部分类"><el-option v-for="category in jobCategories" :key="category" :label="category" :value="category" /></el-select>
      <el-input v-model="filters.city" clearable placeholder="工作城市" @keyup.enter="search" />
      <el-button type="primary" @click="search">搜索</el-button>
    </div>
    <StateView :loading="loading" :error="error" :empty="!jobs.length" empty-text="暂无符合条件的招聘岗位" @retry="load">
      <template #hint>招聘者发布岗位后会显示在这里，也可以调整搜索条件。</template>
      <template #content>
        <p class="resource-count">共 {{ total }} 个招聘岗位</p>
        <div class="job-grid">
          <article v-for="job in jobs" :key="job.id" class="job-card vacancy-card" tabindex="0" role="link" :aria-label="`查看岗位：${job.title}`" @click="router.push(`/recruitment/jobs/${job.id}`)" @keydown.enter="router.push(`/recruitment/jobs/${job.id}`)">
            <header><div><el-tag size="small" effect="plain">{{ job.category }}</el-tag><h3>{{ job.title }}</h3></div></header>
            <b class="salary">{{ job.salary }}</b>
            <p>{{ job.company_name }}</p><p class="muted">{{ job.city }} · {{ job.employment_type }} · {{ job.education }} · {{ job.experience }}</p>
            <p class="snippet">{{ job.description.slice(0, 110) }}</p>
            <div class="tag-row"><el-tag v-for="tag in job.tags.slice(0, 5)" :key="tag" size="small" type="info">{{ tag }}</el-tag></div>
            <footer>查看详情与投递 <span>→</span></footer>
          </article>
        </div>
      </template>
    </StateView>
    <el-pagination v-if="total > 12" v-model:current-page="page" :page-size="12" :total="total" layout="prev, pager, next" @current-change="load" />
  </div>
</template>

<style scoped>
.salary { color: var(--color-primary); font-size: 17px; }
.vacancy-card { overflow-wrap: anywhere; }
.snippet { min-height: 44px; }
.el-pagination { margin-top: 24px; justify-content: center; }
@media (max-width: 700px) { .recruitment-filters { flex-wrap: wrap; } }
</style>

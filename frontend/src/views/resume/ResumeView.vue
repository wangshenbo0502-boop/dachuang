<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { Check, CopyDocument, Edit, MagicStick, Plus, Printer, Refresh, Select } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useUserStore } from "@/stores/user";
import type { ResumeVersion, StudentProfile } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";
import SectionPanel from "@/components/common/SectionPanel.vue";
import StateView from "@/components/common/StateView.vue";

const user = useUserStore();
const profile = ref<StudentProfile | null>(null);
const versions = ref<ResumeVersion[]>([]);
const selected = ref<ResumeVersion | null>(null);
const loading = ref(true);
const saving = ref(false);
const dialog = ref(false);
const copySource = ref<ResumeVersion | null>(null);
const optimizing = ref(false);
const pending = ref<Record<string, unknown> | null>(null);
const form = reactive({ name: "", target_job: "", selected_projects: [] as number[], selected_skills: [] as number[], selected_experiences: { competitions: [] as number[], internships: [] as number[] } });
const selectedSkills = computed(() => {
  if (!selected.value) return [];
  const ids = new Set(selected.value.selected_skills);
  return selected.value.profile.skills.filter((item) => ids.has(item.id!));
});
const selectedProjects = computed(() => {
  if (!selected.value) return [];
  const ids = new Set(selected.value.selected_projects);
  return selected.value.profile.projects.filter((item) => ids.has(item.id!));
});
const selectedInternships = computed(() => {
  if (!selected.value) return [];
  const ids = new Set(selected.value.selected_experiences.internships || []);
  return selected.value.profile.internships.filter((item) => ids.has(item.id!));
});
const selectedCompetitions = computed(() => {
  if (!selected.value) return [];
  const ids = new Set(selected.value.selected_experiences.competitions || []);
  return selected.value.profile.competitions.filter((item) => ids.has(item.id!));
});
const optimizedProjects = computed(() => {
  const items = selected.value?.optimized_content?.optimized_projects;
  return Array.isArray(items) ? items as Array<{ project_name?: string; optimized?: string }> : [];
});

function projectDescription(name: string, fallback: string) {
  return optimizedProjects.value.find((item) => item.project_name === name)?.optimized || fallback;
}
function formatDateRange(start?: string | null, end?: string | null) {
  if (!start && !end) return "";
  return `${start || "至今"} - ${end || "至今"}`;
}
function printResume() {
  window.print();
}
function formatVersionTime(value?: string) {
  if (!value) return "刚刚";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "刚刚" : date.toLocaleDateString("zh-CN", { year: "numeric", month: "numeric", day: "numeric" });
}

function numberList(value: unknown): number[] {
  return Array.isArray(value)
    ? value.filter((item): item is number => Number.isInteger(item))
    : [];
}

function experienceList(value: unknown, key: "competitions" | "internships"): number[] {
  if (!value || typeof value !== "object") return [];
  return numberList((value as Record<string, unknown>)[key]);
}

async function load() {
  loading.value = true;
  try {
    profile.value = await api.getUser(user.userId!);
    versions.value = await api.resumeVersions(user.userId!);
    if (selected.value) selected.value = await api.resumeVersion(selected.value.id);
    else if (versions.value[0]) selected.value = versions.value[0];
  } catch (error) { ElMessage.error(error instanceof Error ? error.message : "简历数据加载失败"); }
  finally { loading.value = false; }
}
function openCreate(source?: ResumeVersion | null) {
  copySource.value = source || null;
  Object.assign(form, {
    name: source ? `${source.name} - 复制` : "",
    target_job: source?.target_job || "",
    selected_projects: source ? numberList(source.selected_projects) : profile.value?.projects.map((item) => item.id!) || [],
    selected_skills: source ? numberList(source.selected_skills) : profile.value?.skills.map((item) => item.id!) || [],
    selected_experiences: source
      ? { competitions: experienceList(source.selected_experiences, "competitions"), internships: experienceList(source.selected_experiences, "internships") }
      : { competitions: profile.value?.competitions.map((item) => item.id!) || [], internships: profile.value?.internships.map((item) => item.id!) || [] },
  });
  dialog.value = true;
}
async function createVersion() {
  if (!form.name.trim() || !form.target_job.trim()) return ElMessage.warning("请填写简历名称和目标岗位");
  saving.value = true;
  try {
    const created = await api.createResumeVersion({
      user_id: user.userId,
      ...form,
      ...(copySource.value ? {
        personal_summary: copySource.value.personal_summary,
        optimized_content: copySource.value.optimized_content,
        template: copySource.value.template,
      } : {}),
    });
    versions.value = await api.resumeVersions(user.userId!);
    selected.value = versions.value.find(item => item.id === created.id) || created;
    pending.value = null;
    copySource.value = null;
    dialog.value = false;
    ElMessage.success("新简历已创建并打开");
  }
  catch (error) { ElMessage.error(error instanceof Error ? error.message : "创建失败"); }
  finally { saving.value = false; }
}
async function saveSelection() {
  if (!selected.value) return;
  saving.value = true;
  try { selected.value = await api.updateResumeVersion(selected.value.id, { selected_projects: selected.value.selected_projects, selected_skills: selected.value.selected_skills, selected_experiences: selected.value.selected_experiences }); ElMessage.success("展示内容已保存"); }
  catch (error) { ElMessage.error(error instanceof Error ? error.message : "保存失败"); }
  finally { saving.value = false; }
}
async function optimize() {
  if (!selected.value) return;
  optimizing.value = true;
  try { const result = await api.resume({ user_id: user.userId, target_job: selected.value.target_job, selected_project_ids: selected.value.selected_projects, selected_skill_ids: selected.value.selected_skills }); pending.value = result.result as unknown as Record<string, unknown>; ElMessage.success("AI 建议已生成，请确认后再写入简历"); }
  catch (error) { ElMessage.error(error instanceof Error ? error.message : "AI 优化失败"); }
  finally { optimizing.value = false; }
}
async function acceptSuggestion() {
  if (!selected.value || !pending.value) return;
  saving.value = true;
  try { selected.value = await api.updateResumeVersion(selected.value.id, { optimized_content: pending.value, personal_summary: String(pending.value.personal_summary || "") }); pending.value = null; ElMessage.success("AI 建议已采纳并写入当前简历"); }
  catch (error) { ElMessage.error(error instanceof Error ? error.message : "采纳失败"); }
  finally { saving.value = false; }
}
onMounted(load);
</script>

<template>
  <div class="resume-version-page">
    <PageHeader title="我的简历" description="为不同求职方向准备多份简历，随时切换使用。"><el-button :icon="Refresh" @click="load">刷新</el-button><el-button type="primary" :icon="Plus" @click="openCreate">新建简历</el-button></PageHeader>
    <StateView :loading="loading" :error="''" @retry="load"><template #content>
      <div v-if="!versions.length" class="resume-empty"><el-icon><Edit /></el-icon><h3>还没有简历</h3><p>创建第一份简历，为你的求职方向准备一份专属版本。</p><el-button type="primary" :icon="Plus" @click="openCreate">创建第一份简历</el-button></div>
      <div v-else class="resume-version-layout">
        <aside class="version-list">
          <div class="version-list-heading"><div><b>我的简历</b><span>{{ versions.length }} 份</span></div><el-button text :icon="Plus" aria-label="新建简历" title="新建简历" @click="openCreate" /></div>
          <div v-for="item in versions" :key="item.id" class="version-item" :class="{ active: selected?.id === item.id }" @click="selected = item; pending = null"><b>{{ item.name }}</b><span>{{ item.target_job }}</span><small>更新于 {{ formatVersionTime(item.updated_at || item.created_at) }}</small></div>
        </aside>
        <main v-if="selected" class="version-editor">
          <section class="version-heading"><div><span class="resume-kicker">岗位简历</span><h2>{{ selected.name }}</h2><p>目标岗位：{{ selected.target_job }}</p></div><div class="version-actions"><el-button :icon="CopyDocument" @click="openCreate(selected)">复制一份</el-button><el-button :icon="Printer" @click="printResume">打印 / 导出 PDF</el-button><el-button :icon="MagicStick" type="primary" :loading="optimizing" @click="optimize">AI 优化</el-button><el-button :icon="Select" :loading="saving" @click="saveSelection">保存选择</el-button></div></section>
          <div class="resume-editor-grid">
            <div class="resume-selection-column">
              <div class="selection-caption"><b>选择要展示的内容</b><span>调整左侧内容，右侧会即时更新预览。</span></div>
              <div class="source-grid">
                <SectionPanel title="核心技能" subtitle="来自就业档案，可随档案更新"><el-checkbox-group v-model="selected.selected_skills" class="source-options"><el-checkbox v-for="item in selected.profile.skills" :key="item.id" :value="item.id">{{ item.name }}<small>{{ item.proficiency }}</small></el-checkbox></el-checkbox-group><el-empty v-if="!selected.profile.skills.length" description="请先在就业档案中添加技能" /></SectionPanel>
                <SectionPanel title="项目经历" subtitle="选择最能证明岗位能力的项目"><el-checkbox-group v-model="selected.selected_projects" class="source-options"><el-checkbox v-for="item in selected.profile.projects" :key="item.id" :value="item.id">{{ item.name }}<small>{{ item.role }}</small></el-checkbox></el-checkbox-group><el-empty v-if="!selected.profile.projects.length" description="请先在就业档案中添加项目" /></SectionPanel>
                <SectionPanel title="实习与竞赛" subtitle="按岗位需要组合展示"><el-checkbox-group v-model="selected.selected_experiences.internships" class="source-options"><el-checkbox v-for="item in selected.profile.internships" :key="item.id" :value="item.id">{{ item.company }}<small>{{ item.position }}</small></el-checkbox></el-checkbox-group><el-checkbox-group v-model="selected.selected_experiences.competitions" class="source-options"><el-checkbox v-for="item in selected.profile.competitions" :key="item.id" :value="item.id">{{ item.name }}<small>{{ item.award }}</small></el-checkbox></el-checkbox-group><el-empty v-if="!selected.profile.internships.length && !selected.profile.competitions.length" description="暂无可展示经历" /></SectionPanel>
              </div>
            </div>
            <div class="resume-preview-column">
              <div class="resume-preview-label"><b>简历预览</b><span>这是当前版本的打印效果</span></div>
              <article class="resume-paper">
                <header class="resume-paper-header">
                  <div><h1>{{ selected.profile.name || "你的姓名" }}</h1><h2>{{ selected.target_job }}</h2></div>
                  <div class="resume-contact"><span v-if="selected.profile.phone">{{ selected.profile.phone }}</span><span v-if="selected.profile.email">{{ selected.profile.email }}</span><span>{{ selected.profile.school }} · {{ selected.profile.major }}</span></div>
                </header>
                <section v-if="selected.profile.bio || selected.personal_summary" class="paper-section"><h3>个人简介</h3><p>{{ selected.personal_summary || selected.profile.bio }}</p></section>
                <section v-if="selectedSkills.length" class="paper-section"><h3>核心技能</h3><div class="paper-skill-list"><span v-for="item in selectedSkills" :key="item.id"><b>{{ item.name }}</b><small>{{ item.proficiency }}</small></span></div></section>
                <section v-if="selectedProjects.length" class="paper-section"><h3>项目经历</h3><article v-for="item in selectedProjects" :key="item.id" class="paper-entry"><div class="paper-entry-heading"><div><b>{{ item.name }}</b><span>{{ item.role }}</span></div><small>{{ formatDateRange(item.start_date, item.end_date) }}</small></div><div class="paper-tags"><span v-for="tag in item.tech_stack" :key="tag">{{ tag }}</span></div><p>{{ projectDescription(item.name, item.description) }}</p></article></section>
                <section v-if="selectedInternships.length" class="paper-section"><h3>实习经历</h3><article v-for="item in selectedInternships" :key="item.id" class="paper-entry"><div class="paper-entry-heading"><div><b>{{ item.company }}</b><span>{{ item.position }}</span></div><small>{{ formatDateRange(item.start_date, item.end_date) }}</small></div><div class="paper-tags"><span v-for="tag in item.tech_stack" :key="tag">{{ tag }}</span></div><p>{{ item.description }}</p></article></section>
                <section v-if="selectedCompetitions.length" class="paper-section"><h3>竞赛与获奖</h3><article v-for="item in selectedCompetitions" :key="item.id" class="paper-entry"><div class="paper-entry-heading"><div><b>{{ item.name }}</b><span>{{ item.level }} · {{ item.award }}</span></div><small>{{ item.competition_date || "" }}</small></div><p v-if="item.description">{{ item.description }}</p></article></section>
                <section class="paper-section"><h3>教育背景</h3><article class="paper-entry"><div class="paper-entry-heading"><div><b>{{ selected.profile.school }}</b><span>{{ selected.profile.major }} · {{ selected.profile.grade }}</span></div></div></article></section>
                <div v-if="!selectedSkills.length && !selectedProjects.length && !selectedInternships.length && !selectedCompetitions.length" class="paper-empty">请在左侧选择要展示的档案内容</div>
              </article>
            </div>
          </div>
          <section v-if="selected.optimized_content && Object.keys(selected.optimized_content).length" class="accepted-panel"><div><b>已采纳的 AI 表达</b><span>只优化你已选择的内容，不会凭空增加经历。</span></div><el-tag type="success">已写入当前版本</el-tag><p>{{ String(selected.optimized_content.personal_summary || selected.personal_summary || "暂无个人简介") }}</p></section>
          <section v-if="pending" class="pending-panel"><div><b>AI 建议，等待你的确认</b><span>建议不会自动覆盖简历内容。</span></div><div class="pending-content"><p>{{ String(pending.personal_summary || "AI 已完成岗位针对性建议，请检查项目表达和技能关键词。") }}</p><div class="tag-row"><el-tag v-for="item in (pending.overall_suggestions as string[] || [])" :key="item" type="warning">{{ item }}</el-tag></div></div><div class="pending-actions"><el-button @click="pending = null">暂不采纳</el-button><el-button type="primary" :icon="Check" :loading="saving" @click="acceptSuggestion">采纳并写入简历</el-button></div></section>
        </main>
      </div>
    </template></StateView>
    <el-dialog v-model="dialog" title="新建简历" width="min(760px, 92vw)"><el-form label-position="top"><el-form-item label="简历名称"><el-input v-model="form.name" placeholder="例如：Java 后端开发工程师简历" /></el-form-item><el-form-item label="目标岗位"><el-input v-model="form.target_job" placeholder="例如：Java 后端开发工程师" /></el-form-item><el-alert title="先选好这份简历要展示的经历，创建后还可以继续调整。" type="info" :closable="false" /><div class="create-source-grid"><div><b>项目</b><el-checkbox-group v-model="form.selected_projects"><el-checkbox v-for="item in profile?.projects" :key="item.id" :value="item.id">{{ item.name }}</el-checkbox></el-checkbox-group></div><div><b>技能</b><el-checkbox-group v-model="form.selected_skills"><el-checkbox v-for="item in profile?.skills" :key="item.id" :value="item.id">{{ item.name }}</el-checkbox></el-checkbox-group></div><div><b>实习经历</b><el-checkbox-group v-model="form.selected_experiences.internships"><el-checkbox v-for="item in profile?.internships" :key="item.id" :value="item.id">{{ item.company }} · {{ item.position }}</el-checkbox></el-checkbox-group></div><div><b>竞赛与获奖</b><el-checkbox-group v-model="form.selected_experiences.competitions"><el-checkbox v-for="item in profile?.competitions" :key="item.id" :value="item.id">{{ item.name }}</el-checkbox></el-checkbox-group></div></div></el-form><template #footer><el-button @click="dialog = false">取消</el-button><el-button type="primary" :loading="saving" @click="createVersion">创建简历</el-button></template></el-dialog>
  </div>
</template>

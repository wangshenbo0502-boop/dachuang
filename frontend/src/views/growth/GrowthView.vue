<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Check, Edit, MagicStick, Plus, Reading, VideoPlay } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useUserStore } from "@/stores/user";
import { err, fmt } from "@/utils/format";
import type { GrowthResponse, GrowthTask } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";
import SectionPanel from "@/components/common/SectionPanel.vue";

const user = useUserStore();
const router = useRouter();
const target = ref("");
const result = ref<GrowthResponse | null>(null);
const tasks = ref<GrowthTask[]>([]);
const loading = ref(false);
const running = ref(false);
const saving = ref(false);
const error = ref("");
const tab = ref("tasks");
const filter = ref("all");
const dialog = ref(false);
const editing = ref<GrowthTask | null>(null);
const form = reactive({ title: "", evidence: "", feedback: "", status: "doing" as GrowthTask["status"] });
const done = computed(() => tasks.value.filter(task => task.status === "done"));
const progress = computed(() => tasks.value.length ? Math.round(done.value.length / tasks.value.length * 100) : 0);
const visible = computed(() => tasks.value.filter(task => filter.value === "all" || task.status === filter.value));
const evidenceCount = computed(() => done.value.filter(task => task.evidence.trim()).length);
const weekly = computed(() => done.value.filter(task => task.completed_at && Date.now() - new Date(task.completed_at).getTime() < 7 * 86400000).length);
const labels = { todo: "未开始", doing: "进行中", done: "已完成" };

async function load() {
  loading.value = true; error.value = "";
  const [taskResult, history] = await Promise.allSettled([api.growthTasks(), api.growths(user.userId!)]);
  if (taskResult.status === "fulfilled") tasks.value = taskResult.value;
  else error.value = err(taskResult.reason);
  if (history.status === "fulfilled" && history.value[0]) {
    try { result.value = await api.growthDetail(history.value[0].id); target.value = result.value.target_job; }
    catch (e) { error.value = err(e); }
  } else if (history.status === "rejected") error.value = err(history.reason);
  loading.value = false;
}
async function run() {
  if (!target.value.trim()) return ElMessage.warning("请填写目标 IT 岗位");
  running.value = true;
  try { result.value = await api.growth({ user_id: user.userId, target_job: target.value }); tab.value = "plan"; ElMessage.success("规划已生成"); }
  catch (e) { ElMessage.error(err(e)); }
  finally { running.value = false; }
}
async function addTask(title: string) {
  try {
    const task = await api.addGrowthTask({ title: title.slice(0, 500), target_job: result.value?.target_job || target.value, resource_query: title.slice(0, 500) });
    upsert(task); ElMessage.success("已加入任务");
  } catch (e) { ElMessage.error(err(e)); }
}
function upsert(task: GrowthTask) { tasks.value = [task, ...tasks.value.filter(item => item.id !== task.id)]; }
async function start(task: GrowthTask) {
  try { upsert(await api.updateGrowthTask(task.id, { status: "doing" })); }
  catch (e) { ElMessage.error(err(e)); }
}
function edit(task: GrowthTask | null, complete = false) {
  editing.value = task;
  Object.assign(form, { title: task?.title || "", evidence: task?.evidence || "", feedback: task?.feedback || "", status: complete ? "done" : task?.status || "todo" });
  dialog.value = true;
}
async function save() {
  if (!form.title.trim()) return ElMessage.warning("请填写任务名称");
  if (form.status === "done" && !form.evidence.trim()) return ElMessage.warning("请记录完成产物或学习复盘");
  saving.value = true;
  try {
    const task = editing.value || await api.addGrowthTask({ title: form.title, target_job: target.value, resource_query: form.title });
    upsert(await api.updateGrowthTask(task.id, { status: form.status, feedback: form.feedback, evidence: form.evidence }));
    dialog.value = false; ElMessage.success(form.status === "done" ? "完成记录和证据已保存" : "任务已保存");
  } catch (e) { ElMessage.error(err(e)); }
  finally { saving.value = false; }
}
function openResource(query: string) { router.push({ path: "/resources", query: { query } }); }
onMounted(load);
</script>

<template>
  <div class="growth-page" v-loading="loading">
    <PageHeader title="IT 技术成长规划">
      <el-input v-model="target" placeholder="目标 IT 岗位" class="target-input" maxlength="100" />
      <el-button type="primary" :icon="MagicStick" :loading="running" @click="run">{{ result ? "重新规划" : "生成规划" }}</el-button>
      <el-button :icon="Plus" @click="edit(null)">新建任务</el-button>
    </PageHeader>
    <el-alert v-if="error" :title="error" type="warning" :closable="false"><el-button text @click="load">重试</el-button></el-alert>
    <section class="growth-statistics">
      <div><span>任务完成度</span><strong>{{ progress }}%</strong><el-progress :percentage="progress" :show-text="false" /></div>
      <div><span>本周完成</span><strong>{{ weekly }}</strong><small>过去 7 天</small></div>
      <div><span>完成证据</span><strong>{{ evidenceCount }}</strong><small>用户提交，待验证</small></div>
      <div><span>进行中的任务</span><strong>{{ tasks.filter(task => task.status === "doing").length }}</strong><small>{{ done.length }} / {{ tasks.length }} 已完成</small></div>
    </section>
    <el-tabs v-model="tab">
      <el-tab-pane label="我的成长任务" name="tasks">
        <div class="resource-toolbar"><el-radio-group v-model="filter"><el-radio-button value="all">全部</el-radio-button><el-radio-button value="todo">未开始</el-radio-button><el-radio-button value="doing">进行中</el-radio-button><el-radio-button value="done">成长记录</el-radio-button></el-radio-group></div>
        <el-empty v-if="!visible.length" description="暂无任务" />
        <div class="task-list">
          <article v-for="task in visible" :key="task.id" class="task-row">
            <div><el-tag :type="task.status === 'done' ? 'success' : task.status === 'doing' ? 'warning' : 'info'">{{ labels[task.status] }}</el-tag><h3>{{ task.title }}</h3><small>{{ task.target_job || "自主学习" }} · {{ fmt(task.updated_at) }}</small><p v-if="task.evidence"><b>完成产物：</b>{{ task.evidence }}</p><p v-if="task.feedback"><b>复盘：</b>{{ task.feedback }}</p></div>
            <div class="resource-actions"><el-button v-if="task.status === 'todo'" :icon="VideoPlay" @click="start(task)">开始</el-button><el-button v-if="task.status !== 'done'" type="primary" :icon="Check" @click="edit(task, true)">提交完成</el-button><el-button text :icon="Edit" @click="edit(task)">反馈</el-button><el-button text :icon="Reading" @click="openResource(task.resource_query || task.title)">学习资源</el-button></div>
          </article>
        </div>
        <div v-if="done.length" class="growth-next-step"><p>已累计 {{ evidenceCount }} 条完成证据。能力与岗位覆盖不会仅因勾选任务自动提高。</p><el-button @click="router.push('/profile')">补充项目事实</el-button><el-button @click="router.push('/jobs')">重新匹配岗位</el-button></div>
      </el-tab-pane>
      <el-tab-pane label="阶段规划" name="plan">
        <el-empty v-if="!result" description="暂无阶段规划" />
        <template v-else>
          <div class="growth-head"><div><span>目标岗位</span><h2>{{ result.target_job }}</h2><p>{{ result.result.current_situation }}</p><small>{{ result.is_mock ? "演示规划" : "AI 建议，需结合实际调整" }} · {{ result.result.expected_timeline }}</small></div></div>
          <div class="growth-layout">
            <SectionPanel title="阶段学习路线"><section v-for="(stage, index) in result.result.learning_roadmap" :key="index" class="growth-stage"><h3>{{ stage.stage }}</h3><p>{{ stage.focus }}</p><div v-for="(task, taskIndex) in stage.tasks" :key="taskIndex" class="plan-task"><span>{{ task }}</span><el-button text :icon="Plus" @click="addTask(task)">加入任务</el-button></div><p class="muted">里程碑：{{ stage.milestone }}</p></section></SectionPanel>
            <div><SectionPanel title="能力缺口"><article v-for="gap in result.result.ability_gaps" :key="gap.skill" class="growth-stage"><h4>{{ gap.skill }} <el-tag size="small" type="warning">{{ gap.importance }}</el-tag></h4><p>{{ gap.description }}</p><el-button text :icon="Reading" @click="openResource(gap.skill)">学习资料</el-button><el-button text :icon="Plus" @click="addTask(`完成 ${gap.skill} 实践并补充成果`)">加入任务</el-button></article></SectionPanel><SectionPanel title="推荐资源"><div v-for="resource in result.result.recommended_resources" :key="resource" class="plan-task"><button class="text-link" @click="openResource(resource)">{{ resource }}</button><el-button text :icon="Plus" title="加入任务" aria-label="加入任务" @click="addTask(resource)" /></div></SectionPanel></div>
          </div>
        </template>
      </el-tab-pane>
      <el-tab-pane label="面试与项目实践" name="practice">
        <el-empty v-if="!result" description="生成规划后获取针对性练习" />
        <template v-else><SectionPanel title="技术面试练习"><div v-for="tip in result.result.interview_prep_tips" :key="tip" class="plan-task"><button class="text-link" @click="openResource(tip)">{{ tip }}</button><el-button :icon="Plus" text @click="addTask(`面试练习：${tip}`)">加入练习</el-button></div></SectionPanel><SectionPanel title="推荐实战"><article v-for="project in result.result.recommended_projects" :key="project.name" class="growth-stage"><h3>{{ project.name }}</h3><p>{{ project.description }}</p><div class="tag-row"><el-tag v-for="tech in project.tech_stack" :key="tech">{{ tech }}</el-tag></div><el-button text :icon="Reading" @click="openResource(project.name)">项目资料</el-button><el-button text :icon="Plus" @click="addTask(`项目实践：${project.name}`)">加入任务</el-button></article></SectionPanel></template>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="dialog" :title="editing ? '任务反馈与完成证据' : '新建成长任务'" width="min(640px, 94vw)">
      <el-form label-position="top"><el-form-item label="任务"><el-input v-model="form.title" :disabled="!!editing" maxlength="500" /></el-form-item><el-form-item label="状态"><el-radio-group v-model="form.status"><el-radio-button value="todo">未开始</el-radio-button><el-radio-button value="doing">进行中</el-radio-button><el-radio-button value="done">已完成</el-radio-button></el-radio-group></el-form-item><el-form-item label="完成产物或学习复盘"><el-input v-model="form.evidence" type="textarea" :rows="4" maxlength="3000" placeholder="项目链接、练习结果、面试回答或具体学到的内容" /></el-form-item><el-form-item label="耗时、困难与下一步"><el-input v-model="form.feedback" type="textarea" :rows="3" maxlength="3000" /></el-form-item></el-form>
      <template #footer><el-button @click="dialog = false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存记录</el-button></template>
    </el-dialog>
  </div>
</template>

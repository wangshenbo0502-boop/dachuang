<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, MagicStick, Promotion } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { api } from "@/api";
import { useProfileStore } from "@/stores/profile";
import { useUserStore } from "@/stores/user";
import { err, text } from "@/utils/format";
import type { JobDetail, MatchedJob } from "@/types/api";
import StateView from "@/components/common/StateView.vue";
import SectionPanel from "@/components/common/SectionPanel.vue";
import BarChart from "@/components/charts/BarChart.vue";

const route = useRoute();
const router = useRouter();
const user = useUserStore();
const profiles = useProfileStore();
const job = ref<JobDetail | null>(null);
const match = ref<MatchedJob | null>(null);
const loading = ref(true);
const matching = ref(false);
const submitting = ref(false);
const error = ref("");
const bossUrl = ref("");

async function load() {
  loading.value = true;
  try { job.value = await api.job(String(route.params.id)); }
  catch (e) { error.value = err(e); }
  finally { loading.value = false; }
}

async function prepareApplication() {
  if (!job.value) return;
  if (!bossUrl.value.trim()) {
    error.value = "请先粘贴该岗位的 BOSS 直聘详情页链接";
    return;
  }
  submitting.value = true;
  try {
    await profiles.load(user.userId!);
    const skills = profiles.profile?.skills.slice(0, 3).map(item => item.name).join("、") || "相关技术方向";
    const greeting = `您好，我是${profiles.profile?.name || "一名求职者"}，正在关注贵司的${job.value.title}岗位。结合我在${skills}方面的学习与项目实践，希望有机会进一步交流。`;
    const resumeVersionId = Number(route.query.resume_version_id);
    const created = await api.createApplication({
      job_id: job.value.job_id,
      job_title: job.value.title,
      boss_url: bossUrl.value,
      greeting,
      ...(Number.isInteger(resumeVersionId) && resumeVersionId > 0 ? { resume_version_id: resumeVersionId } : {}),
    });
    const automation = await api.startApplicationAutomation(created.id);
    router.push({ path: "/applications", query: { application: created.id } });
    ElMessage.success(automation.message);
  } catch (e) { error.value = err(e); }
  finally { submitting.value = false; }
}

async function runMatch() {
  matching.value = true;
  try {
    await profiles.load(user.userId!);
    const result = await api.match({ skills: profiles.profile!.skills.map(item => item.name), top_k: 20, user_id: user.userId });
    match.value = result.matches.find(item => item.job_id === job.value?.job_id) || null;
    if (!match.value) error.value = "该岗位未进入本次匹配结果，请补充相关技能后重试";
  } catch (e) { error.value = err(e); }
  finally { matching.value = false; }
}

onMounted(load);
</script>

<template>
  <div>
    <div class="detail-back"><el-button :icon="ArrowLeft" text @click="router.back()">返回岗位列表</el-button></div>
    <StateView :loading="loading" :error="error && !job ? error : ''" :empty="!job" @retry="load">
      <template #content>
        <div class="job-detail-head">
          <div><el-tag>{{ job?.category }}</el-tag><h2>{{ job?.title }}</h2><div class="tag-row"><el-tag v-for="tag in job?.tags" :key="tag" type="info" effect="plain">{{ tag }}</el-tag></div></div>
          <div class="job-detail-actions"><el-input v-model="bossUrl" class="boss-url-input" placeholder="粘贴 BOSS 岗位链接" clearable /><el-button type="primary" :icon="Promotion" :loading="submitting" @click="prepareApplication">一键投递</el-button><el-button type="primary" :icon="MagicStick" :loading="matching" @click="runMatch">分析我的匹配度</el-button></div>
        </div>
        <div class="detail-layout">
          <SectionPanel title="岗位说明"><div class="markdown-text">{{ text(job?.content) }}</div></SectionPanel>
          <aside>
            <SectionPanel v-if="match" title="我的匹配情况">
              <div class="score-large">{{ match.match_score }}<small>%</small></div>
              <BarChart :labels="['综合匹配度']" :values="[match.match_score]" />
              <h4>已掌握技能</h4><div class="tag-row"><el-tag v-for="item in match.matched_skills" :key="item" type="success">{{ item }}</el-tag></div>
              <h4>待提升技能</h4><div class="tag-row"><el-tag v-for="item in match.missing_skills" :key="item" type="warning">{{ item }}</el-tag></div>
              <p v-if="match.match_reason" class="callout">{{ match.match_reason }}</p>
            </SectionPanel>
            <SectionPanel v-else title="我的匹配情况"><StateView empty empty-text="尚未进行匹配"><el-button type="primary" plain @click="runMatch">立即分析</el-button></StateView></SectionPanel>
          </aside>
        </div>
      </template>
    </StateView>
  </div>
</template>

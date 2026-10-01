<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { MagicStick, Refresh } from "@element-plus/icons-vue";
import { api } from "@/api";
import { err, fmt } from "@/utils/format";
import { useUserStore } from "@/stores/user";
import type { AnalysisResponse } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";
import StateView from "@/components/common/StateView.vue";
import SectionPanel from "@/components/common/SectionPanel.vue";
import RadarChart from "@/components/charts/RadarChart.vue";
import MarketContextPanel from "@/components/common/MarketContextPanel.vue";
const user = useUserStore();
const result = ref<AnalysisResponse | null>(null);
const loading = ref(true);
const running = ref(false);
const error = ref("");
const target = ref("");
const marketTarget = ref("");
const dimensionNames: Record<string, string> = { programming_foundation: "编程基础", framework_usage: "框架应用", database_skill: "数据库能力", project_experience: "项目经验", engineering_practice: "工程实践" };
const labels = computed(() => Object.keys(result.value?.result.skill_assessment || {}).map(key => dimensionNames[key] || key));
const values = computed(() => Object.values(result.value?.result.skill_assessment || {}));
async function load() {
  loading.value = true; error.value = "";
  try {
    const history = await api.analyses(user.userId!);
    if (history[0]) {
      result.value = await api.analysisDetail(history[0].id);
      target.value = result.value.target_job;
      marketTarget.value = result.value.target_job || result.value.result.technical_direction;
    }
  } catch (e) { error.value = err(e); }
  finally { loading.value = false; }
}
async function run() {
  running.value = true;
  try {
    result.value = await api.analysis({ user_id: user.userId, target_job: target.value || undefined });
    marketTarget.value = result.value.target_job || result.value.result.technical_direction;
    ElMessage.success("IT 就业画像已更新");
  } catch (e) { ElMessage.error(err(e)); }
  finally { running.value = false; }
}
onMounted(load);
</script>
<template>
  <div>
    <PageHeader title="IT 就业画像"><el-input v-model="target" placeholder="目标 IT 岗位" clearable class="target-input" /><el-button :icon="Refresh" @click="marketTarget = target">查看企业需求</el-button><el-button type="primary" :icon="MagicStick" :loading="running" @click="run">{{ result ? "重新分析" : "开始分析" }}</el-button></PageHeader>
    <StateView :loading="loading" :error="error" :empty="!result" empty-text="暂无个人画像" @retry="load"><template #content>
      <div class="analysis-hero"><div><span>模型评估</span><strong>{{ result?.result.comprehensive_score }}</strong><small>/ 100</small></div><div><el-tag effect="plain">{{ result?.result.current_level }}</el-tag><h3>{{ result?.result.technical_direction }}</h3><p>{{ result?.result.profile_summary }}</p><span class="record-time">{{ fmt(result?.created_at) }} · {{ result?.is_mock ? "演示数据" : "AI 判断，非招聘结论" }}</span></div></div>
      <div class="two-column"><SectionPanel title="能力维度"><RadarChart :labels="labels" :values="values" /></SectionPanel><SectionPanel title="推荐 IT 方向"><div class="direction-list"><div v-for="direction in result?.result.recommended_directions" :key="direction.job_title"><button class="text-link" @click="target = direction.job_title; marketTarget = direction.job_title">{{ direction.job_title }}</button><el-progress :percentage="direction.match_rate" :stroke-width="8" style="width: 140px" /></div></div></SectionPanel></div>
      <div class="two-column"><SectionPanel title="模型判断：主要优势"><ul class="result-list success"><li v-for="value in result?.result.core_advantages" :key="value">{{ value }}</li></ul></SectionPanel><SectionPanel title="模型判断：待提升能力"><ul class="result-list warning"><li v-for="value in result?.result.areas_to_improve" :key="value">{{ value }}</li></ul></SectionPanel></div>
    </template></StateView>
    <MarketContextPanel :target="marketTarget" />
  </div>
</template>

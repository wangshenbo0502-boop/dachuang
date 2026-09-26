<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
  ArrowRight,
  Briefcase,
  CollectionTag,
  DataAnalysis,
  DocumentChecked,
  FolderOpened,
  MagicStick,
} from "@element-plus/icons-vue";
import { api } from "@/api";
import { useUserStore } from "@/stores/user";
import { useProfileStore } from "@/stores/profile";
import type { AnalysisResponse, GrowthResponse } from "@/types/api";
import { err } from "@/utils/format";
import PageHeader from "@/components/common/PageHeader.vue";
import StatCard from "@/components/common/StatCard.vue";
import StateView from "@/components/common/StateView.vue";
import SectionPanel from "@/components/common/SectionPanel.vue";
import RadarChart from "@/components/charts/RadarChart.vue";

const router = useRouter();
const user = useUserStore();
const profiles = useProfileStore();
const analysis = ref<AnalysisResponse | null>(null);
const growth = ref<GrowthResponse | null>(null);
const loading = ref(true);
const error = ref("");
const profile = computed(() => profiles.profile);
const radar = computed(() => analysis.value ? Object.values(analysis.value.result.skill_assessment) : []);
const labels = ["编程基础", "框架应用", "数据库", "工程实践", "项目经验"];
const actions = [
  ["/coach?mode=profile", "AI 完善档案", MagicStick],
  ["/analysis", "生成就业画像", MagicStick],
  ["/jobs", "查看岗位推荐", Briefcase],
] as const;

async function load() {
  loading.value = true;
  error.value = "";
  try {
    await profiles.load(user.userId!, true);
    const [analyses, growths] = await Promise.all([api.analyses(user.userId!), api.growths(user.userId!)]);
    if (analyses[0]) analysis.value = await api.analysisDetail(analyses[0].id);
    if (growths[0]) growth.value = await api.growthDetail(growths[0].id);
  } catch (e) {
    error.value = err(e);
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <PageHeader title="你的就业工作台" description="从完善档案开始，逐步完成画像、岗位匹配与简历准备。" />
    <StateView :loading="loading" :error="error" @retry="load">
      <template #content>
        <section class="dashboard-welcome">
          <div class="welcome-copy">
            <span class="welcome-label">下一步建议</span>
            <h2>你好，{{ user.user?.name || "同学" }}</h2>
            <p>先和 AI 求职助手聊聊你的经历与目标。整理好的内容会先进入草稿，确认后再写入档案。</p>
            <div class="welcome-actions">
              <el-button type="primary" @click="router.push('/coach?mode=profile')">开始完善档案</el-button>
              <el-button @click="router.push('/coach')">直接咨询求职问题</el-button>
            </div>
          </div>
          <div class="welcome-progress">
            <el-progress type="dashboard" :percentage="profiles.completeness || 0" :width="118" :stroke-width="9" color="#176b5b" />
            <div><b>档案完整度</b><span>持续补充经历，让分析更贴合你的真实能力</span></div>
          </div>
        </section>

        <div class="stats-grid">
          <StatCard label="综合竞争力" :value="analysis?.result.comprehensive_score ?? null" unit="分" :icon="DataAnalysis" tone="blue" />
          <StatCard label="档案完整度" :value="profiles.completeness" unit="%" :icon="DocumentChecked" tone="green" />
          <StatCard label="掌握技能" :value="profile?.skills.length ?? 0" unit="项" :icon="CollectionTag" tone="cyan" />
          <StatCard label="项目经历" :value="profile?.projects.length ?? 0" unit="项" :icon="FolderOpened" tone="orange" />
        </div>

        <div class="workflow-grid">
          <button v-for="[path, label, icon] in actions" :key="path" @click="router.push(path)">
            <el-icon><component :is="icon" /></el-icon><span>{{ label }}</span><el-icon class="arrow"><ArrowRight /></el-icon>
          </button>
        </div>

        <div class="two-column">
          <SectionPanel title="AI就业能力画像" subtitle="最近一次画像分析">
            <StateView :empty="!analysis" empty-text="尚未生成就业画像">
              <template #hint>与 AI 对话补充档案后发起分析，即可查看能力雷达图。</template>
              <el-button type="primary" @click="router.push('/analysis')">立即分析</el-button>
              <template #content><RadarChart :labels="labels" :values="radar" /></template>
            </StateView>
          </SectionPanel>
          <SectionPanel title="推荐就业方向" subtitle="根据最近一次画像分析生成">
            <StateView :empty="!analysis?.result.recommended_directions.length" empty-text="暂无推荐方向">
              <template #content><div class="direction-list"><div v-for="item in analysis?.result.recommended_directions" :key="item.job_title"><div><b>{{ item.job_title }}</b><span>与当前能力画像匹配</span></div><el-progress type="circle" :width="58" :stroke-width="6" :percentage="item.match_rate" /></div></div></template>
            </StateView>
          </SectionPanel>
        </div>

        <div class="two-column dashboard-bottom-grid">
          <SectionPanel title="AI就业建议">
            <StateView :empty="!analysis" empty-text="暂无分析建议">
              <template #content><p class="summary-text">{{ analysis?.result.profile_summary }}</p><div class="advice-columns"><div><b>核心优势</b><ul><li v-for="item in analysis?.result.core_advantages" :key="item">{{ item }}</li></ul></div><div><b>当前短板</b><ul><li v-for="item in analysis?.result.areas_to_improve" :key="item">{{ item }}</li></ul></div></div></template>
            </StateView>
          </SectionPanel>
          <SectionPanel title="当前成长规划">
            <StateView :empty="!growth" empty-text="尚未生成成长规划">
              <el-button type="primary" plain @click="router.push('/growth')">生成规划</el-button>
              <template #content><div class="growth-summary"><el-tag>{{ growth?.result.expected_timeline }}</el-tag><p>{{ growth?.result.current_situation }}</p><el-steps direction="vertical" :active="0" :space="58"><el-step v-for="stage in growth?.result.learning_roadmap.slice(0, 3)" :key="stage.stage" :title="stage.stage" :description="stage.focus" /></el-steps></div></template>
            </StateView>
          </SectionPanel>
        </div>
      </template>
    </StateView>
  </div>
</template>

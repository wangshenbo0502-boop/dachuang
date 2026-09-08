<!--
  文件名称：Home.vue
  文件作用：首页 —— hero 区 + 系统状态 + 四大功能入口。
-->
<template>
  <div class="page home-page">
    <!-- Hero -->
    <section class="hero">
      <p v-reveal class="section-kicker">AI-Powered Career Navigator</p>
      <h1 v-reveal="'80ms'" class="hero-title">
        AI 就业竞争力<br /><span class="hero-accent">分析助手</span>
      </h1>
      <p v-reveal="'160ms'" class="hero-sub">
        面向计算机专业大学生，用大模型评估你的技术水平、匹配目标岗位、优化简历并规划成长路线。
      </p>
      <div v-reveal="'240ms'" class="hero-actions">
        <router-link to="/profile" class="btn btn-primary">开始画像分析</router-link>
        <router-link to="/job-match" class="btn btn-ghost">探索岗位</router-link>
      </div>

      <div v-reveal="'320ms'" class="status-strip glass">
        <span class="status-item">
          <span class="dot" :class="health ? 'ok' : 'err'"></span>
          服务状态
          <b>{{ health ? health.status : '检测中…' }}</b>
        </span>
        <span class="status-item">
          <span class="dot" :class="isLive ? 'live' : 'mock'"></span>
          AI 模式
          <b>{{ aiModeLabel }}</b>
        </span>
        <span class="status-item">
          <span class="dot ok"></span>
          已接入模块
          <b>{{ moduleCount }} 个</b>
        </span>
      </div>
    </section>

    <!-- 功能入口 -->
    <section class="features">
      <h2 v-reveal class="section-title">核心<span class="accent">能力</span></h2>
      <p v-reveal class="section-sub">四项 AI 驱动的求职能力，覆盖从评估到规划的全链路。</p>

      <div class="grid-cards">
        <router-link
          v-for="(f, i) in features"
          :key="f.path"
          v-reveal="`${i * 80}ms`"
          :to="f.path"
          class="feature-card glass card-glow"
        >
          <span class="feature-index">{{ String(i + 1).padStart(2, "0") }}</span>
          <h3 class="feature-title">{{ f.title }}</h3>
          <p class="feature-desc">{{ f.desc }}</p>
          <span class="feature-cta">进入 →</span>
        </router-link>
      </div>
    </section>

    <!-- 快速开始 -->
    <section v-reveal class="quickstart glass">
      <div>
        <h3 class="section-title">三步<span class="accent">上手</span></h3>
      </div>
      <ol class="steps">
        <li>在「就业画像」填写并保存你的基本资料与学习经历</li>
        <li>一键生成画像，AI 输出技术能力评估与改进方向</li>
        <li>去「岗位匹配」「简历优化」「成长规划」继续深挖</li>
      </ol>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { getHealth } from "@/api/system";
import type { HealthData } from "@/api/types";

const health = ref<HealthData | null>(null);

const isLive = computed(() => health.value?.ai_mode === "live");
const aiModeLabel = computed(() =>
  health.value ? (health.value.ai_mode === "live" ? "DeepSeek" : "Mock 演示") : "…"
);
const moduleCount = computed(() => health.value?.modules.length ?? 0);

const features = [
  { path: "/profile", title: "就业画像", desc: "基于你的资料生成技术能力评估、竞争力评分与改进方向。" },
  { path: "/job-match", title: "岗位匹配", desc: "技能与岗位需求智能比对，输出匹配度与差距清单。" },
  { path: "/resume", title: "简历优化", desc: "项目与技能描述专项改写，提升简历竞争力。" },
  { path: "/growth", title: "成长规划", desc: "个性化学习路线、阶段目标与推荐资源。" },
];

onMounted(async () => {
  try {
    const res = await getHealth();
    health.value = res.data;
  } catch {
    health.value = null;
  }
});
</script>

<style scoped>
.home-page {
  padding-top: 130px;
}
.hero {
  text-align: center;
  padding: 20px 0 60px;
}
.hero-title {
  font-size: clamp(40px, 8vw, 76px);
  font-weight: 800;
  line-height: 1.08;
  letter-spacing: 1px;
  margin-bottom: 22px;
}
.hero-accent {
  background: var(--grad-text);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  filter: drop-shadow(0 0 24px rgba(91, 124, 255, 0.35));
}
.hero-sub {
  max-width: 620px;
  margin: 0 auto 30px;
  color: var(--text-1);
  font-size: 16px;
}
.hero-actions {
  display: flex;
  gap: 14px;
  justify-content: center;
  margin-bottom: 40px;
}

.status-strip {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 14px 32px;
  justify-content: center;
  padding: 14px 28px;
  border-radius: 999px;
}
.status-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-1);
}
.status-item b {
  color: var(--text-0);
  font-weight: 600;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.dot.ok {
  background: var(--green);
  box-shadow: 0 0 10px var(--green);
}
.dot.live {
  background: var(--cyan);
  box-shadow: 0 0 10px var(--cyan);
}
.dot.mock {
  background: var(--amber);
  box-shadow: 0 0 10px var(--amber);
}
.dot.err {
  background: var(--red);
  box-shadow: 0 0 10px var(--red);
}

.features {
  padding: 40px 0;
}
.feature-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 26px 24px;
  min-height: 180px;
  overflow: hidden;
}
.feature-index {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--cyan);
  letter-spacing: 2px;
}
.feature-title {
  font-size: 20px;
  font-weight: 700;
}
.feature-desc {
  color: var(--text-1);
  font-size: 14px;
  line-height: 1.7;
  flex: 1;
}
.feature-cta {
  font-size: 13px;
  color: var(--violet);
  transition: transform 0.25s;
}
.feature-card:hover .feature-cta {
  transform: translateX(6px);
}

.quickstart {
  margin-top: 30px;
  padding: 32px 34px;
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr 2fr;
}
.steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
  color: var(--text-1);
  font-size: 14px;
  padding-left: 22px;
}
@media (max-width: 860px) {
  .quickstart {
    grid-template-columns: 1fr;
  }
}
</style>
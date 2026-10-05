<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Lock, Opportunity, ChatDotRound, TrendCharts, User, Suitcase, Document, Tickets } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import { err } from "@/utils/format";
import { resolveAuthRole, safeInternalRedirect } from "@/utils/authSession";
import type { AccountRole } from "@/utils/authSession";
const route = useRoute(), router = useRouter(), auth = useAuthStore();
const form = reactive({ email: "", password: "" });
const error = ref("");
const role = computed(() => resolveAuthRole(route.query.role, route.query.redirect));
const authQuery = computed(() => ({ ...route.query, role: role.value }));
const roles = [
  { value: "student" as const, label: "求职者登录", description: "找岗位 · 提升求职能力", icon: User },
  { value: "recruiter" as const, label: "招聘者登录", description: "发岗位 · 寻找合适人才", icon: Suitcase },
];
const content = computed(() => role.value === "recruiter" ? {
  headline: "让合适的人才", highlight: "遇见合适的岗位",
  description: "发布招聘岗位，查看求职者简历并跟进投递，让每一次招聘沟通都有清晰的进展。",
  title: "招聘者登录", note: "使用招聘者账号，进入企业招聘工作台",
  button: "登录招聘工作台", signup: "注册招聘者账号", icon: Suitcase,
  pillars: [
    { title: "发布招聘岗位", description: "管理岗位草稿、发布与下架", icon: Opportunity },
    { title: "查看求职简历", description: "围绕项目经历与技能了解候选人", icon: Document },
    { title: "跟进招聘进度", description: "处理投递状态，提供站内反馈", icon: Tickets },
  ],
} : {
  headline: "让技术能力", highlight: "变成求职竞争力",
  description: "从技术栈、项目经历到岗位匹配，帮助你把开发能力转化为更清晰、更可信的求职材料。",
  title: "求职者登录", note: "使用求职者账号，进入 IT 求职成长工作台",
  button: "登录求职工作台", signup: "注册求职者账号", icon: User,
  pillars: [
    { title: "看懂技术岗位", description: "拆解岗位需要的技术能力", icon: Opportunity },
    { title: "优化开发者简历", description: "用项目证据呈现技术成果", icon: ChatDotRound },
    { title: "规划技术成长", description: "围绕目标岗位补齐技能缺口", icon: TrendCharts },
  ],
});
watch(role, () => { error.value = ""; });
async function selectRole(value: AccountRole) {
  if (auth.loading || value === role.value) return;
  await router.replace({ path: "/login", query: { ...route.query, role: value } });
}
async function submit() {
  if (auth.loading) return;
  error.value = "";
  try {
    await auth.login(form.email, form.password, role.value);
    ElMessage.success("登录成功");
    await router.replace(safeInternalRedirect(route.query.redirect, auth.account?.role));
  } catch (e) { error.value = err(e); }
}
</script>
<template>
  <main class="login-page role-login-page">
    <section class="login-brand">
      <div class="login-brand-content">
        <div class="institution-label"><span class="brand-mark">IT</span> IT 求职成长系统</div>
        <h1>{{ content.headline }}<br /><span>{{ content.highlight }}</span></h1>
        <p>{{ content.description }}</p>
        <div class="login-pillars">
          <div v-for="pillar in content.pillars" :key="pillar.title"><span class="pillar-icon"><el-icon><component :is="pillar.icon" /></el-icon></span><span><b>{{ pillar.title }}</b><small>{{ pillar.description }}</small></span></div>
        </div>
        <div class="brand-footnote">CAREER INTELLIGENCE · BUILT AROUND YOU</div>
      </div>
    </section>
    <section class="login-area">
      <div class="login-form">
        <div class="login-logo"><el-icon><component :is="content.icon" /></el-icon></div>
        <div class="login-eyebrow">欢迎回来</div>
        <h2>{{ content.title }}</h2>
        <p class="muted">{{ content.note }}</p>
        <div class="login-role-options" role="group" aria-label="选择登录身份">
          <button v-for="entry in roles" :key="entry.value" type="button" class="login-role-option"
            :class="{ 'is-selected': role === entry.value }" :aria-label="entry.label" :aria-pressed="role === entry.value"
            :disabled="auth.loading" @click="selectRole(entry.value)">
            <span class="login-role-heading"><el-icon aria-hidden="true"><component :is="entry.icon" /></el-icon><b>{{ entry.label }}</b></span>
            <small>{{ entry.description }}</small>
          </button>
        </div>
        <el-alert v-if="error" :title="error" type="error" :closable="false" show-icon />
        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="QQ 邮箱"><el-input v-model="form.email" size="large" type="email" placeholder="123456789@qq.com" autocomplete="username" /></el-form-item>
          <el-form-item label="密码"><el-input v-model="form.password" size="large" type="password" show-password autocomplete="current-password" /></el-form-item>
          <div class="login-options"><span class="secure-note"><el-icon><Lock /></el-icon> QQ 邮箱安全登录</span><router-link :to="{ path: '/forgot-password', query: authQuery }">忘记密码？</router-link></div>
          <el-button native-type="submit" type="primary" size="large" :loading="auth.loading" class="full-button">{{ content.button }}</el-button>
        </el-form>
        <p class="login-note">还没有账号？<router-link :to="{ path: '/register', query: authQuery }">{{ content.signup }}</router-link></p>
      </div>
      <div class="login-copyright">IT 求职成长系统 <span>·</span> 让技术能力更好地被看见</div>
    </section>
  </main>
</template>

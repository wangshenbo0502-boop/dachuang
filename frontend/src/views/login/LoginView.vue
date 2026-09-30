<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Lock, Opportunity, ChatDotRound, TrendCharts } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import { err } from "@/utils/format";
import { safeInternalRedirect } from "@/utils/authSession";
const route = useRoute(), router = useRouter(), auth = useAuthStore();
const form = reactive({ email: "", password: "" });
const error = ref("");
async function submit() {
  error.value = "";
  try {
    await auth.login(form.email, form.password);
    ElMessage.success("登录成功");
    await router.replace(safeInternalRedirect(route.query.redirect));
  } catch (e) { error.value = err(e); }
}
</script>
<template>
  <main class="login-page">
    <section class="login-brand">
      <div class="login-brand-content">
        <div class="institution-label"><span class="brand-mark">IT</span> IT 求职成长系统</div>
        <h1>让技术能力<br /><span>变成求职竞争力</span></h1>
        <p>从技术栈、项目经历到岗位匹配，帮助你把开发能力转化为更清晰、更可信的求职材料。</p>
        <div class="login-pillars">
          <div><span class="pillar-icon"><el-icon><Opportunity /></el-icon></span><span><b>看懂技术岗位</b><small>拆解岗位需要的技术能力</small></span></div>
          <div><span class="pillar-icon"><el-icon><ChatDotRound /></el-icon></span><span><b>优化开发者简历</b><small>用项目证据呈现技术成果</small></span></div>
          <div><span class="pillar-icon"><el-icon><TrendCharts /></el-icon></span><span><b>规划技术成长</b><small>围绕目标岗位补齐技能缺口</small></span></div>
        </div>
        <div class="brand-footnote">CAREER INTELLIGENCE · BUILT AROUND YOU</div>
      </div>
    </section>
    <section class="login-area">
      <div class="login-form">
        <div class="login-logo"><el-icon><Opportunity /></el-icon></div>
        <div class="login-eyebrow">欢迎回来</div>
        <h2>进入 IT 求职工作台</h2>
        <p class="muted">使用已验证的 QQ 邮箱登录</p>
        <el-alert v-if="error" :title="error" type="error" :closable="false" show-icon />
        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="QQ 邮箱"><el-input v-model="form.email" size="large" type="email" placeholder="123456789@qq.com" autocomplete="username" /></el-form-item>
          <el-form-item label="密码"><el-input v-model="form.password" size="large" type="password" show-password autocomplete="current-password" @keyup.enter="submit" /></el-form-item>
          <div class="login-options"><span class="secure-note"><el-icon><Lock /></el-icon> 安全登录</span><router-link to="/forgot-password">忘记密码？</router-link></div>
          <el-button native-type="submit" type="primary" size="large" :loading="auth.loading" class="full-button">登录</el-button>
        </el-form>
        <p class="login-note">还没有账号？<router-link :to="{path:'/register',query:route.query}">使用 QQ 邮箱注册</router-link></p>
      </div>
      <div class="login-copyright">IT 求职成长系统 <span>·</span> 让技术能力更好地被看见</div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Opportunity, ChatDotRound, TrendCharts } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useAuthStore } from "@/stores/auth";
import { err } from "@/utils/format";
import { safeInternalRedirect } from "@/utils/authSession";
const route = useRoute(), router = useRouter(), auth = useAuthStore();
const form = reactive({ email: "", code: "", password: "", confirm_password: "", name: "" });
const error = ref(""), sending = ref(false), cooldown = ref(0);
async function sendCode() {
  error.value = "";
  sending.value = true;
  try {
    await api.authSendCode(form.email);
    ElMessage.success("验证码已发送，请检查邮箱");
    cooldown.value = 60;
    const timer = window.setInterval(() => { cooldown.value--; if (cooldown.value <= 0) window.clearInterval(timer); }, 1000);
  } catch (e) { error.value = err(e); }
  finally { sending.value = false; }
}
async function submit() {
  error.value = "";
  if (form.password !== form.confirm_password) { error.value = "两次输入的密码不一致"; return; }
  try {
    await auth.register({ ...form, name: form.name || undefined });
    ElMessage.success("注册成功");
    await router.replace(safeInternalRedirect(route.query.redirect));
  } catch (e) { error.value = err(e); }
}
</script>
<template>
  <main class="login-page">
    <section class="login-brand">
      <div class="login-brand-content">
        <div class="institution-label"><span class="brand-mark">AI</span> 大学生就业成长平台</div>
        <h1>让每一步成长<br /><span>都更有方向</span></h1>
        <p>创建账号后即可开始完善就业档案，探索适合自己的职业方向。</p>
        <div class="login-pillars">
          <div><span class="pillar-icon"><el-icon><Opportunity /></el-icon></span><span><b>看见优势</b><small>建立清晰的能力画像</small></span></div>
          <div><span class="pillar-icon"><el-icon><ChatDotRound /></el-icon></span><span><b>AI 陪伴</b><small>对话补全档案与简历</small></span></div>
          <div><span class="pillar-icon"><el-icon><TrendCharts /></el-icon></span><span><b>持续成长</b><small>获得可执行的提升建议</small></span></div>
        </div>
      </div>
    </section>
    <section class="login-area">
      <div class="login-form">
        <div class="login-logo"><el-icon><Opportunity /></el-icon></div>
        <div class="login-eyebrow">创建账号</div>
        <h2>开启你的成长空间</h2>
        <p class="muted">注册只需 QQ 邮箱和密码，就业档案稍后完善</p>
        <el-alert v-if="error" :title="error" type="error" :closable="false" show-icon />
        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="QQ 邮箱"><el-input v-model="form.email" size="large" type="email" placeholder="123456789@qq.com" autocomplete="email" /></el-form-item>
          <el-form-item label="验证码">
            <div style="display:flex;gap:8px;width:100%"><el-input v-model="form.code" size="large" maxlength="6" inputmode="numeric" placeholder="6 位验证码" /><el-button size="large" :disabled="cooldown>0" :loading="sending" @click="sendCode">{{ cooldown>0 ? `${cooldown}s` : "获取验证码" }}</el-button></div>
          </el-form-item>
          <el-form-item label="姓名（可选）"><el-input v-model="form.name" size="large" maxlength="50" autocomplete="name" /></el-form-item>
          <el-form-item label="密码"><el-input v-model="form.password" size="large" type="password" show-password autocomplete="new-password" placeholder="至少 8 位" /></el-form-item>
          <el-form-item label="确认密码"><el-input v-model="form.confirm_password" size="large" type="password" show-password autocomplete="new-password" /></el-form-item>
          <el-button native-type="submit" type="primary" size="large" :loading="auth.loading" class="full-button">注册并进入</el-button>
        </el-form>
        <p class="login-note">已有账号？<router-link :to="{path:'/login',query:route.query}">返回登录</router-link></p>
      </div>
    </section>
  </main>
</template>

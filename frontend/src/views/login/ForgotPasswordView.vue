<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Opportunity } from "@element-plus/icons-vue";
import { api } from "@/api";
import { err } from "@/utils/format";
const router = useRouter();
const form = reactive({ email: "", code: "", password: "", confirm_password: "" });
const error = ref(""), sending = ref(false), saving = ref(false), cooldown = ref(0);
async function sendCode() {
  error.value = "";
  sending.value = true;
  try {
    await api.authSendCode(form.email, "RESET_PASSWORD");
    ElMessage.success("如邮箱已注册，验证码将发送至该邮箱");
    cooldown.value = 60;
    const timer = window.setInterval(() => { cooldown.value--; if (cooldown.value <= 0) window.clearInterval(timer); }, 1000);
  } catch (e) { error.value = err(e); }
  finally { sending.value = false; }
}
async function submit() {
  error.value = "";
  if (form.password !== form.confirm_password) { error.value = "两次输入的密码不一致"; return; }
  saving.value = true;
  try {
    await api.authResetPassword(form);
    ElMessage.success("密码已重置，请重新登录");
    await router.replace("/login");
  } catch (e) { error.value = err(e); }
  finally { saving.value = false; }
}
</script>
<template>
  <main class="login-page">
    <section class="login-brand">
      <div class="login-brand-content">
        <div class="institution-label"><span class="brand-mark">AI</span> 大学生就业成长平台</div>
        <h1>重新找回<br /><span>你的成长空间</span></h1>
        <p>通过已绑定的 QQ 邮箱验证码重置密码。</p>
      </div>
    </section>
    <section class="login-area">
      <div class="login-form">
        <div class="login-logo"><el-icon><Opportunity /></el-icon></div>
        <div class="login-eyebrow">账号安全</div>
        <h2>重置密码</h2>
        <p class="muted">验证码 5 分钟内有效</p>
        <el-alert v-if="error" :title="error" type="error" :closable="false" show-icon />
        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="QQ 邮箱"><el-input v-model="form.email" size="large" type="email" autocomplete="email" /></el-form-item>
          <el-form-item label="验证码"><div style="display:flex;gap:8px;width:100%"><el-input v-model="form.code" size="large" maxlength="6" inputmode="numeric" /><el-button size="large" :loading="sending" :disabled="cooldown>0" @click="sendCode">{{ cooldown>0 ? `${cooldown}s` : "获取验证码" }}</el-button></div></el-form-item>
          <el-form-item label="新密码"><el-input v-model="form.password" size="large" type="password" show-password autocomplete="new-password" placeholder="至少 8 位" /></el-form-item>
          <el-form-item label="确认新密码"><el-input v-model="form.confirm_password" size="large" type="password" show-password autocomplete="new-password" /></el-form-item>
          <el-button native-type="submit" type="primary" size="large" :loading="saving" class="full-button">重置密码</el-button>
        </el-form>
        <p class="login-note"><router-link to="/login">返回登录</router-link></p>
      </div>
    </section>
  </main>
</template>

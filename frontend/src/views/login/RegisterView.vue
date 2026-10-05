<script setup lang="ts">
import { onBeforeUnmount, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Opportunity } from "@element-plus/icons-vue";
import { api } from "@/api";
import { useAuthStore } from "@/stores/auth";
import { err } from "@/utils/format";
import { resolveAuthRole, safeInternalRedirect } from "@/utils/authSession";
const route = useRoute(), router = useRouter(), auth = useAuthStore();
const form = reactive({ email: "", code: "", password: "", confirm_password: "", name: "", role: resolveAuthRole(route.query.role, route.query.redirect), phone: "", birth_date: null as string | null });
const error = ref(""), sending = ref(false), cooldown = ref(0);
let timer: number | undefined;
onBeforeUnmount(() => window.clearInterval(timer));
function disabledBirthDate(value: Date) { return value.getTime() > Date.now() || value.getFullYear() < 1900; }
async function sendCode() {
  error.value = "";
  sending.value = true;
  try {
    await api.authSendCode(form.email);
    ElMessage.success("验证码已发送，请检查邮箱");
    cooldown.value = 60;
    timer = window.setInterval(() => { cooldown.value--; if (cooldown.value <= 0) window.clearInterval(timer); }, 1000);
  } catch (e) { error.value = err(e); }
  finally { sending.value = false; }
}
async function submit() {
  error.value = "";
  if (form.password !== form.confirm_password) { error.value = "两次输入的密码不一致"; return; }
  if (!/^1[3-9]\d{9}$/.test(form.phone)) { error.value = "请输入有效的 11 位手机号"; return; }
  if (!form.birth_date) { error.value = "请选择出生日期"; return; }
  try {
    await auth.register({ ...form, name: form.name || undefined });
    ElMessage.success("注册成功");
    await router.replace(safeInternalRedirect(route.query.redirect, auth.account?.role));
  } catch (e) { error.value = err(e); }
}
</script>
<template>
  <main class="login-page registration-page">
    <section class="login-area">
      <div class="login-form">
        <div class="registration-brand"><div class="login-logo"><el-icon><Opportunity /></el-icon></div><span>IT 求职成长系统</span></div>
        <h2>{{ form.role === 'recruiter' ? '创建招聘者账号' : '创建求职者账号' }}</h2><p v-if="form.role === 'recruiter'" class="muted">注册后完善企业资料，即可发布岗位并接收简历</p>
        <el-alert v-if="error" :title="error" type="error" :closable="false" show-icon />
        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="注册身份"><el-radio-group v-model="form.role" size="large"><el-radio-button value="student">求职者</el-radio-button><el-radio-button value="recruiter">招聘者</el-radio-button></el-radio-group></el-form-item>
          <el-form-item label="QQ 邮箱"><el-input v-model="form.email" size="large" type="email" placeholder="123456789@qq.com" autocomplete="email" /></el-form-item>
          <el-form-item label="验证码">
            <div style="display:flex;gap:8px;width:100%"><el-input v-model="form.code" size="large" maxlength="6" inputmode="numeric" placeholder="6 位验证码" /><el-button size="large" :disabled="cooldown>0" :loading="sending" @click="sendCode">{{ cooldown>0 ? `${cooldown}s` : "获取验证码" }}</el-button></div>
          </el-form-item>
          <el-form-item label="姓名（可选）"><el-input v-model="form.name" size="large" maxlength="50" autocomplete="name" /></el-form-item>
          <div class="register-fields">
            <el-form-item label="手机号"><el-input v-model="form.phone" size="large" maxlength="11" inputmode="tel" autocomplete="tel" placeholder="用于完善求职档案" /></el-form-item>
            <el-form-item label="出生日期"><el-date-picker v-model="form.birth_date" type="date" value-format="YYYY-MM-DD" size="large" :editable="false" :disabled-date="disabledBirthDate" placeholder="选择出生日期" style="width: 100%" /></el-form-item>
          </div>
          <div class="register-fields">
          <el-form-item label="密码"><el-input v-model="form.password" size="large" type="password" show-password autocomplete="new-password" placeholder="至少 8 位" /></el-form-item>
          <el-form-item label="确认密码"><el-input v-model="form.confirm_password" size="large" type="password" show-password autocomplete="new-password" /></el-form-item>
          </div>
          <el-button native-type="submit" type="primary" size="large" :loading="auth.loading" class="full-button">注册并进入</el-button>
        </el-form>
        <p class="login-note">已有账号？<router-link :to="{ path: '/login', query: { ...route.query, role: form.role } }">返回登录</router-link></p>
      </div>
    </section>
  </main>
</template>

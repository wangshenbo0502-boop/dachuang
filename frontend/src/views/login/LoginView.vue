<script setup lang="ts">
import{reactive,ref}from"vue";import{useRoute,useRouter}from"vue-router";import{ElMessage}from"element-plus";import{UserFilled,Lock,Opportunity,ChatDotRound,TrendCharts}from"@element-plus/icons-vue";import{useUserStore}from"@/stores/user";import{err}from"@/utils/format";
const router=useRouter(),route=useRoute(),store=useUserStore(),form=reactive({id:"",remember:true}),error=ref("");async function submit(){error.value="";const id=Number(form.id);if(!Number.isInteger(id)||id<1){error.value="请输入有效的学生档案编号";return}try{await store.login(id,form.remember);ElMessage.success("身份验证成功");router.replace(String(route.query.redirect||"/dashboard"))}catch(e){error.value=err(e)}}
</script>
<template>
  <main class="login-page">
    <section class="login-brand">
      <div class="login-brand-content">
        <div class="institution-label"><span class="brand-mark">AI</span> 大学生就业成长平台</div>
        <h1>让每一步成长<br /><span>都更有方向</span></h1>
        <p>从认识自己的能力开始，在 AI 陪伴下找到适合的职业方向，把每一次积累变成求职竞争力。</p>
        <div class="login-pillars">
          <div><span class="pillar-icon"><el-icon><Opportunity /></el-icon></span><span><b>看见优势</b><small>建立清晰的能力画像</small></span></div>
          <div><span class="pillar-icon"><el-icon><ChatDotRound /></el-icon></span><span><b>AI 陪伴</b><small>对话补全档案与简历</small></span></div>
          <div><span class="pillar-icon"><el-icon><TrendCharts /></el-icon></span><span><b>持续成长</b><small>获得可执行的提升建议</small></span></div>
        </div>
        <div class="brand-footnote">CAREER INTELLIGENCE · BUILT AROUND YOU</div>
      </div>
    </section>
    <section class="login-area">
      <div class="login-form">
        <div class="login-logo"><el-icon><Opportunity /></el-icon></div>
        <div class="login-eyebrow">欢迎回来</div>
        <h2>进入你的成长空间</h2>
        <p class="muted">输入学生档案编号，继续探索职业可能</p>
        <el-alert v-if="error" :title="error" type="error" :closable="false" show-icon />
        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="学生档案编号">
            <el-input v-model="form.id" size="large" placeholder="请输入档案编号" :prefix-icon="UserFilled" inputmode="numeric" autocomplete="username" @keyup.enter="submit" />
          </el-form-item>
          <div class="login-options"><el-checkbox v-model="form.remember">保持登录</el-checkbox><span class="secure-note"><el-icon><Lock /></el-icon> 安全连接</span></div>
          <el-button native-type="submit" type="primary" size="large" :loading="store.loading" class="full-button">继续</el-button>
        </el-form>
        <p class="login-note">使用已建立的学生档案编号登录。登录后，你的 AI 就业助手将为你整理能力与成长方向。</p>
      </div>
      <div class="login-copyright">AI 就业成长平台 <span>·</span> 让职业选择更清晰</div>
    </section>
  </main>
</template>

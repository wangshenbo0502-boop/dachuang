<!--
  文件名称：Footer.vue
  文件作用：底部信息栏。
-->
<template>
  <footer class="footer">
    <p>AI 就业竞争力分析助手 · 面向计算机专业大学生的智能求职平台</p>
    <p class="muted">数据与 AI 结果仅供参考 · 演示环境</p>
  </footer>
</template>

<script setup lang="ts"></script>

<style scoped>
.footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 30px 20px 40px;
  color: var(--text-2);
  font-size: 13px;
  border-top: 1px solid var(--border);
}
.footer .muted {
  margin-top: 6px;
  font-size: 12px;
  opacity: 0.75;
}
</style>
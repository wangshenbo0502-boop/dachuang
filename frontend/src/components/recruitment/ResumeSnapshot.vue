<script setup lang="ts">
import type { ResumeSnapshot } from '@/types/recruitment';
defineProps<{ resume: ResumeSnapshot }>();
</script>

<template>
  <article class="resume-snapshot">
    <h2>{{ resume.profile.name }}</h2>
    <p class="summary-text">{{ resume.profile.school }} · {{ resume.profile.major }} · {{ resume.profile.grade }}</p>
    <p class="summary-text">{{ resume.profile.email }}<span v-if="resume.profile.phone"> · {{ resume.profile.phone }}</span></p>
    <p class="muted">{{ resume.name }} · 求职方向：{{ resume.target_job }}</p>
    <section v-if="resume.personal_summary"><h3>个人概要</h3><p class="markdown-text">{{ resume.personal_summary }}</p></section>
    <section v-if="resume.profile.skills.length"><h3>技能</h3><div class="tag-row"><el-tag v-for="skill in resume.profile.skills" :key="skill.name" effect="plain">{{ skill.name }} · {{ skill.proficiency }}</el-tag></div><p v-for="skill in resume.profile.skills.filter(s => s.description)" :key="skill.name" class="summary-text">{{ skill.name }}：{{ skill.description }}</p></section>
    <section v-if="resume.profile.projects.length"><h3>项目经历</h3><div v-for="(item, index) in resume.profile.projects" :key="index" class="entry"><h4>{{ item.name }} · {{ item.role }}</h4><p class="muted">{{ item.start_date || '时间未填写' }} — {{ item.end_date || '时间未填写' }}</p><p class="markdown-text">{{ item.description }}</p><div class="tag-row"><el-tag v-for="tag in item.tech_stack" :key="tag" size="small" type="info">{{ tag }}</el-tag></div></div></section>
    <section v-if="resume.profile.internships.length"><h3>实习经历</h3><div v-for="(item, index) in resume.profile.internships" :key="index" class="entry"><h4>{{ item.company }} · {{ item.position }}</h4><p class="muted">{{ item.start_date || '时间未填写' }} — {{ item.end_date || '时间未填写' }}</p><p class="markdown-text">{{ item.description }}</p></div></section>
    <section v-if="resume.profile.competitions.length"><h3>竞赛经历</h3><div v-for="(item, index) in resume.profile.competitions" :key="index" class="entry"><h4>{{ item.name }} · {{ item.award }}</h4><p class="summary-text">{{ item.level }} · {{ item.competition_date || '时间未填写' }}</p><p class="markdown-text">{{ item.description }}</p></div></section>
    <p class="callout">这是投递时保存的简历内容。后续修改就业档案或简历，不会改变这份投递。</p>
  </article>
</template>

<style scoped>
.resume-snapshot { overflow-wrap: anywhere; }
section { margin-top: 22px; }
h3 { margin-bottom: 10px; }
.entry + .entry { margin-top: 16px; }
.tag-row { margin: 8px 0; }
</style>

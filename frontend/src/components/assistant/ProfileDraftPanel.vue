<script setup lang="ts">
import { computed } from "vue";
import { Check, EditPen } from "@element-plus/icons-vue";

const props = defineProps<{
  draft: Record<string, any>;
  loading: boolean;
  syncing: boolean;
}>();
const emit = defineEmits<{
  change: [];
  confirm: [];
}>();
const reviewInput = defineModel<string>("reviewInput", { required: true });

const fields = [
  ["name", "姓名"], ["school", "学校"], ["major", "专业"], ["grade", "年级"],
  ["target_city", "目标城市"], ["target_salary", "期望薪资"], ["bio", "个人优势"],
] as const;
const listFields = [
  ["skills", "技能"], ["projects", "项目"], ["competitions", "竞赛"], ["internships", "实习"],
] as const;
const hasDraft = computed(() => Object.values(props.draft).some(value =>
  Array.isArray(value) ? value.length > 0 : typeof value === "string" && value.trim(),
));
</script>

<template>
  <div class="assistant-draft-content">
    <div class="draft-heading">
      <div><span class="assistant-kicker">保存前确认</span><h2>AI 整理出的档案</h2></div>
      <el-tag effect="plain" type="success">待你确认</el-tag>
    </div>
    <p class="draft-hint">先和 AI 把信息聊清楚。这里的内容还没有写入档案，确认无误后再保存。</p>
    <div class="draft-content">
      <div v-for="[key, label] in fields" :key="key" v-show="draft[key]" class="draft-row">
        <span>{{ label }}</span><b>{{ draft[key] }}</b>
      </div>
      <div v-for="[key, label] in listFields" :key="key" v-show="draft[key]?.length" class="draft-section">
        <span>{{ label }} · {{ draft[key]?.length }} 项</span>
        <div class="draft-tags">
          <el-tag v-for="(item, index) in draft[key]" :key="index" size="small">
            {{ item.name || `${item.company || ""}${item.position ? ` · ${item.position}` : ""}` }}
          </el-tag>
        </div>
      </div>
      <el-empty v-if="!hasDraft" description="继续回答问题，整理出的内容会出现在这里" :image-size="68" />
    </div>
    <div class="draft-review">
      <el-input
        v-model="reviewInput"
        type="textarea"
        :rows="2"
        maxlength="1000"
        placeholder="需要调整内容时，可以直接告诉 AI，例如：我的角色是前端开发"
      />
      <el-button :icon="EditPen" plain :disabled="!reviewInput.trim()" :loading="loading" @click="emit('change')">
        让 AI 修正草稿
      </el-button>
    </div>
    <el-button
      type="primary"
      class="draft-confirm"
      :icon="Check"
      :loading="syncing"
      :disabled="!hasDraft || loading"
      @click="emit('confirm')"
    >
      确认并更新我的档案
    </el-button>
  </div>
</template>

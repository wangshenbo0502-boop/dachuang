<script setup lang="ts">
import { DocumentDelete, Warning } from "@element-plus/icons-vue";

interface Props {
  loading?: boolean;
  error?: string;
  empty?: boolean;
  emptyText?: string;
}

defineProps<Props>();
defineEmits<{ retry: [] }>();
</script>

<template>
  <div v-if="loading" class="state-view">
    <el-skeleton :rows="5" animated />
  </div>
  <div v-else-if="error" class="state-view centered">
    <el-icon class="state-icon error"><Warning /></el-icon>
    <b>数据加载失败</b>
    <p>{{ error }}</p>
    <el-button type="primary" plain @click="$emit('retry')">重新加载</el-button>
  </div>
  <div v-else-if="empty" class="state-view centered">
    <el-icon class="state-icon"><DocumentDelete /></el-icon>
    <b>{{ emptyText || "暂无数据" }}</b>
    <p><slot name="hint" /></p>
    <slot />
  </div>
  <slot v-else name="content" />
</template>

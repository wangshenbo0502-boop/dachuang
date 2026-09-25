<script setup lang="ts">
import type { Component } from "vue";

interface Props {
  label: string;
  value: string | number | null;
  unit?: string;
  icon: Component;
  tone?: string;
}

defineProps<Props>();
</script>

<template>
  <div class="stat-card">
    <div class="stat-icon" :class="tone">
      <el-icon><component :is="icon" /></el-icon>
    </div>
    <div>
      <span>{{ label }}</span>
      <strong>
        {{ value ?? "暂无数据" }}<small v-if="value !== null && unit">{{ unit }}</small>
      </strong>
      <i class="stat-accent" />
    </div>
  </div>
</template>

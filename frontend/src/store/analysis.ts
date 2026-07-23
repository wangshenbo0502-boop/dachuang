/**
 * 文件名称：analysis.ts
 * 文件作用：就业画像分析状态管理 Store，管理分析报告数据和加载状态。
 * 当前阶段仅定义 Store 框架，具体状态和操作后续实现。
 */

import { defineStore } from "pinia";
import { ref } from "vue";

export const useAnalysisStore = defineStore("analysis", () => {
  // TODO: 分析报告数据
  const report = ref<object | null>(null);
  const isLoading = ref(false);

  // TODO: 触发分析
  // function startAnalysis() {}

  // TODO: 获取报告
  // function fetchReport() {}

  return {
    report,
    isLoading,
  };
});

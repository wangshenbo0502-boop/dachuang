<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps<{ items: { label: string; count: number }[] }>();
const element = ref<HTMLElement>();
let chart: echarts.ECharts | undefined;
let observer: ResizeObserver | undefined;

function draw() {
  chart?.setOption({
    grid: { left: 8, right: 36, top: 6, bottom: 6, containLabel: true },
    xAxis: { type: "value", minInterval: 1, splitLine: { lineStyle: { color: "#eaf0ed" } }, axisLabel: { color: "#87938e" } },
    yAxis: { type: "category", inverse: true, data: props.items.map(item => item.label), axisTick: { show: false }, axisLine: { show: false }, axisLabel: { color: "#3d514b", fontSize: 12 } },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: (params: any) => `${params[0].name}：${params[0].value} 个知识库岗位` },
    series: [{ type: "bar", data: props.items.map(item => item.count), barMaxWidth: 17, itemStyle: { color: "#287a69", borderRadius: [0, 3, 3, 0] }, label: { show: true, position: "right", color: "#3d514b" } }],
  });
}

onMounted(() => { chart = echarts.init(element.value!); draw(); observer = new ResizeObserver(() => chart?.resize()); observer.observe(element.value!); });
watch(() => props.items, draw, { deep: true });
onBeforeUnmount(() => { observer?.disconnect(); chart?.dispose(); });
</script>

<template><div ref="element" class="career-coverage-chart" role="img" :aria-label="`知识库岗位方向分布：${items.map(item => `${item.label}${item.count}个`).join('，')}`" /></template>

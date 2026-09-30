<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";
const props = withDefaults(defineProps<{ labels: string[]; values: number[]; unit?: string }>(), { unit: "%" });
const emit = defineEmits<{ select: [index: number] }>();
const el = ref<HTMLElement>();
let chart: echarts.ECharts | undefined;
let observer: ResizeObserver | undefined;
function draw() {
  chart?.setOption({
    tooltip: { trigger: "axis" },
    grid: { left: 12, right: 35, top: 12, bottom: 12, containLabel: true },
    xAxis: { type: "value", max: props.unit === "%" ? 100 : undefined, minInterval: 1, splitLine: { lineStyle: { color: "#e5ece8" } } },
    yAxis: { type: "category", data: props.labels, axisLine: { show: false }, axisTick: { show: false } },
    series: [{ type: "bar", data: props.values, barWidth: 14, itemStyle: { color: "#158779", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right", formatter: `{c}${props.unit}` } }],
  });
}
onMounted(() => {
  chart = echarts.init(el.value!); draw();
  chart.on("click", event => emit("select", event.dataIndex));
  observer = new ResizeObserver(() => chart?.resize()); observer.observe(el.value!);
});
watch(() => [props.labels, props.values, props.unit], draw, { deep: true });
onBeforeUnmount(() => { observer?.disconnect(); chart?.dispose(); });
</script>
<template><div ref="el" class="chart-canvas compact" /></template>

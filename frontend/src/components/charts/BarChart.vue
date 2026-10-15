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
    animation: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    textStyle: { fontFamily: 'Microsoft YaHei UI, sans-serif', color: '#cbd6e3', fontSize: 12 },
    tooltip: { trigger: "axis", confine: true, backgroundColor: "#142333", borderColor: "#415b63", textStyle: { color: "#f2f4fa" } },
    grid: { left: 12, right: 35, top: 12, bottom: 12, containLabel: true },
    xAxis: { type: "value", max: props.unit === "%" ? 100 : undefined, minInterval: 1, axisLabel: { color: "#a3b1c5" }, splitLine: { lineStyle: { color: "#304654" } } },
    yAxis: { type: "category", data: props.labels, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: "#cbd6e3" } },
    series: [{ type: "bar", data: props.values, barWidth: 12, itemStyle: { color: "#83e5b2", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right", color: "#cbd6e3", formatter: `{c}${props.unit}` } }],
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

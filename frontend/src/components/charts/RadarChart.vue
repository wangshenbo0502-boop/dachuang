<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";
const props = defineProps<{ labels: string[]; values: number[]; compare?: number[] }>();
const emit = defineEmits<{ select: [index: number] }>();
const el = ref<HTMLElement>();
let chart: echarts.ECharts | undefined;
let observer: ResizeObserver | undefined;
function draw() {
  const series = [{ name: "当前记录", value: props.values }];
  if (props.compare) series.push({ name: "岗位要求", value: props.compare });
  chart?.setOption({
    animation: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    textStyle: { fontFamily: 'Microsoft YaHei UI, sans-serif', color: '#cbd6e3' },
    tooltip: { backgroundColor: "#142333", borderColor: "#415b63", textStyle: { color: "#f2f4fa" } }, color: ["#83e5b2", "#ebc780"], legend: { bottom: 0, textStyle: { fontSize: 12, color: '#a3b1c5' } },
    radar: { radius: "57%", center: ["50%", "45%"], triggerEvent: true, indicator: props.labels.map(name => ({ name, max: 100 })), splitNumber: 4, axisName: { color: "#cbd6e3" }, splitArea: { areaStyle: { color: ["#111b2a", "#152634"] } }, axisLine: { lineStyle: { color: "#3c5361" } }, splitLine: { lineStyle: { color: "#3c5361" } } },
    series: [{ type: "radar", data: series, symbolSize: 5, lineStyle: { width: 2 }, areaStyle: { opacity: 0.12 } }],
  }, true);
}
onMounted(() => {
  chart = echarts.init(el.value!); draw();
  chart.on("click", event => { const index = props.labels.indexOf(event.name); emit("select", index >= 0 ? index : 0); });
  observer = new ResizeObserver(() => chart?.resize()); observer.observe(el.value!);
});
watch(() => [props.labels, props.values, props.compare], draw, { deep: true });
onBeforeUnmount(() => { observer?.disconnect(); chart?.dispose(); });
</script>
<template><div ref="el" class="chart-canvas" /></template>

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
    tooltip: {}, color: ["#2563eb", "#158779"], legend: { bottom: 0 },
    radar: { radius: "57%", center: ["50%", "45%"], triggerEvent: true, indicator: props.labels.map(name => ({ name, max: 100 })), splitNumber: 4, axisName: { color: "#475569" }, splitArea: { areaStyle: { color: ["#fff", "#f8fafc"] } }, axisLine: { lineStyle: { color: "#dbe4ef" } }, splitLine: { lineStyle: { color: "#dbe4ef" } } },
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

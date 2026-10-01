<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps<{ items: { label: string; count: number }[]; selected: string }>();
const emit = defineEmits<{ select: [category: string] }>();
const element = ref<HTMLElement>();
let chart: echarts.ECharts | undefined;
let observer: ResizeObserver | undefined;
const total = computed(() => props.items.reduce((sum, item) => sum + item.count, 0));
const colors: Record<string, string> = {
  AI: "#226b57", "后端": "#437dc0", "前端": "#549ca2", "数据": "#8777b4",
  "测试": "#ba8650", "运维": "#697d99", "安全": "#a36883", "产品": "#ac7564",
  "移动端": "#619076", "运营": "#7d8763", "其他": "#697f85",
};
function color(label: string) { return colors[label] || "#697f85"; }
function draw() {
  chart?.setOption({
    animationDuration: 450,
    animationDurationUpdate: 250,
    tooltip: {
      confine: true, renderMode: "richText",
      formatter: (params: any) => {
        const item = props.items.find(item => item.label === params.name);
        return item ? `${item.label}方向\n${item.count} 个岗位样本 / 占收录样本 ${Math.round(item.count / total.value * 100)}%` : "";
      },
    },
    series: [{
      type: "treemap", left: 0, right: 0, top: 0, bottom: 0,
      roam: false, nodeClick: false, breadcrumb: { show: false },
      sort: "desc", squareRatio: 1.25,
      itemStyle: { borderColor: "#fff", borderWidth: 0, gapWidth: 4 },
      label: {
        show: true, position: "insideTopLeft", padding: [8, 8],
        color: "#fff", fontSize: 13, lineHeight: 22, overflow: "truncate",
        formatter: (params: any) => Number(params.value) / total.value < 0.06
          ? "" : `{title|${params.name}}\n{value|${params.value}}`,
        rich: {
          title: { fontSize: 14, fontWeight: 600, color: "#fff", lineHeight: 25 },
          value: { fontSize: 22, fontWeight: 600, color: "#fff", lineHeight: 28 },
        },
      },
      emphasis: { itemStyle: { borderColor: "#183f35", borderWidth: 2 }, label: { show: true } },
      data: props.items.map(item => ({
        name: item.label, value: item.count,
        itemStyle: {
          color: color(item.label),
          opacity: props.selected && props.selected !== item.label ? 0.4 : 1,
          borderColor: props.selected === item.label ? "#183f35" : "#fff",
          borderWidth: props.selected === item.label ? 3 : 0,
        },
      })),
    }],
  });
}
onMounted(() => {
  chart = echarts.init(element.value!);
  chart.on("click", params => {
    if (props.items.some(item => item.label === params.name)) emit("select", params.name);
  });
  draw();
  observer = new ResizeObserver(() => chart?.resize());
  observer.observe(element.value!);
});
watch(() => [props.items, props.selected], draw, { deep: true });
onBeforeUnmount(() => { observer?.disconnect(); chart?.dispose(); });
</script>

<template>
  <div class="direction-map">
    <div ref="element" class="direction-map-canvas" role="img" :aria-label="`岗位样本方向地图：${items.map(item => `${item.label}${item.count}个`).join('，')}`" />
    <div class="map-legend" role="group" aria-label="选择技术方向">
      <button v-for="item in items" :key="item.label" :aria-label="item.label" :aria-pressed="selected === item.label" :class="{ selected: selected === item.label }" @click="emit('select', item.label)">
        <i :style="{ background: color(item.label) }" /><span>{{ item.label }}</span><small>{{ item.count }}</small>
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.direction-map { min-width: 0; }
.direction-map-canvas { width: 100%; height: 240px; }
.map-legend {
  display: flex; flex-wrap: wrap; gap: 4px 8px; margin-top: 12px;
  button { display: flex; align-items: center; gap: 5px; border: 1px solid transparent; border-radius: 3px; padding: 3px 6px; background: transparent; color: #637071; font: inherit; font-size: 11px; line-height: 1.5; }
  button:hover, button.selected { color: #173e31; background: #eff5f1; border-color: #b7cdc0; }
  button:focus-visible { outline: 2px solid #155eef; outline-offset: 2px; }
  i { width: 7px; height: 7px; flex-shrink: 0; border-radius: 1px; }
  small { color: #697771; font-size: 10px; }
}
@media (max-width: 650px) { .direction-map-canvas { height: 232px; } }
</style>

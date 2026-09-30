<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { Search, Star, Plus, Hide, Link, Refresh } from "@element-plus/icons-vue";
import { api } from "@/api";
import { err, text } from "@/utils/format";
import { resourceDate, resourceKey, resourceTitle, resourceUrl } from "@/utils/resources";
import type { KnowledgeResult, ResourceEvent } from "@/types/api";
import PageHeader from "@/components/common/PageHeader.vue";
import StateView from "@/components/common/StateView.vue";

const route = useRoute();
const query = ref("");
const category = ref("");
const tab = ref("home");
const items = ref<KnowledgeResult[]>([]);
const homeItems = ref<KnowledgeResult[]>([]);
const events = ref<ResourceEvent[]>([]);
const keys = ref<Record<string, string>>({});
const selected = ref<KnowledgeResult | null>(null);
const loading = ref(false);
const error = ref("");
const sourceWarning = ref("");
const searchWarning = ref("");
const categories = [["jobs", "岗位知识"], ["skills", "技术教程"], ["market", "行业动态"], ["policies", "就业政策"], ["resume", "简历指导"], ["interview", "面试准备"]];
const subjects = ["前端开发", "Java 后端", "AI 应用开发", "数据工程", "测试开发", "云原生"];
let sequence = 0;
function identity(item: KnowledgeResult) { return resourceUrl(item) || String(item.document_id || item.doc_id || item.id || resourceTitle(item)); }
const visible = computed(() => {
  if (tab.value === "favorites") return events.value.filter(event => event.favorite && !event.hidden).map(event => event.resource);
  return (tab.value === "search" ? items.value : homeItems.value).filter(item => !eventOf(item)?.hidden);
});
function eventOf(item: KnowledgeResult) { return events.value.find(event => event.resource_key === keys.value[identity(item)]); }
function sourceOf(item: KnowledgeResult) { return String(item.metadata?.source_name || item.source || "项目知识库"); }
function categoryOf(item: KnowledgeResult) { return categories.find(([key]) => key === item.category)?.[1] || "技术知识"; }
async function indexItems(values: KnowledgeResult[]) {
  await Promise.all(values.map(async item => { keys.value[identity(item)] = await resourceKey(item); }));
  return values;
}
async function loadHome() {
  const current = ++sequence;
  tab.value = "home"; loading.value = true; error.value = "";
  try {
    const data = await api.resourceHome();
    const indexed = await indexItems(data.items);
    if (current !== sequence) return;
    homeItems.value = indexed;
    sourceWarning.value = data.unavailable_sources.length ? `部分官方来源暂不可达：${data.unavailable_sources.join("、")}` : "";
  } catch (e) { if (current === sequence) error.value = err(e); }
  finally { if (current === sequence) loading.value = false; }
}
async function search() {
  if (!query.value.trim()) return loadHome();
  const current = ++sequence;
  tab.value = "search"; loading.value = true; error.value = ""; searchWarning.value = "";
  try {
    const term = query.value.trim();
    const includeNews = !category.value || category.value === "market";
    const [knowledge, news] = await Promise.allSettled([
      api.knowledge({ query: term, category: category.value || undefined, top_k: 12 }),
      includeNews ? api.resourceHome() : Promise.resolve(null),
    ]);
    const words = term.toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const recent = news.status === "fulfilled" ? (news.value?.items || []).filter(item =>
      words.every(word => `${resourceTitle(item)} ${item.content}`.toLocaleLowerCase().includes(word))) : [];
    const results = [...recent, ...(knowledge.status === "fulfilled" ? knowledge.value.results : [])];
    const unique = [...new Map(results.map(item => [identity(item), item])).values()];
    const indexed = await indexItems(unique);
    if (current !== sequence) return;
    items.value = indexed;
    if (knowledge.status === "rejected") {
      if (indexed.length) searchWarning.value = "知识库暂不可用，当前仅展示匹配的近期官方动态。";
      else error.value = err(knowledge.reason);
    } else if (news.status === "rejected" || (news.status === "fulfilled" && news.value?.unavailable_sources.length)) {
      searchWarning.value = "部分官方动态暂不可用，知识库检索不受影响。";
    }
  } catch (e) { if (current === sequence) { items.value = []; error.value = err(e); } }
  finally { if (current === sequence) loading.value = false; }
}
async function updateEvent(item: KnowledgeResult, change: {favorite?:boolean; read?:boolean; hidden?:boolean}) {
  try {
    const key = keys.value[identity(item)] || await resourceKey(item);
    keys.value[identity(item)] = key;
    const response = await api.saveResourceEvent({ resource_key: key, resource: { ...item, content: item.content.slice(0, 10000) }, ...change });
    events.value = [...events.value.filter(event => event.resource_key !== key), response];
  } catch (e) { ElMessage.error(err(e)); }
}
async function open(item: KnowledgeResult) { selected.value = item; await updateEvent(item, { read: true }); }
async function addTask(item: KnowledgeResult) {
  try {
    await api.addGrowthTask({ title: `学习：${resourceTitle(item)}`.slice(0, 500), source_key: `resource:${await resourceKey(item)}`, resource_query: resourceTitle(item).slice(0, 500) });
    ElMessage.success("已加入成长任务");
  } catch (e) { ElMessage.error(err(e)); }
}
function quickSearch(value: string) { query.value = value; category.value = ""; search(); }
function showFavorites() { sequence++; loading.value = false; error.value = ""; tab.value = "favorites"; }
function changeTab(value: string | number | boolean | undefined) { value === "favorites" ? showFavorites() : value === "home" ? loadHome() : search(); }
async function routeSearch() {
  query.value = typeof route.query.query === "string" ? route.query.query : "";
  category.value = typeof route.query.category === "string" ? route.query.category : "";
  await (query.value ? search() : loadHome());
}
watch(() => [route.query.query, route.query.category], routeSearch);
onMounted(async () => {
  routeSearch();
  try {
    const saved = await api.resourceEvents();
    saved.forEach(event => { keys.value[identity(event.resource)] = event.resource_key; });
    events.value = saved;
  } catch (e) { ElMessage.error(err(e)); }
});
</script>

<template>
  <div class="resources-page">
    <PageHeader title="IT 就业资源中心"><el-button :icon="Refresh" @click="loadHome">刷新动态</el-button></PageHeader>
    <form class="resource-search" @submit.prevent="search">
      <el-input v-model="query" size="large" :prefix-icon="Search" placeholder="搜索技术栈、岗位或面试问题" clearable />
      <el-select v-model="category" size="large" clearable placeholder="全部分类"><el-option v-for="[key, label] in categories" :key="key" :value="key" :label="label" /></el-select>
      <el-button native-type="submit" type="primary" size="large" :icon="Search">搜索</el-button>
    </form>
    <div class="resource-toolbar">
      <el-radio-group :model-value="tab" @change="changeTab">
        <el-radio-button value="home">今日 IT 动态</el-radio-button><el-radio-button value="search">知识检索</el-radio-button><el-radio-button value="favorites">我的收藏</el-radio-button>
      </el-radio-group>
    </div>
    <div class="topic-links"><el-button v-for="subject in subjects" :key="subject" text @click="quickSearch(subject)">{{ subject }}</el-button></div>
    <p v-if="tab === 'home'" class="muted">官方来源 · 最近 30 天发布 · 按发布时间排序</p>
    <el-alert v-if="tab === 'home' && sourceWarning" :title="sourceWarning" type="warning" :closable="false" />
    <el-alert v-if="tab === 'search' && searchWarning" :title="searchWarning" type="warning" :closable="false" />
    <StateView :loading="loading" :error="error" :empty="!visible.length" :empty-text="tab === 'home' ? '暂无可核验的近期动态，可搜索技术知识或稍后重试' : tab === 'favorites' ? '暂无收藏' : '没有找到相关资料'" @retry="tab === 'home' ? loadHome() : search()">
      <template #content>
        <div class="resource-list">
          <article v-for="(item, index) in visible" :key="identity(item)">
            <div class="resource-index">{{ String(index + 1).padStart(2, "0") }}</div>
            <div class="resource-content">
              <div class="resource-meta"><el-tag size="small">{{ categoryOf(item) }}</el-tag><span>{{ resourceDate(item) }}</span><span>{{ sourceOf(item) }}</span><el-tag v-if="eventOf(item)?.read" type="info" size="small">已读</el-tag></div>
              <button class="resource-title" @click="open(item)">{{ resourceTitle(item) }}</button>
              <p>{{ text(item.content).slice(0, 280) }}</p>
              <small>{{ item.metadata?.recommendation || (tab === "search" ? `与“${query}”相关的知识库资料` : "官方技术更新") }}</small>
              <div class="resource-actions">
                <el-button text :icon="Star" :type="eventOf(item)?.favorite ? 'warning' : 'default'" @click="updateEvent(item, { favorite: !eventOf(item)?.favorite })">{{ eventOf(item)?.favorite ? "已收藏" : "收藏" }}</el-button>
                <el-button text :icon="Plus" @click="addTask(item)">加入成长任务</el-button>
                <el-button text :icon="Hide" @click="updateEvent(item, { hidden: true })">不相关</el-button>
                <el-button text :icon="Link" @click="open(item)">阅读全文</el-button>
              </div>
            </div>
          </article>
        </div>
      </template>
    </StateView>
    <el-drawer :model-value="!!selected" :title="selected ? resourceTitle(selected) : ''" size="min(720px, 94vw)" @close="selected = null">
      <template v-if="selected"><p class="muted">{{ sourceOf(selected) }} · {{ resourceDate(selected) }}</p><p class="resource-full-text">{{ text(selected.content) }}</p><a v-if="resourceUrl(selected)" :href="resourceUrl(selected)" target="_blank" rel="noopener noreferrer">查看原文</a><div class="resource-actions"><el-button type="primary" :icon="Plus" @click="addTask(selected)">加入成长任务</el-button></div></template>
    </el-drawer>
  </div>
</template>

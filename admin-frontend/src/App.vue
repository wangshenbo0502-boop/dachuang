<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api, setCsrfToken } from "./api";

type View = "overview" | "accounts" | "jobs" | "applications" | "commands";
const view = ref<View>("overview");
const loggedIn = ref(false);
const admin = ref<{ username: string; role: string } | null>(null);
const username = ref("admin");
const password = ref("");
const error = ref("");
const data = ref<any>(null);
const loading = ref(false);
const labels: Record<View, string> = { overview: "运行概览", accounts: "账号管理", jobs: "岗位治理", applications: "投递记录", commands: "命令中心" };
const title = computed(() => labels[view.value]);

async function loadMe() {
  try {
    const { data: result } = await api.get("/auth/me");
    admin.value = result.data.admin;
    setCsrfToken(result.data.csrf_token);
    loggedIn.value = true;
    await loadView();
  } catch { loggedIn.value = false; }
}
async function login() {
  error.value = "";
  try {
    const { data: result } = await api.post("/auth/login", { username: username.value, password: password.value });
    admin.value = result.data.admin;
    setCsrfToken(result.data.csrf_token);
    loggedIn.value = true;
    await loadView();
  } catch (e: any) { error.value = e?.response?.data?.message || "登录失败"; }
}
async function loadView() {
  loading.value = true;
  try {
    const { data: result } = await api.get(`/${view.value === "overview" ? "overview" : view.value}`);
    data.value = result.data;
  }
  catch (e: any) { error.value = e?.response?.data?.message || "数据加载失败"; }
  finally { loading.value = false; }
}
async function logout() { await api.post("/auth/logout"); loggedIn.value = false; admin.value = null; }
function selectView(next: View) { view.value = next; loadView(); }
onMounted(loadMe);
</script>

<template>
  <main v-if="!loggedIn" class="login">
    <section class="login-panel">
      <p class="eyebrow">DACHUANG CONTROL PLANE</p>
      <h1>管理员控制台</h1>
      <p class="muted">独立管理服务 · 业务数据只读/受控写入</p>
      <form @submit.prevent="login">
        <label>管理员账号<input v-model="username" autocomplete="username" /></label>
        <label>密码<input v-model="password" type="password" autocomplete="current-password" /></label>
        <button>登录</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </section>
  </main>
  <main v-else class="shell">
    <aside>
      <div class="brand">大创项目<span>ADMIN</span></div>
      <nav>
        <button v-for="(label, key) in labels" :key="key" :class="{ active: view === key }" @click="selectView(key as View)">{{ label }}</button>
      </nav>
      <div class="account"><strong>{{ admin?.username }}</strong><small>{{ admin?.role }}</small><button class="quiet" @click="logout">退出登录</button></div>
    </aside>
    <section class="content">
      <header><div><p class="eyebrow">CONTROL CENTER</p><h1>{{ title }}</h1></div><button class="refresh" @click="loadView">刷新</button></header>
      <p v-if="error" class="error">{{ error }}</p>
      <div v-if="loading" class="empty">正在加载...</div>
      <template v-else-if="view === 'overview' && data">
        <div class="metrics"><article><small>账号总数</small><b>{{ data.accounts }}</b></article><article><small>启用账号</small><b>{{ data.active_accounts }}</b></article><article><small>岗位总数</small><b>{{ data.jobs }}</b></article><article><small>投递总数</small><b>{{ data.applications }}</b></article></div>
      </template>
      <template v-else-if="data">
        <div class="table-wrap">
          <table><thead><tr><th v-for="key in Object.keys((data.items || data)[0] || {})" :key="key">{{ key }}</th></tr></thead>
            <tbody><tr v-for="(row, index) in (data.items || data)" :key="row.id || row.command_id || index"><td v-for="key in Object.keys(row)" :key="key">{{ typeof row[key] === 'object' ? JSON.stringify(row[key]) : row[key] }}</td></tr></tbody>
          </table>
          <div v-if="!(data.items || data).length" class="empty">暂无数据</div>
        </div>
      </template>
    </section>
  </main>
</template>

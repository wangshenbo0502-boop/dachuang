<!--
  文件名称：NavBar.vue
  文件作用：顶部导航栏，玻璃拟态 + 霓虹高亮当前路由。
-->
<template>
  <nav class="navbar">
    <router-link to="/" class="brand">
      <span class="brand-mark"></span>
      <span class="brand-text">AI<span class="brand-accent">职鉴</span></span>
    </router-link>

    <div class="links">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-link"
        :class="{ active: isActive(item.path) }"
      >
        {{ item.label }}
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";

const navItems = [
  { path: "/", label: "首页" },
  { path: "/profile", label: "就业画像" },
  { path: "/job-match", label: "岗位匹配" },
  { path: "/resume", label: "简历优化" },
  { path: "/growth", label: "成长规划" },
];

const route = useRoute();
function isActive(path: string) {
  if (path === "/") return route.path === "/";
  return route.path.startsWith(path);
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 10px 16px 10px 20px;
  border-radius: 999px;
  background: rgba(10, 13, 28, 0.6);
  border: 1px solid var(--border);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.4);
}

.brand {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
}
.brand-mark {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  background: var(--grad-neon);
  box-shadow: var(--glow-cyan);
}
.brand-accent {
  background: var(--grad-text);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.links {
  display: flex;
  gap: 4px;
}
.nav-link {
  padding: 7px 14px;
  border-radius: 999px;
  font-size: 14px;
  color: var(--text-1);
  transition: color 0.25s, background 0.25s, box-shadow 0.25s;
}
.nav-link:hover {
  color: var(--text-0);
}
.nav-link.active {
  color: var(--text-0);
  background: linear-gradient(
    120deg,
    rgba(34, 211, 238, 0.16),
    rgba(168, 85, 247, 0.16)
  );
  box-shadow: inset 0 0 0 1px var(--border-strong), var(--glow-cyan);
}

@media (max-width: 720px) {
  .navbar {
    gap: 10px;
    padding: 8px 10px;
  }
  .nav-link {
    padding: 6px 9px;
    font-size: 13px;
  }
  .brand-text {
    display: none;
  }
}
</style>
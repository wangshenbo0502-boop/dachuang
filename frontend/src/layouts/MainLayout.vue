<script setup lang="ts">
import AppSidebar from "@/components/layout/AppSidebar.vue";
import AppHeader from "@/components/layout/AppHeader.vue";
import { useAppStore } from "@/stores/app";
import { useRoute } from "vue-router";

const app = useAppStore();
const route = useRoute();
</script>

<template>
  <div class="app-shell" :class="{ collapsed: app.sidebarCollapsed, 'is-home': route.path === '/dashboard' }">
    <AppSidebar />
    <div class="app-workspace">
      <AppHeader />
      <main class="main-content">
        <router-view v-slot="{ Component, route }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </main>
    </div>
    <transition name="mask-fade">
      <div v-if="app.mobileSidebarOpen" class="sidebar-mask" @click="app.toggleMobile" />
    </transition>
  </div>
</template>

<style lang="scss">
.app-shell.is-home {
  background: #fff;
  .main-content { max-width: 1660px; padding: 24px 36px 32px; }
  .top-header { background: #fff; border-bottom-color: #e2e7e5; }
  .header-eyebrow { letter-spacing: 0; color: #7c8983; }
  .sidebar { background: #f5f7f6; border-right-color: #e1e6e3; }
  .brand-text b { color: #222f29; letter-spacing: 0; }
  .brand-mark { border-radius: 6px; background: #203e34; }
  .assistant-new-button { color: #365648; border: 1px solid #cfdbd4; background: #fff; border-radius: 5px; &:hover { background: #eaf2ed; } }
  .nav-list a { border-radius: 4px; color: #626e68; &.active { background: #e3eee7; color: #17533e; &::after { background: #17533e; } } }
  .nav-section-label, .assistant-history-heading { letter-spacing: 0; }
}
@media (max-width: 1150px) { .app-shell.is-home .main-content { padding: 22px 24px 28px; } }
@media (max-width: 650px) { .app-shell.is-home .main-content { padding: 16px 18px 24px; } }
</style>

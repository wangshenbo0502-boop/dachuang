<script setup lang="ts">
import AppSidebar from "@/components/layout/AppSidebar.vue";
import AppHeader from "@/components/layout/AppHeader.vue";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
</script>

<template>
  <div class="app-shell" :class="{ collapsed: app.sidebarCollapsed }">
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

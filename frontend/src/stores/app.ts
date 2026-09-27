import { ref, watch } from "vue";
import { defineStore } from "pinia";

const SIDEBAR_KEY = "employment-sidebar-collapsed";

export const useAppStore = defineStore("app", () => {
  let savedCollapsed = false;
  try { savedCollapsed = localStorage.getItem(SIDEBAR_KEY) === "true"; } catch { /* Storage may be unavailable. */ }
  const sidebarCollapsed = ref(savedCollapsed);
  const mobileSidebarOpen = ref(false);

  watch(sidebarCollapsed, value => {
    try { localStorage.setItem(SIDEBAR_KEY, String(value)); } catch { /* Keep the current session usable. */ }
  });

  return {
    sidebarCollapsed,
    mobileSidebarOpen,
    toggleSidebar: () => { sidebarCollapsed.value = !sidebarCollapsed.value; },
    toggleMobile: () => { mobileSidebarOpen.value = !mobileSidebarOpen.value; },
  };
});

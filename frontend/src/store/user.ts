/**
 * 文件名称：user.ts
 * 文件作用：用户状态管理 Store —— 当前用户 ID 持久化到 localStorage，管理资料加载与更新。
 */

import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type { UserCreate, UserProfile } from "@/api/types";
import { createUser, getUser, updateUser } from "@/api/user";

const USER_ID_KEY = "aijob:current_user_id";

function readStoredId(): number | null {
  const raw = localStorage.getItem(USER_ID_KEY);
  if (!raw) return null;
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? n : null;
}

export const useUserStore = defineStore("user", () => {
  const currentUserId = ref<number | null>(readStoredId());
  const profile = ref<UserProfile | null>(null);
  const loading = ref(false);

  const hasUser = computed(() => profile.value !== null);

  function setCurrentUserId(id: number) {
    currentUserId.value = id;
    localStorage.setItem(USER_ID_KEY, String(id));
  }

  async function fetchProfile(id: number | null = currentUserId.value): Promise<UserProfile | null> {
    if (id == null) return null;
    loading.value = true;
    try {
      const res = await getUser(id);
      profile.value = res.data;
      setCurrentUserId(id);
      return res.data;
    } catch {
      profile.value = null;
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function register(data: UserCreate): Promise<UserProfile> {
    const res = await createUser(data);
    profile.value = res.data;
    setCurrentUserId(res.data.id);
    return res.data;
  }

  async function updateProfile(id: number, data: Partial<UserCreate>): Promise<UserProfile> {
    const res = await updateUser(id, data);
    profile.value = res.data;
    return res.data;
  }

  function clear() {
    currentUserId.value = null;
    profile.value = null;
    localStorage.removeItem(USER_ID_KEY);
  }

  return {
    currentUserId,
    profile,
    loading,
    hasUser,
    setCurrentUserId,
    fetchProfile,
    register,
    updateProfile,
    clear,
  };
});
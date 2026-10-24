import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { api } from "@/api";
import { ApiError } from "@/api/request";
import { clearAssistantSessionCache } from "@/utils/assistantSessions";
import type { StudentProfile } from "@/types/api";
import { clearAuthToken, getAuthToken, setAuthToken } from "@/utils/authSession";
import type { AccountRole } from "@/utils/authSession";

export interface AccountIdentity { id: number; email: string; profile_id: number; email_verified: boolean; role: AccountRole; name: string }
export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(getAuthToken());
  const account = ref<AccountIdentity | null>(null);
  const user = ref<StudentProfile | null>(null);
  const loading = ref(false);
  const userId = computed(() => account.value?.role === "student" ? account.value.profile_id : null);
  const isRecruiter = computed(() => account.value?.role === "recruiter");
  const displayName = computed(() => user.value?.name || account.value?.name || "用户");
  const isAuthenticated = computed(() => !!token.value && !!account.value);
  let hydrated = false;

  async function establish(payload: { access_token: string; user: AccountIdentity }) {
    // 切换账号时不能沿用上一个账号留在内存里的对话
    clearAssistantSessionCache();
    setAuthToken(payload.access_token);
    token.value = payload.access_token;
    account.value = payload.user;
    user.value = payload.user.role === "student" ? await api.getUser(payload.user.profile_id) : null;
    hydrated = true;
    return account.value;
  }
  async function login(email: string, password: string, role?: AccountRole) {
    loading.value = true;
    try { return await establish(await api.authLogin({ email, password, role })); }
    catch (error) { clearLocal(); throw error; }
    finally { loading.value = false; }
  }
  async function register(body: object) {
    loading.value = true;
    try { return await establish(await api.authRegister(body)); }
    catch (error) { clearLocal(); throw error; }
    finally { loading.value = false; }
  }
  function clearLocal() {
    token.value = null; account.value = null; user.value = null; hydrated = false;
    clearAuthToken();
    clearAssistantSessionCache();
  }
  async function fetchMe() {
    if (!token.value) return null;
    try {
      account.value = await api.authMe();
      user.value = account.value.role === "student" ? await api.getUser(account.value.profile_id) : null;
      hydrated = true;
      return account.value;
    } catch (error) {
      // 只有凭证确实失效才退出登录；网络波动或服务端 5xx 时保留登录态，交给调用方提示重试
      if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
        clearLocal();
        return null;
      }
      throw error;
    }
  }
  async function hydrate() {
    if (hydrated && account.value) return account.value;
    return fetchMe();
  }
  async function logout() {
    const revoke = token.value ? api.authLogout(token.value) : Promise.resolve();
    clearLocal();
    try { await revoke; } catch { /* Local logout still succeeds if offline. */ }
  }
  return { token, account, user, userId, loading, isAuthenticated, isRecruiter, displayName, login, register, logout, fetchMe, hydrate };
});

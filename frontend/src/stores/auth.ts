import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { api } from "@/api";
import type { StudentProfile } from "@/types/api";
import { clearAuthToken, getAuthToken, setAuthToken } from "@/utils/authSession";

export interface AccountIdentity { id: number; email: string; profile_id: number; email_verified: boolean; role: "student" | "recruiter"; name: string }
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
    setAuthToken(payload.access_token);
    token.value = payload.access_token;
    account.value = payload.user;
    user.value = payload.user.role === "student" ? await api.getUser(payload.user.profile_id) : null;
    hydrated = true;
    return account.value;
  }
  async function login(email: string, password: string) {
    loading.value = true;
    try { return await establish(await api.authLogin({ email, password })); }
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
  }
  async function fetchMe() {
    if (!token.value) return null;
    try {
      account.value = await api.authMe();
      user.value = account.value.role === "student" ? await api.getUser(account.value.profile_id) : null;
      hydrated = true;
      return account.value;
    } catch { clearLocal(); return null; }
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

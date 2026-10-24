const TOKEN_KEY = "employment-platform-access-token";
export type AccountRole = "student" | "recruiter";

export function resolveAuthRole(value: unknown, redirect?: unknown): AccountRole {
  if (value === "student" || value === "recruiter") return value;
  if (typeof redirect === "string") {
    const path = redirect.split(/[?#]/)[0];
    if (path === "/recruiter" || path.startsWith("/recruiter/")) return "recruiter";
  }
  return "student";
}

export const getAuthToken = () => localStorage.getItem(TOKEN_KEY);
export const setAuthToken = (token: string) => localStorage.setItem(TOKEN_KEY, token);
export const clearAuthToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem("employment-platform-user-id");
  sessionStorage.removeItem("employment-platform-user-id");
};

/**
 * 服务端返回 401 时调用：仅当失败请求携带的仍是当前凭证才清除登录态并跳转登录页，
 * 避免旧请求的 401 误伤刚刚重新登录的会话。整页跳转同时会清空内存中的对话副本。
 */
export function handleUnauthorized(sentToken: string | null | undefined) {
  const activeToken = getAuthToken();
  if (!activeToken || sentToken !== activeToken) return;
  clearAuthToken();
  if (!["/login", "/register", "/forgot-password"].includes(window.location.pathname)) {
    const redirect = `${window.location.pathname}${window.location.search}${window.location.hash}`;
    window.location.assign(`/login?redirect=${encodeURIComponent(redirect)}`);
  }
}

export function safeInternalRedirect(value: unknown, role: AccountRole = "student"): string {
  const home = role === "recruiter" ? "/recruiter" : "/dashboard";
  if (typeof value !== "string" || !value.startsWith("/") || value.startsWith("//") || value.includes("\\")) return home;
  const path = value.split(/[?#]/)[0];
  if (["/", "/login", "/register", "/forgot-password"].includes(path)) return home;
  const recruiterPath = path === "/recruiter" || path.startsWith("/recruiter/");
  if (role === "recruiter" && !recruiterPath && path !== "/settings") return home;
  if (role === "student" && recruiterPath) return home;
  return value;
}

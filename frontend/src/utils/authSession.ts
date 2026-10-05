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

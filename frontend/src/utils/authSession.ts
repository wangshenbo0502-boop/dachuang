const TOKEN_KEY = "employment-platform-access-token";
export const getAuthToken = () => localStorage.getItem(TOKEN_KEY);
export const setAuthToken = (token: string) => localStorage.setItem(TOKEN_KEY, token);
export const clearAuthToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem("employment-platform-user-id");
  sessionStorage.removeItem("employment-platform-user-id");
};

export function safeInternalRedirect(value: unknown): string {
  if (typeof value !== "string" || !value.startsWith("/") || value.startsWith("//")) return "/dashboard";
  if (["/login", "/register", "/forgot-password"].includes(value.split("?")[0])) return "/dashboard";
  return value;
}

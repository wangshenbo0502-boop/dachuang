import axios from "axios";

export const api = axios.create({ baseURL: "/admin-api/v1", withCredentials: true });
let csrfToken = "";
api.interceptors.request.use((config) => {
  if (csrfToken && config.method !== "get") config.headers["X-CSRF-Token"] = csrfToken;
  return config;
});

export function setCsrfToken(token: string) {
  csrfToken = token;
}

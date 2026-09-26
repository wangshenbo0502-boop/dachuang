import axios, { AxiosError } from "axios";
import type { ApiEnvelope } from "@/types/api";
import { getAuthToken, clearAuthToken } from "@/utils/authSession";
export class ApiError extends Error {
  constructor(message: string, public code?: number, public status?: number) {
    super(message);
    this.name = "ApiError";
  }
}

const request=axios.create({baseURL:import.meta.env.VITE_API_BASE_URL||"/api",timeout:90000});
request.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

request.interceptors.response.use(
  (response) => {
    const payload = response.data as ApiEnvelope<unknown>;
    if (payload && typeof payload.code === "number" && payload.code !== 0) {
      throw new ApiError(payload.message, payload.code, response.status);
    }
    return response;
  },
  (error: AxiosError<ApiEnvelope<unknown>>) => {
    if (axios.isCancel(error)) return Promise.reject(error);
    const status = error.response?.status;
    if (status === 401 && getAuthToken()) {
      clearAuthToken();
      if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
        window.location.assign("/login");
      }
    }
    const code = error.response?.data?.code;
    const validationMessage = Array.isArray(error.response?.data?.data)
      ? error.response?.data?.data
          .map((item: any) => `${Array.isArray(item?.loc) ? item.loc.join(".") : "请求"}：${item?.msg || "参数不合法"}`)
          .join("；")
      : "";
    const message =
      validationMessage ||
      error.response?.data?.message ||
      (code === 3101 || status === 503
        ? "知识库服务暂不可用，请先启动 PostgreSQL + pgvector 并完成知识库初始化"
        : error.code === "ECONNABORTED"
          ? "请求超时，请稍后重试"
          : "服务连接失败，请确认后端已启动");
    return Promise.reject(new ApiError(message, code, status));
  },
);

export async function apiData<T>(promise: Promise<{ data: ApiEnvelope<T> }>) {
  return (await promise).data.data;
}

export default request;

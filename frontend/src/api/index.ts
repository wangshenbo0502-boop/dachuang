/**
 * 文件名称：index.ts
 * 文件作用：axios 实例与全局拦截器 —— 统一三段式响应处理、X-Request-ID 注入、业务错误抛出。
 * 拦截器将响应解包为 ApiResponse 体（调用方通过 res.data 直接取业务数据）。
 */

import axios from "axios";
import type { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import type { ApiResponse } from "./types";

/** 业务错误（携带后端 code 与 HTTP 状态） */
export class ApiError extends Error {
  code: number;
  status: number;
  constructor(message: string, code = -1, status = 0) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

const http = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// 请求拦截器：注入 X-Request-ID
http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  config.headers.set("X-Request-ID", Math.random().toString(36).slice(2, 10));
  return config;
});

// 从 422 校验错误中提取首条字段提示
function extractValidationDetail(body: ApiResponse): string {
  const data = body?.data;
  if (Array.isArray(data) && data.length > 0) {
    const first = data[0] as { msg?: string; loc?: unknown[] };
    if (first?.msg) {
      const loc = Array.isArray(first.loc) ? first.loc.join(".") : "";
      return loc ? `${first.msg}（字段：${loc}）` : first.msg;
    }
  }
  return body?.message ?? "请求失败";
}

http.interceptors.response.use(
  (response) => {
    const body = response.data as ApiResponse;
    if (body && typeof body === "object" && "code" in body && body.code !== 0) {
      const message = response.status === 422 ? extractValidationDetail(body) : body.message;
      return Promise.reject(new ApiError(message, body.code, response.status));
    }
    // 解包：返回 ApiResponse 体，而非 AxiosResponse
    return response.data;
  },
  (error: AxiosError<ApiResponse>) => {
    if (error.response) {
      const body = error.response.data;
      if (body && (body as ApiResponse).code !== undefined) {
        const message =
          error.response.status === 422 ? extractValidationDetail(body) : (body as ApiResponse).message;
        return Promise.reject(
          new ApiError(message || "请求失败", (body as ApiResponse).code, error.response.status)
        );
      }
      if (error.response.status === 429) {
        return Promise.reject(new ApiError("请求过于频繁，请稍后再试", 429, 429));
      }
      return Promise.reject(
        new ApiError(`请求失败（HTTP ${error.response.status}）`, -1, error.response.status)
      );
    }
    return Promise.reject(new ApiError("网络错误，无法连接服务", -1, 0));
  }
);

export default http;
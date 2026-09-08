/**
 * 文件名称：system.ts
 * 文件作用：系统类接口（服务信息/健康检查/Token 用量）。
 */

import http from "./index";
import type { ApiResponse, HealthData, UsageData } from "./types";

/** GET / — 服务信息 */
export function getServiceInfo() {
  return http.get<ApiResponse<Record<string, unknown>>>("/");
}

/** GET /api/health — 健康检查 */
export function getHealth() {
  return http.get<never, ApiResponse<HealthData>>("/health");
}

/** GET /api/usage — token 用量统计 */
export function getUsage() {
  return http.get<never, ApiResponse<UsageData>>("/usage");
}
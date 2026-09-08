/**
 * 文件名称：growth.ts
 * 文件作用：AI 成长规划相关 API 请求封装（契约见 docs/02-API接口文档.md 第 8 章）。
 */

import http from "./index";
import type {
  ApiResponse,
  GrowthHistoryItem,
  GrowthPlanRequest,
  GrowthPlanResponse,
} from "./types";

/** POST /api/growth — 生成成长规划（落库） */
export function generatePlan(data: GrowthPlanRequest): Promise<ApiResponse<GrowthPlanResponse>> {
  return http.post<unknown, ApiResponse<GrowthPlanResponse>>("/growth", data, {
    timeout: 60000,
  });
}

/** GET /api/growth/{plan_id} — 规划记录详情 */
export function getPlan(planId: number): Promise<ApiResponse<GrowthPlanResponse>> {
  return http.get<unknown, ApiResponse<GrowthPlanResponse>>(`/growth/${planId}`);
}

/** GET /api/growth/user/{user_id} — 历史规划列表 */
export function getPlanHistory(userId: number): Promise<ApiResponse<GrowthHistoryItem[]>> {
  return http.get<unknown, ApiResponse<GrowthHistoryItem[]>>(`/growth/user/${userId}`);
}
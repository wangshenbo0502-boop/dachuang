/**
 * 文件名称：resume.ts
 * 文件作用：简历优化相关 API 请求封装（契约见 docs/02-API接口文档.md 第 7 章）。
 */

import http from "./index";
import type {
  ApiResponse,
  ResumeHistoryItem,
  ResumeOptimizationRequest,
  ResumeOptimizationResponse,
} from "./types";

/** POST /api/resume — AI 简历优化（落库） */
export function optimizeResume(
  data: ResumeOptimizationRequest
): Promise<ApiResponse<ResumeOptimizationResponse>> {
  return http.post<unknown, ApiResponse<ResumeOptimizationResponse>>("/resume", data, {
    timeout: 60000,
  });
}

/** GET /api/resume/{optimization_id} — 优化记录详情 */
export function getResumeOptimization(
  optimizationId: number
): Promise<ApiResponse<ResumeOptimizationResponse>> {
  return http.get<unknown, ApiResponse<ResumeOptimizationResponse>>(`/resume/${optimizationId}`);
}

/** GET /api/resume/user/{user_id} — 历史优化列表 */
export function getResumeHistory(userId: number): Promise<ApiResponse<ResumeHistoryItem[]>> {
  return http.get<unknown, ApiResponse<ResumeHistoryItem[]>>(`/resume/user/${userId}`);
}
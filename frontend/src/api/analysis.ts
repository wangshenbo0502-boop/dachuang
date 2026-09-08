/**
 * 文件名称：analysis.ts
 * 文件作用：AI 就业画像分析相关 API 请求封装（契约见 docs/02-API接口文档.md 第 6 章）。
 */

import http from "./index";
import type {
  AnalysisHistoryItem,
  ApiResponse,
  ProfileAnalysisRequest,
  ProfileAnalysisResponse,
} from "./types";

/** POST /api/analysis — AI 就业画像分析（落库） */
export function startAnalysis(
  data: ProfileAnalysisRequest
): Promise<ApiResponse<ProfileAnalysisResponse>> {
  return http.post<unknown, ApiResponse<ProfileAnalysisResponse>>("/analysis", data, {
    timeout: 60000,
  });
}

/** GET /api/analysis/{analysis_id} — 分析记录详情 */
export function getAnalysis(analysisId: number): Promise<ApiResponse<ProfileAnalysisResponse>> {
  return http.get<unknown, ApiResponse<ProfileAnalysisResponse>>(`/analysis/${analysisId}`);
}

/** GET /api/analysis/user/{user_id} — 历史分析列表 */
export function getAnalysisHistory(userId: number): Promise<ApiResponse<AnalysisHistoryItem[]>> {
  return http.get<unknown, ApiResponse<AnalysisHistoryItem[]>>(`/analysis/user/${userId}`);
}
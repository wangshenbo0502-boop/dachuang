/**
 * 文件名称：jobMatch.ts
 * 文件作用：岗位匹配相关 API 请求封装（契约见 docs/02-API接口文档.md 第 5 章）。
 */

import http from "./index";
import type {
  ApiResponse,
  JobDetail,
  JobListResponse,
  MatchRecord,
  MatchResult,
} from "./types";

export interface JobListParams {
  keyword?: string;
  category?: string;
  page?: number;
  page_size?: number;
}

export interface MatchRequest {
  skills: string[];
  job_category?: string | null;
  top_k?: number;
  user_id?: number | null;
}

/** GET /api/jobs — 岗位列表搜索 */
export function getJobList(params: JobListParams = {}): Promise<ApiResponse<JobListResponse>> {
  return http.get<unknown, ApiResponse<JobListResponse>>("/jobs", { params });
}

/** GET /api/jobs/{job_id} — 岗位详情 */
export function getJobDetail(jobId: string): Promise<ApiResponse<JobDetail>> {
  return http.get<unknown, ApiResponse<JobDetail>>(`/jobs/${encodeURIComponent(jobId)}`);
}

/** POST /api/match — 岗位技能匹配（落库） */
export function startMatch(data: MatchRequest): Promise<ApiResponse<MatchResult>> {
  return http.post<unknown, ApiResponse<MatchResult>>("/match", data, { timeout: 60000 });
}

/** GET /api/match/{match_id} — 查询历史匹配记录 */
export function getMatchRecord(matchId: number): Promise<ApiResponse<MatchRecord>> {
  return http.get<unknown, ApiResponse<MatchRecord>>(`/match/${matchId}`);
}
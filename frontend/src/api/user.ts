/**
 * 文件名称：user.ts
 * 文件作用：用户管理相关 API 请求封装（契约见 docs/02-API接口文档.md 第 4 章）。
 */

import http from "./index";
import type {
  ApiResponse,
  CompetitionItem,
  InternshipItem,
  ProjectItem,
  SkillItem,
  UserCreate,
  UserProfile,
  UserUpdate,
} from "./types";

/** POST /api/users — 创建学生资料（201） */
export function createUser(data: UserCreate): Promise<ApiResponse<UserProfile>> {
  return http.post<unknown, ApiResponse<UserProfile>>("/users", data);
}

/** GET /api/users/{user_id} — 获取完整资料 */
export function getUser(userId: number): Promise<ApiResponse<UserProfile>> {
  return http.get<unknown, ApiResponse<UserProfile>>(`/users/${userId}`);
}

/** PUT /api/users/{user_id} — 更新基本资料 */
export function updateUser(userId: number, data: UserUpdate): Promise<ApiResponse<UserProfile>> {
  return http.put<unknown, ApiResponse<UserProfile>>(`/users/${userId}`, data);
}

/** PUT /api/users/{user_id}/skills — 整组替换技能 */
export function replaceSkills(
  userId: number,
  skills: SkillItem[]
): Promise<ApiResponse<SkillItem[]>> {
  return http.put<unknown, ApiResponse<SkillItem[]>>(`/users/${userId}/skills`, { skills });
}

/** PUT /api/users/{user_id}/projects — 整组替换项目经历 */
export function replaceProjects(
  userId: number,
  projects: ProjectItem[]
): Promise<ApiResponse<ProjectItem[]>> {
  return http.put<unknown, ApiResponse<ProjectItem[]>>(`/users/${userId}/projects`, { projects });
}

/** PUT /api/users/{user_id}/competitions — 整组替换竞赛经历 */
export function replaceCompetitions(
  userId: number,
  competitions: CompetitionItem[]
): Promise<ApiResponse<CompetitionItem[]>> {
  return http.put<unknown, ApiResponse<CompetitionItem[]>>(`/users/${userId}/competitions`, {
    competitions,
  });
}

/** PUT /api/users/{user_id}/internships — 整组替换实习经历 */
export function replaceInternships(
  userId: number,
  internships: InternshipItem[]
): Promise<ApiResponse<InternshipItem[]>> {
  return http.put<unknown, ApiResponse<InternshipItem[]>>(`/users/${userId}/internships`, {
    internships,
  });
}

/** GET /api/users/{user_id}/context — AI 学生上下文 */
export function getUserContext(userId: number): Promise<ApiResponse<UserProfile>> {
  return http.get<unknown, ApiResponse<UserProfile>>(`/users/${userId}/context`);
}
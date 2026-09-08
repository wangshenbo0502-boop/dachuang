/**
 * 文件名称：types.ts
 * 文件作用：前端与后端交互的 TypeScript 类型定义，与 docs/02-API接口文档.md 逐字段对齐。
 */

/** 三段式统一响应 */
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

/* ---------------- 用户 ---------------- */
export type Proficiency = "了解" | "熟悉" | "掌握" | "精通" | string;

export interface SkillItem {
  id?: number;
  user_id?: number;
  name: string;
  proficiency: Proficiency;
  description?: string;
}

export interface ProjectItem {
  id?: number;
  name: string;
  role: string;
  description: string;
  tech_stack: string[];
  start_date?: string;
  end_date?: string;
}

export interface CompetitionItem {
  id?: number;
  name: string;
  level?: string;
  award?: string;
  description?: string;
  competition_date?: string;
}

export interface InternshipItem {
  id?: number;
  company: string;
  position: string;
  description?: string;
  tech_stack?: string[];
  start_date?: string;
  end_date?: string;
}

export interface UserCreate {
  name: string;
  school: string;
  major: string;
  grade: string;
  bio?: string;
  email?: string;
  phone?: string;
  target_city?: string;
  target_salary?: string;
}

export type UserUpdate = Partial<UserCreate>;

export interface UserProfile {
  id: number;
  name: string;
  school: string;
  major: string;
  grade: string;
  bio?: string;
  email?: string;
  phone?: string;
  target_city?: string;
  target_salary?: string;
  created_at?: string;
  updated_at?: string;
  skills: SkillItem[];
  projects: ProjectItem[];
  competitions: CompetitionItem[];
  internships: InternshipItem[];
}

/* ---------------- 岗位 ---------------- */
export interface JobListItem {
  job_id: string;
  title: string;
  category: string;
  tags: string[];
  snippet: string;
}

export interface JobListResponse {
  total: number;
  keyword: string;
  items: JobListItem[];
}

export interface JobDetail {
  job_id: string;
  title: string;
  category: string;
  tags: string[];
  content: string;
  metadata: Record<string, unknown>;
}

/* ---------------- 岗位匹配 ---------------- */
export interface MatchItem {
  job_id: string;
  title: string;
  category: string;
  tags: string[];
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  snippet: string;
  match_reason?: string;
  learning_suggestions?: string[];
  interview_focus?: string[];
}

export interface MatchResult {
  user_skills: string[];
  total_matches: number;
  matches: MatchItem[];
  record_id: number | null;
}

export interface MatchRecord {
  id: number;
  user_id: number;
  skills: string[];
  job_id: string;
  job_title: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  matches: MatchItem[];
  created_at: string;
}

/* ---------------- AI 就业画像 ---------------- */
export interface RecommendedDirection {
  job_title: string;
  match_rate: number;
}

export interface SkillAssessment {
  programming_foundation: number;
  framework_usage: number;
  database_skill: number;
  engineering_practice: number;
  project_experience: number;
}

export interface AnalysisResult {
  profile_summary: string;
  technical_direction: string;
  core_advantages: string[];
  current_level: string;
  recommended_directions: RecommendedDirection[];
  areas_to_improve: string[];
  comprehensive_score: number;
  skill_assessment: SkillAssessment;
}

export interface ProfileAnalysisResponse {
  id: number;
  user_id: number;
  target_job?: string;
  is_mock: boolean;
  created_at: string;
  result: AnalysisResult;
}

export interface AnalysisHistoryItem {
  id: number;
  user_id: number;
  target_job?: string;
  technical_direction: string;
  comprehensive_score: number;
  created_at: string;
}

export interface ProfileAnalysisRequest {
  user_id?: number;
  name?: string;
  school?: string;
  major?: string;
  grade?: string;
  bio?: string;
  skills?: SkillItem[];
  projects?: ProjectItem[];
  target_job?: string;
}

/* ---------------- 简历优化 ---------------- */
export interface OptimizedProject {
  project_name: string;
  original: string;
  optimized: string;
  highlight_tags: string[];
}

export interface OptimizedSkill {
  original: string;
  optimized: string;
}

export interface ResumeResult {
  optimized_projects: OptimizedProject[];
  optimized_skills: OptimizedSkill[];
  overall_suggestions: string[];
  personal_summary: string;
  resume_score: number;
}

export interface ResumeOptimizationResponse {
  id: number;
  user_id: number;
  target_job: string;
  is_mock: boolean;
  created_at: string;
  result: ResumeResult;
}

export interface ResumeOptimizationRequest {
  user_id?: number;
  name?: string;
  target_job: string;
  skills?: SkillItem[];
  projects?: ProjectItem[];
  original_resume?: string;
}

export interface ResumeHistoryItem {
  id: number;
  user_id: number;
  target_job: string;
  resume_score: number;
  created_at: string;
}

/* ---------------- 成长规划 ---------------- */
export interface AbilityGap {
  skill: string;
  importance: string;
  difficulty: string;
  description: string;
}

export interface RoadmapStage {
  stage: string;
  focus: string;
  tasks: string[];
  milestone: string;
}

export interface RecommendedProject {
  name: string;
  description: string;
  tech_stack: string[];
  difficulty: string;
}

export interface GrowthResult {
  current_situation: string;
  ability_gaps: AbilityGap[];
  learning_roadmap: RoadmapStage[];
  recommended_projects: RecommendedProject[];
  recommended_resources: string[];
  interview_prep_tips: string[];
  expected_timeline: string;
}

export interface GrowthPlanResponse {
  id: number;
  user_id: number;
  target_job: string;
  is_mock: boolean;
  created_at: string;
  result: GrowthResult;
}

export interface GrowthPlanRequest {
  user_id?: number;
  target_job: string;
  profile_analysis?: Record<string, unknown>;
}

export interface GrowthHistoryItem {
  id: number;
  user_id: number;
  target_job: string;
  expected_timeline: string;
  created_at: string;
}

/* ---------------- 系统 ---------------- */
export interface HealthData {
  status: string;
  environment: string;
  ai_mode: "mock" | "live";
  modules: string[];
}

export interface UsageData {
  daily_prompt_tokens: number;
  daily_completion_tokens: number;
  daily_total_tokens: number;
  daily_cost_usd: number;
  daily_call_count: number;
  is_over_budget: boolean;
  is_near_limit: boolean;
}
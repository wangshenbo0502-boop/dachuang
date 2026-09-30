import type { Skill, Project, Competition, Internship } from './api';

export interface PageResult<T> { items: T[]; total: number; page: number; page_size: number }
export interface RecruiterProfile {
  account_id?: number; company_name: string; industry: string; city: string;
  description: string; contact_name: string; contact_email: string;
}
export type JobState = 'draft' | 'published' | 'closed';
export interface JobInput {
  title: string; category: string; city: string; salary: string;
  employment_type: '实习' | '全职' | '兼职'; education: '不限' | '大专' | '本科' | '硕士' | '博士';
  experience: string; description: string; requirements: string; tags: string[];
}
export interface RecruitmentJob extends JobInput {
  id: number; recruiter_id: number; company_name: string; status: JobState;
  created_at: string; updated_at: string; published_at: string | null; company?: RecruiterProfile;
}
export type RecruitmentState = 'submitted' | 'reviewing' | 'interview' | 'offered' | 'rejected' | 'withdrawn';
export type ReviewState = 'reviewing' | 'interview' | 'offered' | 'rejected';
export interface ResumeSnapshot {
  name: string; target_job: string; personal_summary: string;
  profile: { name: string; school: string; major: string; grade: string; email: string; phone: string;
    skills: Skill[]; projects: Project[]; competitions: Competition[]; internships: Internship[] };
}
export interface RecruitmentApplication {
  id: number; job_id: number; student_id: number; job_title: string; company_name: string;
  resume_snapshot: ResumeSnapshot; note: string; status: RecruitmentState; feedback: string;
  created_at: string; updated_at: string;
}

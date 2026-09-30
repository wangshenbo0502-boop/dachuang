import request, { apiData } from './request';
import type { RecruiterProfile, JobInput, RecruitmentJob, RecruitmentApplication, PageResult, ReviewState } from '@/types/recruitment';

export const recruitmentApi = {
  profile: () => apiData<RecruiterProfile>(request.get('/recruiter/profile')),
  saveProfile: (body: RecruiterProfile) => {
    const { account_id, ...fields } = body;
    return apiData<RecruiterProfile>(request.put('/recruiter/profile', fields));
  },
  ownedJobs: (params: object) => apiData<PageResult<RecruitmentJob>>(request.get('/recruiter/jobs', { params })),
  ownedJob: (id: number) => apiData<RecruitmentJob>(request.get(`/recruiter/jobs/${id}`)),
  createJob: (body: JobInput) => apiData<RecruitmentJob>(request.post('/recruiter/jobs', body)),
  saveJob: (id: number, body: JobInput) => apiData<RecruitmentJob>(request.put(`/recruiter/jobs/${id}`, body)),
  jobStatus: (id: number, status: 'published' | 'closed') => apiData<RecruitmentJob>(request.post(`/recruiter/jobs/${id}/status`, { status })),
  deleteJob: (id: number) => apiData<null>(request.delete(`/recruiter/jobs/${id}`)),
  received: (params: object) => apiData<PageResult<RecruitmentApplication>>(request.get('/recruiter/applications', { params })),
  review: (id: number, body: { status: ReviewState; feedback: string }) => apiData<RecruitmentApplication>(request.patch(`/recruiter/applications/${id}`, body)),
  jobs: (params: object) => apiData<PageResult<RecruitmentJob>>(request.get('/recruitment/jobs', { params })),
  job: (id: number) => apiData<RecruitmentJob>(request.get(`/recruitment/jobs/${id}`)),
  apply: (id: number, body: { resume_id: number; note: string }) => apiData<RecruitmentApplication>(request.post(`/recruitment/jobs/${id}/apply`, body)),
  applications: (params: object) => apiData<PageResult<RecruitmentApplication>>(request.get('/recruitment/applications', { params })),
  withdraw: (id: number) => apiData<RecruitmentApplication>(request.post(`/recruitment/applications/${id}/withdraw`)),
};

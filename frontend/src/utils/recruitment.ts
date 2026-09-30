import type { JobInput, RecruitmentState, ReviewState } from '@/types/recruitment';

export const jobCategories = ['前端', '后端', 'AI', '数据', '测试', '运维', '产品', '运营', '安全', '移动端', '其他'];
export const jobLabels = { draft: '草稿', published: '招聘中', closed: '已下架' };
export const applicationLabels: Record<RecruitmentState, string> = {
  submitted: '已投递', reviewing: '筛选中', interview: '面试中', offered: '已录用', rejected: '未通过', withdrawn: '已撤回',
};
export const reviewTransitions: Record<RecruitmentState, ReviewState[]> = {
  submitted: ['reviewing', 'interview', 'rejected'], reviewing: ['reviewing', 'interview', 'rejected'],
  interview: ['interview', 'offered', 'rejected'], offered: [], rejected: [], withdrawn: [],
};
export const canWithdraw = (status: RecruitmentState) => ['submitted', 'reviewing', 'interview'].includes(status);
export const applicationTone = (status: RecruitmentState): 'info' | 'success' | 'warning' | 'danger' =>
  status === 'rejected' ? 'danger' : status === 'offered' ? 'success' : canWithdraw(status) ? 'warning' : 'info';
export const emptyJob = (): JobInput => ({ title: '', category: '', city: '', salary: '', employment_type: '实习',
  education: '不限', experience: '不限', description: '', requirements: '', tags: [] });

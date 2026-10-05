import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";
import MainLayout from "@/layouts/MainLayout.vue";
import { safeInternalRedirect } from "@/utils/authSession";

const routes=[
  {path:"/login",name:"login",component:()=>import("@/views/login/LoginView.vue"),meta:{title:"登录",public:true}},
  {path:"/register",name:"register",component:()=>import("@/views/login/RegisterView.vue"),meta:{title:"注册",public:true}},
  {path:"/forgot-password",name:"forgot-password",component:()=>import("@/views/login/ForgotPasswordView.vue"),meta:{title:"重置密码",public:true}},
  {path:"/",component:MainLayout,redirect:"/dashboard",children:[
    {path:"recruiter",name:"recruiter",component:()=>import("@/views/recruiter/RecruiterView.vue"),meta:{title:"招聘工作台",role:"recruiter"}},
    {path:"recruiter/jobs/new",name:"recruiter-job-new",component:()=>import("@/views/recruiter/JobEditorView.vue"),meta:{title:"创建招聘岗位",role:"recruiter"}},
    {path:"recruiter/jobs/:id/edit",name:"recruiter-job-edit",component:()=>import("@/views/recruiter/JobEditorView.vue"),meta:{title:"编辑招聘岗位",role:"recruiter"}},
    {path:"recruitment",name:"recruitment",component:()=>import("@/views/recruitment/RecruitmentView.vue"),meta:{title:"招聘岗位"}},
    {path:"recruitment/jobs/:id",name:"recruitment-detail",component:()=>import("@/views/recruitment/RecruitmentDetailView.vue"),meta:{title:"招聘岗位详情"}},
    {path:"recruitment/applications",name:"recruitment-applications",component:()=>import("@/views/recruitment/MyApplicationsView.vue"),meta:{title:"站内投递"}},
    {path:"dashboard",name:"dashboard",component:()=>import("@/views/dashboard/DashboardView.vue"),meta:{title:"IT 求职工作台"}},
    {path:"profile",name:"profile",component:()=>import("@/views/profile/ProfileView.vue"),meta:{title:"我的 IT 求职档案"}},
    {path:"profile/assistant",name:"profile-assistant",redirect:{path:"/coach",query:{mode:"profile"}}},
    {path:"analysis",name:"analysis",component:()=>import("@/views/analysis/AnalysisView.vue"),meta:{title:"IT 就业画像"}},
    {path:"coach",name:"coach",component:()=>import("@/views/coach/CoachView.vue"),meta:{title:"IT 求职教练"}},
    {path:"jobs",name:"jobs",component:()=>import("@/views/jobs/JobsView.vue"),meta:{title:"IT 岗位匹配"}},
    {path:"jobs/:id",name:"job-detail",component:()=>import("@/views/jobs/JobDetailView.vue"),meta:{title:"IT 岗位详情"}},
    {path:"applications",name:"applications",component:()=>import("@/views/applications/ApplicationsView.vue"),meta:{title:"IT 投递记录"}},
    {path:"resume",name:"resume",component:()=>import("@/views/resume/ResumeView.vue"),meta:{title:"开发者简历"}},
    {path:"growth",name:"growth",component:()=>import("@/views/growth/GrowthView.vue"),meta:{title:"IT 技术成长规划"}},
    {path:"resources",name:"resources",component:()=>import("@/views/resources/ResourcesView.vue"),meta:{title:"IT 就业资源"}},
    {path:"history",name:"history",component:()=>import("@/views/history/HistoryView.vue"),meta:{title:"分析记录"}},
    {path:"settings",name:"settings",component:()=>import("@/views/settings/SettingsView.vue"),meta:{title:"系统设置"}},
  ]},
  {path:"/:pathMatch(.*)*",redirect:"/dashboard"}
];
const router=createRouter({history:createWebHistory(),routes,scrollBehavior:()=>({top:0})});
router.beforeEach(async to => {
  const u = useUserStore();
  document.title = `${String(to.meta.title || "")} - IT 求职成长系统`;
  const identity = await u.hydrate();
  if (to.meta.public) return identity ? safeInternalRedirect(to.query.redirect, identity.role) : true;
  if (!identity) return {path: "/login", query: {redirect: to.fullPath, role: to.meta.role === "recruiter" ? "recruiter" : "student"}};
  if (to.path !== "/settings") {
    const role = to.meta.role || "student";
    if (identity.role !== role) return identity.role === "recruiter" ? "/recruiter" : "/dashboard";
  }
  return true;
});
export default router;

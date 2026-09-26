import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";
import MainLayout from "@/layouts/MainLayout.vue";
import { safeInternalRedirect } from "@/utils/authSession";

const routes=[
  {path:"/login",name:"login",component:()=>import("@/views/login/LoginView.vue"),meta:{title:"登录",public:true}},
  {path:"/register",name:"register",component:()=>import("@/views/login/RegisterView.vue"),meta:{title:"注册",public:true}},
  {path:"/forgot-password",name:"forgot-password",component:()=>import("@/views/login/ForgotPasswordView.vue"),meta:{title:"重置密码",public:true}},
  {path:"/",component:MainLayout,redirect:"/dashboard",children:[
    {path:"dashboard",name:"dashboard",component:()=>import("@/views/dashboard/DashboardView.vue"),meta:{title:"就业能力概览"}},
    {path:"profile",name:"profile",component:()=>import("@/views/profile/ProfileView.vue"),meta:{title:"我的就业档案"}},
    {path:"profile/assistant",name:"profile-assistant",redirect:{path:"/coach",query:{mode:"profile"}}},
    {path:"analysis",name:"analysis",component:()=>import("@/views/analysis/AnalysisView.vue"),meta:{title:"AI就业画像"}},
    {path:"coach",name:"coach",component:()=>import("@/views/coach/CoachView.vue"),meta:{title:"AI求职助手"}},
    {path:"jobs",name:"jobs",component:()=>import("@/views/jobs/JobsView.vue"),meta:{title:"岗位方向匹配"}},
    {path:"jobs/:id",name:"job-detail",component:()=>import("@/views/jobs/JobDetailView.vue"),meta:{title:"岗位详情"}},
    {path:"resume",name:"resume",component:()=>import("@/views/resume/ResumeView.vue"),meta:{title:"简历优化"}},
    {path:"growth",name:"growth",component:()=>import("@/views/growth/GrowthView.vue"),meta:{title:"成长规划"}},
    {path:"resources",name:"resources",component:()=>import("@/views/resources/ResourcesView.vue"),meta:{title:"就业资源"}},
    {path:"history",name:"history",component:()=>import("@/views/history/HistoryView.vue"),meta:{title:"分析记录"}},
    {path:"settings",name:"settings",component:()=>import("@/views/settings/SettingsView.vue"),meta:{title:"系统设置"}},
  ]},
  {path:"/:pathMatch(.*)*",redirect:"/dashboard"}
];
const router=createRouter({history:createWebHistory(),routes,scrollBehavior:()=>({top:0})});
router.beforeEach(async to=>{const u=useUserStore();document.title=`${String(to.meta.title||"")} - 大学生就业竞争力评估系统`;const loaded=await u.hydrate();if(to.meta.public){if(loaded)return safeInternalRedirect(to.query.redirect);return true}if(!loaded)return{path:"/login",query:{redirect:to.fullPath}};return true});
export default router;

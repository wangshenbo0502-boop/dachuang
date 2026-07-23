/**
 * 文件名称：index.ts
 * 文件作用：Vue Router 路由配置，定义页面路由映射。
 * 当前阶段仅定义基础路由结构，路由守卫后续实现。
 */

import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/views/Home.vue"),
    meta: { title: "首页" },
  },
  {
    path: "/profile",
    name: "Profile",
    component: () => import("@/views/Profile.vue"),
    meta: { title: "AI就业画像" },
  },
  {
    path: "/job-match",
    name: "JobMatch",
    component: () => import("@/views/JobMatch.vue"),
    meta: { title: "岗位匹配" },
  },
  {
    path: "/resume",
    name: "Resume",
    component: () => import("@/views/Resume.vue"),
    meta: { title: "简历优化" },
  },
  {
    path: "/growth",
    name: "Growth",
    component: () => import("@/views/Growth.vue"),
    meta: { title: "成长规划" },
  },
  // TODO: 后续添加 登录/注册 路由
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// TODO: 添加路由守卫（权限验证、页面标题设置等）

export default router;

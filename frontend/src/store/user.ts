/**
 * 文件名称：user.ts
 * 文件作用：用户状态管理 Store，管理用户登录状态和基本信息。
 * 当前阶段仅定义 Store 框架，具体状态和操作后续实现。
 */

import { defineStore } from "pinia";
import { ref } from "vue";

export const useUserStore = defineStore("user", () => {
  // TODO: 用户信息状态
  const userInfo = ref<object | null>(null);
  const isLoggedIn = ref(false);

  // TODO: 登录操作
  // function login() {}

  // TODO: 登出操作
  // function logout() {}

  // TODO: 获取用户信息
  // function fetchUserInfo() {}

  return {
    userInfo,
    isLoggedIn,
  };
});

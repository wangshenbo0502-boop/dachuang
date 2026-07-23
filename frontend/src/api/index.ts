/**
 * 文件名称：index.ts
 * 文件作用：API 请求基础配置，封装 axios 实例和通用拦截器。
 * 当前阶段仅定义 axios 实例框架，具体拦截逻辑后续实现。
 */

import axios from "axios";

// 创建 axios 实例
const http = axios.create({
  // TODO: 从环境变量读取 baseURL
  baseURL: "/api",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// TODO: 请求拦截器（添加 Token 等）
// http.interceptors.request.use(...)

// TODO: 响应拦截器（统一错误处理）
// http.interceptors.response.use(...)

export default http;

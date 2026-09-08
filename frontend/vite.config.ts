/**
 * 文件名称：vite.config.ts
 * 文件作用：Vite 构建配置，定义项目构建参数、代理规则等。
 * 当前阶段仅配置基础 Vue 插件和开发服务器代理。
 */

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});

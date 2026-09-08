/**
 * 文件名称：vite.config.ts
 * 文件作用：Vite 构建配置 —— React 3D 应用 + /api 后端代理。
 */

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import viteCompression from "vite-plugin-compression";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [react(), viteCompression()],
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

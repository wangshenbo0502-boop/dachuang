/**
 * 文件名称：env.d.ts
 * 文件作用：TypeScript 环境类型声明，声明 .vue 文件模块类型。
 */

/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<object, object, unknown>;
  export default component;
}

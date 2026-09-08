/**
 * 文件名称：reveal.ts
 * 文件作用：v-reveal 滚动进入动效指令 —— 元素进入视口时添加 .is-visible 触发淡入上移。
 * 用法：v-reveal 或 v-reveal="'120ms'"（可选延迟）。
 */

import type { Directive } from "vue";

const observer = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    }
  },
  { threshold: 0.12 }
);

export const reveal: Directive<HTMLElement, string | undefined> = {
  mounted(el, binding) {
    el.classList.add("reveal");
    if (binding.value) {
      el.style.transitionDelay = binding.value;
    }
    observer.observe(el);
  },
  unmounted(el) {
    observer.unobserve(el);
  },
};
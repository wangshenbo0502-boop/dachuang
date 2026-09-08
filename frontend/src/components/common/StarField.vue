<!--
  文件名称：StarField.vue
  文件作用：深空星海背景（Canvas2D 粒子 + 连线，含鼠标视差），营造作品的纵深感。
-->
<template>
  <canvas ref="canvas" class="star-field" aria-hidden="true"></canvas>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const canvas = ref<HTMLCanvasElement | null>(null);

interface Particle {
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  r: number;
  color: string;
}

const COLORS = ["#22d3ee", "#5b7cff", "#a855f7", "#eef1fb"];
const LINK_DIST = 130;
const MAX_PARTICLES = 110;

let ctx: CanvasRenderingContext2D | null = null;
let particles: Particle[] = [];
let width = 0;
let height = 0;
let raf = 0;
let mouseX = 0;
let mouseY = 0;

function resize() {
  const el = canvas.value;
  if (!el) return;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  width = window.innerWidth;
  height = window.innerHeight;
  el.width = width * dpr;
  el.height = height * dpr;
  el.style.width = `${width}px`;
  el.style.height = `${height}px`;
  ctx = el.getContext("2d");
  ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
  spawn();
}

function spawn() {
  const count = Math.min(MAX_PARTICLES, Math.floor((width * height) / 13000));
  particles = Array.from({ length: count }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    z: 0.4 + Math.random() * 0.6,
    vx: (Math.random() - 0.5) * 0.24,
    vy: (Math.random() - 0.5) * 0.24,
    r: 0.6 + Math.random() * 1.6,
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
  }));
}

function tick() {
  if (!ctx) return;
  ctx.clearRect(0, 0, width, height);

  for (const p of particles) {
    p.x += p.vx;
    p.y += p.vy;
    if (p.x < -20) p.x = width + 20;
    if (p.x > width + 20) p.x = -20;
    if (p.y < -20) p.y = height + 20;
    if (p.y > height + 20) p.y = -20;

    const px = p.x + mouseX * p.z * 18;
    const py = p.y + mouseY * p.z * 18;
    ctx.beginPath();
    ctx.arc(px, py, p.r * p.z, 0, Math.PI * 2);
    ctx.globalAlpha = 0.35 + p.z * 0.4;
    ctx.fillStyle = p.color;
    ctx.fill();
  }

  // 连线
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const a = particles[i];
      const b = particles[j];
      const ax = a.x + mouseX * a.z * 18;
      const ay = a.y + mouseY * a.z * 18;
      const bx = b.x + mouseX * b.z * 18;
      const by = b.y + mouseY * b.z * 18;
      const dx = ax - bx;
      const dy = ay - by;
      const d = dx * dx + dy * dy;
      if (d < LINK_DIST * LINK_DIST) {
        ctx.globalAlpha = (1 - Math.sqrt(d) / LINK_DIST) * 0.16;
        ctx.strokeStyle = "#5b7cff";
        ctx.lineWidth = 0.6;
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
        ctx.stroke();
      }
    }
  }
  ctx.globalAlpha = 1;
  raf = requestAnimationFrame(tick);
}

function onMouseMove(e: MouseEvent) {
  mouseX = e.clientX / width - 0.5;
  mouseY = e.clientY / height - 0.5;
}

onMounted(() => {
  resize();
  window.addEventListener("resize", resize);
  window.addEventListener("mousemove", onMouseMove);
  tick();
});

onBeforeUnmount(() => {
  cancelAnimationFrame(raf);
  window.removeEventListener("resize", resize);
  window.removeEventListener("mousemove", onMouseMove);
});
</script>

<style scoped>
.star-field {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
</style>
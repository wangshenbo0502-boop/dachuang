/**
 * 文件名称：studio.ts
 * 文件作用：简历优化 / 成长规划历史 → Studio 显示器塔与 Overlay 结构。
 */

import type {
  GrowthHistoryItem,
  GrowthPlanResponse,
  ResumeHistoryItem,
  ResumeOptimizationResponse,
} from "@/api/types";

export const STUDIO_PLATFORM_CONFIG = {
  resume: {
    color: "#4A90D9",
    accentColor: "#2d6cb5",
    icon: "📄",
    label: "简历优化",
    shape: "monitor",
  },
  growth: {
    color: "#2ECC71",
    accentColor: "#1e8449",
    icon: "🌱",
    label: "成长规划",
    shape: "tv",
  },
} as const;

const RESUME_TEXTURES = [
  "/textures/studio/monitorfront_postnafbdoublewinner.webp",
];
const RESUME_PAINTED = [
  "/textures/studio/monitorfront_postnafbdoublewinner_painted.webp",
];
const GROWTH_TEXTURES = [
  "/textures/studio/tvfront_filmikprojektdlamultiego.webp",
  "/textures/studio/tvfront_filmikedytowaniezdjec.webp",
];
const GROWTH_PAINTED = [
  "/textures/studio/tvfront_filmikprojektdlamultiego_painted.webp",
  "/textures/studio/tvfront_filmikedytowaniezdjec_painted.webp",
];

export type StudioKind = "resume" | "growth" | "create_resume" | "create_growth";

export interface StudioMonitorItem {
  id: string;
  kind: StudioKind;
  recordId: number | null;
  platform: "resume" | "growth";
  title: string;
  description: string;
  date: string;
  views?: string;
  url?: string | null;
  frontTexture: string;
  paintedFrontTexture: string;
  layout: "resume_form" | "growth_form" | "resume_report" | "growth_report";
}

export interface StudioOverlayPayload {
  id: string;
  layout: StudioMonitorItem["layout"];
  title: string;
  description?: string;
  date?: string;
  views?: string;
  loadError?: string | null;
  loadingDetail?: boolean;
  platformConfig: { label: string; color?: string; icon?: string };
  resume?: ResumeOptimizationResponse | null;
  growth?: GrowthPlanResponse | null;
}

function pickTexture(kind: "resume" | "growth", index: number) {
  if (kind === "resume") {
    return {
      frontTexture: RESUME_TEXTURES[index % RESUME_TEXTURES.length],
      paintedFrontTexture: RESUME_PAINTED[index % RESUME_PAINTED.length],
    };
  }
  return {
    frontTexture: GROWTH_TEXTURES[index % GROWTH_TEXTURES.length],
    paintedFrontTexture: GROWTH_PAINTED[index % GROWTH_PAINTED.length],
  };
}

function formatDate(value?: string) {
  return value || "";
}

export function toResumeMonitorItem(item: ResumeHistoryItem, index: number): StudioMonitorItem {
  const score = item.resume_score != null ? `简历评分 ${item.resume_score}` : "简历优化记录";
  return {
    id: `resume-${item.id}`,
    kind: "resume",
    recordId: item.id,
    platform: "resume",
    title: item.target_job || "未指定岗位",
    description: score,
    date: formatDate(item.created_at),
    views: item.resume_score != null ? String(item.resume_score) : undefined,
    url: null,
    layout: "resume_report",
    ...pickTexture("resume", index),
  };
}

export function toGrowthMonitorItem(item: GrowthHistoryItem, index: number): StudioMonitorItem {
  const timeline = item.expected_timeline ? `周期 ${item.expected_timeline}` : "成长规划记录";
  return {
    id: `growth-${item.id}`,
    kind: "growth",
    recordId: item.id,
    platform: "growth",
    title: item.target_job || "未指定岗位",
    description: timeline,
    date: formatDate(item.created_at),
    views: item.expected_timeline || undefined,
    url: null,
    layout: "growth_report",
    ...pickTexture("growth", index),
  };
}

export function buildStudioMonitors(
  resumeHistory: ResumeHistoryItem[] = [],
  growthHistory: GrowthHistoryItem[] = []
): StudioMonitorItem[] {
  const actions: StudioMonitorItem[] = [
    {
      id: "action-resume",
      kind: "create_resume",
      recordId: null,
      platform: "resume",
      title: "生成简历优化",
      description: "填写目标岗位，基于已保存档案生成优化建议。",
      date: "",
      url: null,
      layout: "resume_form",
      ...pickTexture("resume", 0),
    },
    {
      id: "action-growth",
      kind: "create_growth",
      recordId: null,
      platform: "growth",
      title: "生成成长规划",
      description: "填写目标岗位，生成能力差距与学习路线。",
      date: "",
      url: null,
      layout: "growth_form",
      ...pickTexture("growth", 0),
    },
  ];

  const resumes = (resumeHistory || []).map((item, i) => toResumeMonitorItem(item, i + 1));
  const growths = (growthHistory || []).map((item, i) => toGrowthMonitorItem(item, i + 1));

  return [...actions, ...resumes, ...growths].sort((a, b) => {
    if (!a.date) return -1;
    if (!b.date) return 1;
    return new Date(b.date).getTime() - new Date(a.date).getTime();
  });
}

export function toStudioOverlayFromMonitor(item: StudioMonitorItem, extra: Partial<StudioOverlayPayload> = {}): StudioOverlayPayload {
  const platformConfig = STUDIO_PLATFORM_CONFIG[item.platform];
  return {
    id: item.id,
    layout: item.layout,
    title: item.title,
    description: item.description,
    date: item.date,
    views: item.views,
    platformConfig: { label: platformConfig.label, color: platformConfig.color, icon: platformConfig.icon },
    resume: extra.resume ?? null,
    growth: extra.growth ?? null,
    loadError: extra.loadError ?? null,
    loadingDetail: extra.loadingDetail ?? false,
    ...extra,
  };
}

export function toResumeOverlay(detail: ResumeOptimizationResponse): StudioOverlayPayload {
  const r = detail.result;
  const summary = r?.personal_summary || `简历评分 ${r?.resume_score ?? "—"}`;
  return {
    id: `resume-${detail.id}`,
    layout: "resume_report",
    title: detail.target_job || "简历优化",
    description: summary,
    date: detail.created_at,
    views: r?.resume_score != null ? String(r.resume_score) : undefined,
    platformConfig: {
      label: STUDIO_PLATFORM_CONFIG.resume.label,
      color: STUDIO_PLATFORM_CONFIG.resume.color,
      icon: STUDIO_PLATFORM_CONFIG.resume.icon,
    },
    resume: detail,
  };
}

export function toGrowthOverlay(detail: GrowthPlanResponse): StudioOverlayPayload {
  const r = detail.result;
  const summary = r?.current_situation || r?.expected_timeline || "成长规划";
  return {
    id: `growth-${detail.id}`,
    layout: "growth_report",
    title: detail.target_job || "成长规划",
    description: summary,
    date: detail.created_at,
    views: r?.expected_timeline,
    platformConfig: {
      label: STUDIO_PLATFORM_CONFIG.growth.label,
      color: STUDIO_PLATFORM_CONFIG.growth.color,
      icon: STUDIO_PLATFORM_CONFIG.growth.icon,
    },
    growth: detail,
  };
}

/**
 * 文件名称：jobMatch.ts
 * 文件作用：岗位列表/详情/匹配结果 → GlobalOverlay 所需结构；Markdown 轻量文本解析。
 */

import type { JobDetail, JobListItem, MatchItem } from "@/api/types";
import type { OverlayPayload } from "./profile";

export type MarkdownBlock =
  | { type: "h"; level: number; text: string }
  | { type: "p"; text: string }
  | { type: "li"; text: string };

/** 安全轻量 Markdown → 标题/段落/列表（不渲染 HTML） */
export function parseMarkdownLite(content: string): MarkdownBlock[] {
  if (!content?.trim()) return [];
  const blocks: MarkdownBlock[] = [];
  const lines = content.replace(/\r\n/g, "\n").split("\n");

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      blocks.push({ type: "h", level: heading[1].length, text: heading[2].trim() });
      continue;
    }

    const listItem = line.match(/^[-*+]\s+(.+)$/);
    if (listItem) {
      blocks.push({ type: "li", text: listItem[1].trim() });
      continue;
    }

    const ordered = line.match(/^\d+[.)]\s+(.+)$/);
    if (ordered) {
      blocks.push({ type: "li", text: ordered[1].trim() });
      continue;
    }

    blocks.push({ type: "p", text: line });
  }
  return blocks;
}

export interface JobDetailOverlayPayload extends OverlayPayload {
  layout: "job_detail";
  job?: JobDetail | null;
  match?: MatchItem | null;
  blocks?: MarkdownBlock[];
  loadError?: string;
}

export function toJobDetailOverlay(
  job: JobDetail,
  match?: MatchItem | null
): JobDetailOverlayPayload {
  return {
    id: `job-${job.job_id}`,
    layout: "job_detail",
    title: job.title,
    job,
    match: match ?? null,
    blocks: parseMarkdownLite(job.content),
    platformConfig: { label: job.category || "岗位", icon: "📋" },
  };
}

export function toJobDetailErrorOverlay(
  item: Pick<JobListItem, "job_id" | "title" | "category">,
  message: string
): JobDetailOverlayPayload {
  return {
    id: `job-err-${item.job_id}`,
    layout: "job_detail",
    title: item.title,
    job: null,
    match: null,
    blocks: [],
    loadError: message,
    platformConfig: { label: item.category || "岗位", icon: "📋" },
  };
}

/** 卡片展示用的统一结构（browse 与 match 均可映射） */
export interface JobCardView {
  job_id: string;
  title: string;
  category: string;
  tags: string[];
  snippet: string;
  match_score?: number;
  matched_skills?: string[];
  missing_skills?: string[];
}

export function toCardView(item: JobListItem | MatchItem): JobCardView {
  return {
    job_id: item.job_id,
    title: item.title,
    category: item.category,
    tags: item.tags ?? [],
    snippet: item.snippet ?? "",
    match_score: "match_score" in item ? item.match_score : undefined,
    matched_skills: "matched_skills" in item ? item.matched_skills : undefined,
    missing_skills: "missing_skills" in item ? item.missing_skills : undefined,
  };
}

export interface JobMatchPanelOverlayPayload extends OverlayPayload {
  layout: "job_match_panel";
}

export function toJobMatchPanelOverlay(): JobMatchPanelOverlayPayload {
  return {
    id: "job-match-panel",
    layout: "job_match_panel",
    title: "岗位搜索与匹配",
    platformConfig: { label: "岗位匹配", icon: "🔍" },
  };
}

export const JOB_CATEGORIES = [
  "全部",
  "前端",
  "后端",
  "AI",
  "数据",
  "移动端",
  "运维",
  "测试",
  "产品",
  "运营",
  "安全",
] as const;

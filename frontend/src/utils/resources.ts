import type { KnowledgeResult } from "@/types/api";

export function resourceTitle(item: KnowledgeResult) {
  return item.title || String(item.metadata?.title || item.doc_id || "IT 技术资源");
}

export function resourceDate(item: KnowledgeResult) {
  const value = item.metadata?.published_at;
  if (!value) return "未标注发布日期";
  const date = new Date(String(value));
  return Number.isNaN(date.getTime()) ? "未标注发布日期" : date.toLocaleDateString("zh-CN");
}

export function resourceUrl(item: KnowledgeResult) {
  const value = String(item.metadata?.source_url || item.source || "");
  try { const url = new URL(value); return ["https:", "http:"].includes(url.protocol) ? url.href : ""; }
  catch { return ""; }
}

export async function resourceKey(item: KnowledgeResult) {
  const identity = resourceUrl(item) || String(item.document_id || item.doc_id || item.id || resourceTitle(item));
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(identity));
  return Array.from(new Uint8Array(hash), byte => byte.toString(16).padStart(2, "0")).join("");
}

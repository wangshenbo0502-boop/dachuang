import type { ChatMessage } from "@/types/api";

export type AssistantMode = "consult" | "profile";
export type AssistantSuggestedAction = "profile" | "resume" | "analysis" | "growth" | "jobs";

export interface AssistantMessage extends ChatMessage {
  id: string;
  createdAt: string;
  failed?: boolean;
}

export interface AssistantSession {
  id: string;
  title: string;
  mode: AssistantMode;
  target: string;
  consultMessages: AssistantMessage[];
  profileMessages: AssistantMessage[];
  draft: Record<string, any>;
  suggestedAction: AssistantSuggestedAction | null;
  createdAt: string;
  updatedAt: string;
}

export interface AssistantSessionStore {
  version: 3;
  activeId: string;
  sessions: AssistantSession[];
}

export const assistantStorageKey = (userId: number | string) => `ai-career-assistant-v3-${userId}`;

export function createAssistantId() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function createAssistantSession(mode: AssistantMode = "consult"): AssistantSession {
  const now = new Date().toISOString();
  return {
    id: createAssistantId(),
    title: "新对话",
    mode,
    target: "",
    consultMessages: [],
    profileMessages: [],
    draft: {},
    suggestedAction: null,
    createdAt: now,
    updatedAt: now,
  };
}

export function readAssistantSessionStore(userId: number | string): AssistantSessionStore | null {
  try {
    const parsed = JSON.parse(localStorage.getItem(assistantStorageKey(userId)) || "null");
    if (parsed?.version !== 3 || !Array.isArray(parsed.sessions)) return null;
    return parsed as AssistantSessionStore;
  } catch {
    return null;
  }
}

export function writeAssistantSessionStore(userId: number | string, store: AssistantSessionStore) {
  localStorage.setItem(assistantStorageKey(userId), JSON.stringify(store));
  notifyAssistantSessionsUpdated();
}

export function notifyAssistantSessionsUpdated() {
  window.dispatchEvent(new CustomEvent("assistant-sessions-updated"));
}

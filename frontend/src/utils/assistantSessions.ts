import request, { apiData } from "@/api/request";
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

/** 侧边栏只需要的会话摘要，不含消息正文。 */
export type AssistantSessionSummary = Pick<AssistantSession, "id" | "title" | "mode" | "createdAt" | "updatedAt">;

// 对话属于个人隐私，只保存在服务器上并按登录账号隔离；浏览器里只保留当前页面的内存副本，
// 退出登录或切换账号时清空，不写入 localStorage。以下为旧版本使用过的本地存储键，仅用于迁移。
const LEGACY_KEY_PREFIXES = ["ai-career-assistant-v3-", "ai-career-assistant-v2-", "career-copilot-chat-"];

let summaries: AssistantSessionSummary[] = [];
let summariesLoaded = false;
let pendingList: Promise<AssistantSessionSummary[]> | null = null;
const details = new Map<string, AssistantSession>();
const saveChains = new Map<string, Promise<unknown>>();
const saveTimers = new Map<string, ReturnType<typeof setTimeout>>();
let generation = 0;

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

export function notifyAssistantSessionsUpdated() {
  window.dispatchEvent(new CustomEvent("assistant-sessions-updated"));
}

function toSummary(session: AssistantSession): AssistantSessionSummary {
  const { id, title, mode, createdAt, updatedAt } = session;
  return { id, title, mode, createdAt, updatedAt };
}

function upsertSummary(summary: AssistantSessionSummary) {
  summaries = [summary, ...summaries.filter(item => item.id !== summary.id)]
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
  notifyAssistantSessionsUpdated();
}

export function cachedSessionSummaries(): AssistantSessionSummary[] {
  return summaries;
}

export async function listAssistantSessions(force = false): Promise<AssistantSessionSummary[]> {
  if (summariesLoaded && !force) return summaries;
  if (!pendingList) {
    const startedIn = generation;
    pendingList = apiData<AssistantSessionSummary[]>(request.get("/chat/sessions"))
      .then(items => {
        if (startedIn !== generation) return [];
        // 保留本页刚创建、尚未保存成功的会话
        const local = summaries.filter(item => !items.some(remote => remote.id === item.id) && details.has(item.id));
        summaries = [...local, ...items];
        summariesLoaded = true;
        notifyAssistantSessionsUpdated();
        return summaries;
      })
      .finally(() => { pendingList = null; });
  }
  return pendingList;
}

export async function loadAssistantSession(id: string): Promise<AssistantSession | null> {
  const cached = details.get(id);
  if (cached) return cached;
  const startedIn = generation;
  try {
    const session = await apiData<AssistantSession>(request.get(`/chat/sessions/${encodeURIComponent(id)}`));
    if (startedIn !== generation) return null;
    details.set(id, session);
    return session;
  } catch (error: any) {
    if (error?.status === 404) return null;
    throw error;
  }
}

/** 登记一个新建的会话，使侧边栏立即可见；内容在首次 save 时写入服务器。 */
export function registerAssistantSession(session: AssistantSession) {
  details.set(session.id, session);
  upsertSummary(toSummary(session));
}

function payload(session: AssistantSession) {
  const { id: _id, createdAt: _createdAt, updatedAt: _updatedAt, ...body } = session;
  return body;
}

/** 立即保存；同一会话的保存串行执行，避免较旧的内容覆盖较新的内容。 */
export function saveAssistantSession(session: AssistantSession): Promise<void> {
  const timer = saveTimers.get(session.id);
  if (timer) {
    clearTimeout(timer);
    saveTimers.delete(session.id);
  }
  details.set(session.id, session);
  upsertSummary(toSummary(session));
  const startedIn = generation;
  const body = JSON.parse(JSON.stringify(payload(session)));
  const previous = saveChains.get(session.id) || Promise.resolve();
  const next = previous
    .catch(() => undefined)
    .then(() => {
      if (startedIn !== generation) return;
      return request.put(`/chat/sessions/${encodeURIComponent(session.id)}`, body);
    });
  saveChains.set(session.id, next);
  return next.then(() => undefined).finally(() => {
    if (saveChains.get(session.id) === next) saveChains.delete(session.id);
  });
}

/** 防抖保存：流式输出等高频变更合并为一次请求。 */
export function scheduleAssistantSessionSave(session: AssistantSession, delay = 800): Promise<void> {
  details.set(session.id, session);
  upsertSummary(toSummary(session));
  const existing = saveTimers.get(session.id);
  if (existing) clearTimeout(existing);
  return new Promise((resolve, reject) => {
    saveTimers.set(session.id, setTimeout(() => {
      saveTimers.delete(session.id);
      saveAssistantSession(session).then(resolve, reject);
    }, delay));
  });
}

export async function deleteAssistantSession(id: string): Promise<void> {
  const timer = saveTimers.get(id);
  if (timer) clearTimeout(timer);
  saveTimers.delete(id);
  // 等待进行中的保存完成，防止删除后又被写回
  await (saveChains.get(id) || Promise.resolve()).catch(() => undefined);
  await request.delete(`/chat/sessions/${encodeURIComponent(id)}`);
  details.delete(id);
  summaries = summaries.filter(item => item.id !== id);
  notifyAssistantSessionsUpdated();
}

export function normalizeMessages(value: unknown): AssistantMessage[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap(item => {
    if (!item || typeof item !== "object") return [];
    const raw = item as Partial<AssistantMessage>;
    if ((raw.role !== "user" && raw.role !== "assistant") || typeof raw.content !== "string") return [];
    return [{
      role: raw.role,
      content: raw.content,
      failed: Boolean(raw.failed),
      id: typeof raw.id === "string" && raw.id ? raw.id : createAssistantId(),
      createdAt: typeof raw.createdAt === "string" && raw.createdAt ? raw.createdAt : new Date().toISOString(),
    }];
  });
}

export function normalizeSession(value: Partial<AssistantSession>): AssistantSession {
  const fallback = createAssistantSession(value.mode === "profile" ? "profile" : "consult");
  return {
    ...fallback,
    id: typeof value.id === "string" && /^[A-Za-z0-9-]{1,64}$/.test(value.id) ? value.id : fallback.id,
    title: typeof value.title === "string" && value.title.trim() ? value.title.trim().slice(0, 28) : "新对话",
    mode: value.mode === "profile" ? "profile" : "consult",
    target: typeof value.target === "string" ? value.target.slice(0, 100) : "",
    consultMessages: normalizeMessages(value.consultMessages),
    profileMessages: normalizeMessages(value.profileMessages),
    draft: value.draft && typeof value.draft === "object" ? value.draft : {},
    suggestedAction: value.suggestedAction || null,
    createdAt: typeof value.createdAt === "string" ? value.createdAt : fallback.createdAt,
    updatedAt: typeof value.updatedAt === "string" ? value.updatedAt : fallback.updatedAt,
  };
}

function legacySessions(userId: number): AssistantSession[] {
  const read = (key: string) => {
    try { return JSON.parse(localStorage.getItem(key) || "null"); } catch { return null; }
  };
  const v3 = read(`ai-career-assistant-v3-${userId}`);
  if (v3?.version === 3 && Array.isArray(v3.sessions)) return v3.sessions.map(normalizeSession);
  const v2 = read(`ai-career-assistant-v2-${userId}`);
  const v1 = read(`career-copilot-chat-${userId}`);
  const session = createAssistantSession();
  if (v2?.version === 2) {
    session.mode = v2.mode === "profile" ? "profile" : "consult";
    session.target = v2.consult?.target || "";
    session.consultMessages = normalizeMessages(v2.consult?.messages);
    session.profileMessages = normalizeMessages(v2.profile?.messages);
    session.draft = v2.profile?.draft && typeof v2.profile.draft === "object" ? v2.profile.draft : {};
    session.suggestedAction = v2.consult?.suggestedAction || null;
  } else if (v1) {
    session.target = v1.target || "";
    session.consultMessages = normalizeMessages(v1.messages);
  }
  const firstUserMessage = [...session.consultMessages, ...session.profileMessages].find(item => item.role === "user");
  if (!firstUserMessage) return [];
  const title = firstUserMessage.content.replace(/s+/g, " ").trim();
  session.title = title.length > 22 ? `${title.slice(0, 22)}…` : title || "新对话";
  return [session];
}

function legacyKeys(userId: number) {
  return LEGACY_KEY_PREFIXES.map(prefix => `${prefix}${userId}`);
}

/**
 * 旧版本把对话明文存在浏览器里。当前学生登录后，把属于本人的旧对话上传到服务器并从浏览器删除；
 * 上传失败时保留原数据，下次进入再试。其他账号的旧数据等其本人登录时再迁移。
 */
export async function migrateLegacyAssistantStorage(userId: number): Promise<void> {
  let keys: string[];
  try {
    keys = legacyKeys(userId).filter(key => localStorage.getItem(key) !== null);
  } catch {
    return;
  }
  if (!keys.length) return;
  const sessions = legacySessions(userId);
  for (const session of sessions) await saveAssistantSession(session);
  keys.forEach(key => localStorage.removeItem(key));
  if (sessions.length) await listAssistantSessions(true);
}

/** 退出登录或切换账号时调用：清空本页内存中的对话副本。 */
export function clearAssistantSessionCache() {
  generation += 1;
  saveTimers.forEach(timer => clearTimeout(timer));
  saveTimers.clear();
  saveChains.clear();
  details.clear();
  summaries = [];
  summariesLoaded = false;
  pendingList = null;
  notifyAssistantSessionsUpdated();
}

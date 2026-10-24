import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const requestMock = vi.hoisted(() => ({
  get: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}));

vi.mock("@/api/request", () => ({
  default: requestMock,
  apiData: async (promise: Promise<{ data: { data: unknown } }>) => (await promise).data.data,
}));

import {
  cachedSessionSummaries,
  clearAssistantSessionCache,
  createAssistantSession,
  deleteAssistantSession,
  listAssistantSessions,
  loadAssistantSession,
  migrateLegacyAssistantStorage,
  saveAssistantSession,
} from "./assistantSessions";

const ok = (data: unknown) => Promise.resolve({ data: { code: 0, message: "", data } });

beforeEach(() => {
  localStorage.clear();
  clearAssistantSessionCache();
  requestMock.get.mockReset();
  requestMock.put.mockReset().mockImplementation(() => ok({}));
  requestMock.delete.mockReset().mockImplementation(() => ok(null));
});

afterEach(() => vi.useRealTimers());

describe("assistant session storage", () => {
  it("never writes conversations to localStorage", async () => {
    const session = createAssistantSession();
    session.consultMessages.push({ id: "m1", role: "user", content: "我的私人困惑", createdAt: "" });
    await saveAssistantSession(session);
    expect(requestMock.put).toHaveBeenCalledWith(`/chat/sessions/${session.id}`, expect.objectContaining({ title: "新对话" }));
    expect(JSON.stringify({ ...localStorage })).not.toContain("我的私人困惑");
  });

  it("forgets the previous account's conversations on logout", async () => {
    requestMock.get.mockImplementation((url: string) =>
      url === "/chat/sessions"
        ? ok([{ id: "a", title: "A 的对话", mode: "consult", createdAt: "", updatedAt: "" }])
        : ok({ ...createAssistantSession(), id: "a", title: "A 的对话" }),
    );
    await listAssistantSessions();
    await loadAssistantSession("a");
    expect(cachedSessionSummaries()).toHaveLength(1);

    clearAssistantSessionCache();
    expect(cachedSessionSummaries()).toEqual([]);
    requestMock.get.mockImplementation(() => ok([]));
    expect(await listAssistantSessions()).toEqual([]);
    // 缓存已清空，必须重新向服务器请求，而服务器只返回当前账号的数据
    requestMock.get.mockImplementation(() => Promise.reject({ status: 404 }));
    expect(await loadAssistantSession("a")).toBeNull();
  });

  it("drops responses that arrive after the account changed", async () => {
    let resolveList!: (value: unknown) => void;
    requestMock.get.mockImplementation(() => new Promise(resolve => { resolveList = resolve; }));
    const pending = listAssistantSessions();
    clearAssistantSessionCache();
    resolveList({ data: { data: [{ id: "old", title: "旧账号", mode: "consult", createdAt: "", updatedAt: "" }] } });
    await pending;
    expect(cachedSessionSummaries()).toEqual([]);
  });

  it("serializes saves so an older snapshot cannot overwrite a newer one", async () => {
    const order: string[] = [];
    let releaseFirst!: () => void;
    requestMock.put
      .mockImplementationOnce((_url: string, body: { title: string }) => new Promise(resolve => {
        releaseFirst = () => { order.push(body.title); resolve({ data: {} }); };
      }))
      .mockImplementationOnce((_url: string, body: { title: string }) => { order.push(body.title); return ok({}); });
    const session = createAssistantSession();
    session.title = "第一版";
    const first = saveAssistantSession(session);
    session.title = "第二版";
    const second = saveAssistantSession(session);
    await vi.waitFor(() => expect(requestMock.put).toHaveBeenCalledTimes(1));
    // 第一次请求未完成前，第二次保存必须排队等待
    expect(requestMock.put).toHaveBeenCalledTimes(1);
    releaseFirst();
    await Promise.all([first, second]);
    expect(order).toEqual(["第一版", "第二版"]);
  });

  it("deletes on the server and removes the summary", async () => {
    const session = createAssistantSession();
    await saveAssistantSession(session);
    await deleteAssistantSession(session.id);
    expect(requestMock.delete).toHaveBeenCalledWith(`/chat/sessions/${session.id}`);
    expect(cachedSessionSummaries().some(item => item.id === session.id)).toBe(false);
  });
});

describe("legacy localStorage migration", () => {
  it("uploads the student's own old conversations, then removes them from the browser", async () => {
    const legacy = createAssistantSession();
    legacy.title = "旧对话";
    legacy.consultMessages.push({ id: "m1", role: "user", content: "旧版本里的问题", createdAt: "" });
    localStorage.setItem("ai-career-assistant-v3-7", JSON.stringify({ version: 3, activeId: legacy.id, sessions: [legacy] }));
    localStorage.setItem("ai-career-assistant-v3-8", JSON.stringify({ version: 3, activeId: "x", sessions: [] }));
    requestMock.get.mockImplementation(() => ok([]));

    await migrateLegacyAssistantStorage(7);

    expect(requestMock.put).toHaveBeenCalledWith(`/chat/sessions/${legacy.id}`, expect.objectContaining({ title: "旧对话" }));
    expect(localStorage.getItem("ai-career-assistant-v3-7")).toBeNull();
    // 其他账号的旧数据不能被当前账号上传，留给其本人登录时迁移
    expect(localStorage.getItem("ai-career-assistant-v3-8")).not.toBeNull();
  });

  it("keeps the old data if the upload fails", async () => {
    const legacy = createAssistantSession();
    legacy.consultMessages.push({ id: "m1", role: "user", content: "内容", createdAt: "" });
    localStorage.setItem("ai-career-assistant-v3-7", JSON.stringify({ version: 3, activeId: legacy.id, sessions: [legacy] }));
    requestMock.put.mockImplementation(() => Promise.reject(new Error("offline")));
    await expect(migrateLegacyAssistantStorage(7)).rejects.toThrow("offline");
    expect(localStorage.getItem("ai-career-assistant-v3-7")).not.toBeNull();
  });
});

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { consumeSse } from "./sse";
import { setAuthToken } from "./authSession";

function streamResponse(text: string, status = 200) {
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(text));
      controller.close();
    },
  });
  return new Response(body, { status, headers: { "Content-Type": "text/event-stream" } });
}

const event = (type: string, payload: object) => `event: ${type}\ndata: ${JSON.stringify({ type, ...payload })}\n\n`;

beforeEach(() => {
  localStorage.clear();
  window.history.replaceState(null, "", "/coach?session=abc");
});

afterEach(() => vi.unstubAllGlobals());

describe("consumeSse", () => {
  it("dispatches chunk and complete events", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => streamResponse(
      event("start", { message: "思考中" }) + event("chunk", { content: "你好" }) + event("chunk", { content: "，同学" })
        + event("complete", { result: { suggested_action: "resume" } }),
    )));
    const chunks: string[] = [];
    let result: unknown;
    await consumeSse("/chat/conversation-stream", {}, { chunk: c => chunks.push(c), complete: r => { result = r; } });
    expect(chunks.join("")).toBe("你好，同学");
    expect(result).toEqual({ suggested_action: "resume" });
  });

  it("clears the session and redirects to login on 401", async () => {
    setAuthToken("expired-token");
    const assign = vi.fn();
    vi.stubGlobal("location", { ...window.location, pathname: "/coach", search: "?session=abc", hash: "", assign });
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ code: 5102, message: "登录凭证无效" }), { status: 401 })));

    await expect(consumeSse("/chat/conversation-stream", {}, {})).rejects.toMatchObject({ status: 401 });
    expect(localStorage.getItem("employment-platform-access-token")).toBeNull();
    expect(assign).toHaveBeenCalledWith(`/login?redirect=${encodeURIComponent("/coach?session=abc")}`);
  });

  it("shows the server's message for quota errors", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(
      JSON.stringify({ code: 3005, message: "今日 AI 使用次数已达上限（50 次），请明天再试" }), { status: 429 },
    )));
    await expect(consumeSse("/chat/conversation-stream", {}, {})).rejects.toThrow("今日 AI 使用次数已达上限");
  });

  it("reports stream error events", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => streamResponse(event("error", { message: "AI 服务暂时不可用" }))));
    const errors: string[] = [];
    await expect(consumeSse("/x", {}, { error: m => errors.push(m) })).rejects.toThrow();
    expect(errors).toEqual(["AI 服务暂时不可用"]);
  });
});

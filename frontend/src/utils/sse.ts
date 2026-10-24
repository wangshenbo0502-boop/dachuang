import { ApiError } from "@/api/request";
import { getAuthToken, handleUnauthorized } from "@/utils/authSession";

interface SseHandlers<T> {
  start?: (message: string) => void;
  chunk?: (content: string) => void;
  complete?: (result: T | null, raw?: string) => void;
  error?: (message: string) => void;
}

async function failureMessage(response: Response) {
  try {
    const payload = await response.json();
    if (typeof payload?.message === "string" && payload.message) return payload.message;
  } catch {
    // Non-JSON error bodies fall back to the generic message below.
  }
  return `流式请求失败（${response.status}）`;
}

/** POST 一个 SSE 接口并逐个分发 start / chunk / complete / error 事件。 */
export async function consumeSse<T>(path: string, body: object, handlers: SseHandlers<T>, signal?: AbortSignal) {
  const token = getAuthToken();
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || "/api"}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
    signal,
  });
  if (response.status === 401) {
    // 与 axios 拦截器一致：凭证失效时清除登录态并回到登录页
    handleUnauthorized(token);
    throw new ApiError("登录已过期，请重新登录", undefined, 401);
  }
  if (!response.ok || !response.body) {
    // 429（额度用完）、503（预算用完）等返回 JSON 提示，直接展示给用户
    throw new ApiError(await failureMessage(response), undefined, response.status);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let failed = false;
  const dispatch = (block: string) => {
    const data = block.split("\n").find(line => line.startsWith("data:"))?.slice(5).trim();
    if (!data) return;
    let event: any;
    try {
      event = JSON.parse(data);
    } catch {
      return;
    }
    if (event.type === "start") handlers.start?.(event.message);
    if (event.type === "chunk") handlers.chunk?.(event.content);
    if (event.type === "complete") handlers.complete?.(event.result || null, event.raw_text);
    if (event.type === "error") {
      failed = true;
      handlers.error?.(event.message);
    }
  };

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() || "";
    for (const block of blocks) dispatch(block);
    if (done) break;
  }
  if (buffer.trim()) dispatch(buffer);
  if (failed) throw new Error("流式请求处理失败");
}

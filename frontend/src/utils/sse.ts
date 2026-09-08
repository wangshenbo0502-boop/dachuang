/**
 * 文件名称：sse.ts
 * 文件作用：SSE 流式接口消费助手（POST + fetch + ReadableStream）。
 * 用于 /api/stream/analysis、/api/stream/resume、/api/stream/growth，事件契约见 docs/02 第 9 章。
 */

export interface SSEHandlers {
  onStart?: (message: string) => void;
  onChunk?: (content: string) => void;
  onComplete?: (result: unknown, rawText?: string) => void;
  onError?: (message: string) => void;
}

interface SSEResult {
  result?: unknown;
  raw_text?: string;
}

export async function streamSSE(
  path: string,
  body: Record<string, unknown>,
  handlers: SSEHandlers
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    handlers.onError?.("网络错误，无法连接服务");
    return;
  }

  if (!response.ok) {
    if (response.status === 404) {
      handlers.onError?.("学生资料不存在");
    } else {
      handlers.onError?.(`请求失败（HTTP ${response.status}）`);
    }
    return;
  }
  if (!response.body) {
    handlers.onError?.("浏览器不支持流式读取");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const lines = frame.split("\n");
      const event = lines.find((l) => l.startsWith("event:"))?.slice(6).trim() ?? "";
      const dataLine = lines.find((l) => l.startsWith("data:"));
      if (!dataLine) continue;

      let payload: SSEResult & { message?: string; content?: string };
      try {
        payload = JSON.parse(dataLine.slice(5).trim());
      } catch {
        continue;
      }

      if (event === "start") handlers.onStart?.(payload.message ?? "处理开始…");
      else if (event === "chunk") handlers.onChunk?.(payload.content ?? "");
      else if (event === "complete") handlers.onComplete?.(payload.result, payload.raw_text);
      else if (event === "error") handlers.onError?.(payload.message ?? "AI 服务异常");
    }
  }
}
import type { HealthResponse, SessionInfo, SseEvent } from "../types/chat";

const API_BASE = "/api/v1";

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend unavailable");
  return res.json();
}

export async function fetchSession(): Promise<SessionInfo> {
  const res = await fetch(`${API_BASE}/chat/sessions`);
  if (!res.ok) throw new Error("Failed to load session");
  return res.json();
}

export async function resetSession(): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/reset`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reset session");
}

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onMetadata: (nodes: string[]) => void;
  onError: (message: string) => void;
  onDone: () => void;
}

export async function streamChatMessage(
  message: string,
  callbacks: StreamCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const event = JSON.parse(line.slice(6)) as SseEvent;

      if (event.type === "token") callbacks.onToken(event.content);
      if (event.type === "metadata") callbacks.onMetadata(event.nodes ?? []);
      if (event.type === "error") callbacks.onError(event.content);
      if (event.type === "done") callbacks.onDone();
    }
  }
}

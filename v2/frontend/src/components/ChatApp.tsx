import { useCallback, useEffect, useRef, useState } from "react";
import {
  checkHealth,
  fetchSession,
  resetSession,
  streamChatMessage,
} from "../api/chat";
import type { ChatMessage } from "../types/chat";
import { MessageBubble } from "./MessageBubble";

function uid(): string {
  return crypto.randomUUID();
}

export function ChatApp() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeDomain, setActiveDomain] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadSession = useCallback(async () => {
    try {
      const session = await fetchSession();
      if (session.exists && session.messages) {
        setMessages(
          session.messages.map((m) => ({
            id: uid(),
            role: m.role,
            content: m.content,
          })),
        );
        setActiveDomain(session.session?.active_domain ?? null);
      }
    } catch {
      /* empty session on first load */
    }
  }, []);

  useEffect(() => {
    checkHealth()
      .then(() => {
        setConnected(true);
        return loadSession();
      })
      .catch(() => setConnected(false));
  }, [loadSession]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleNewChat = async () => {
    abortRef.current?.abort();
    await resetSession();
    setMessages([]);
    setActiveDomain(null);
    setError(null);
    setInput("");
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading || !connected) return;

    setError(null);
    setInput("");
    setLoading(true);

    const userMsg: ChatMessage = { id: uid(), role: "user", content: text };
    const assistantId = uid();
    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: assistantId, role: "assistant", content: "", streaming: true },
    ]);

    abortRef.current = new AbortController();
    let content = "";

    try {
      await streamChatMessage(
        text,
        {
          onToken: (token) => {
            content += token;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content, streaming: true } : m,
              ),
            );
          },
          onMetadata: (nodes) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content, route: nodes, streaming: false }
                  : m,
              ),
            );
            if (nodes.includes("finance")) setActiveDomain("finance");
            if (nodes.includes("marketing")) setActiveDomain("marketing");
            if (nodes.includes("terminal")) {
              setActiveDomain(null);
              void loadSession();
            }
          },
          onError: (msg) => setError(msg),
          onDone: () => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, streaming: false } : m,
              ),
            );
          },
        },
        abortRef.current.signal,
      );
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setError((err as Error).message);
        setMessages((prev) => prev.filter((m) => m.id !== assistantId));
      }
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Analytics Copilot</h1>
          <p className="subtitle">Finance & Marketing multi-agent assistant</p>
        </div>
        <div className="header-actions">
          <span className={`status-pill ${connected ? "online" : "offline"}`}>
            {connected ? "Connected" : "Offline"}
          </span>
          {activeDomain && (
            <span className="domain-pill">{activeDomain} domain</span>
          )}
          <button type="button" className="btn secondary" onClick={() => void handleNewChat()}>
            New chat
          </button>
        </div>
      </header>

      <main className="chat-panel">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>Ask about Finance or Marketing data</h2>
            <p>Try: &quot;Give me a statement&quot; or &quot;Show me CAC trends&quot;</p>
            <p className="hint">Say &quot;I am done, thank you&quot; to end the session.</p>
          </div>
        ) : (
          messages.map((m) => <MessageBubble key={m.id} message={m} />)
        )}
        <div ref={bottomRef} />
      </main>

      {error && <div className="error-banner">{error}</div>}

      <footer className="input-bar">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            connected
              ? "Type your message… (Enter to send, Shift+Enter for new line)"
              : "Start the backend: uvicorn app.main:app --reload"
          }
          disabled={!connected || loading}
          rows={2}
        />
        <button
          type="button"
          className="btn primary"
          onClick={() => void handleSend()}
          disabled={!connected || loading || !input.trim()}
        >
          {loading ? "Sending…" : "Send"}
        </button>
      </footer>
    </div>
  );
}

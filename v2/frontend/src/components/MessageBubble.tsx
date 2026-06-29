import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../types/chat";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const hasTable = !isUser && message.content.includes("|");

  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}${hasTable ? " has-table" : ""}`}>
      <div className="message-meta">
        <span className="message-role">{isUser ? "You" : "Copilot"}</span>
        {!isUser && message.route && message.route.length > 0 && (
          <span className="message-route">{message.route.join(" → ")}</span>
        )}
      </div>
      <div className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}>
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({ children }) => (
                <div className="table-wrap">
                  <table>{children}</table>
                </div>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
        {message.streaming && <span className="cursor-blink">▍</span>}
      </div>
    </div>
  );
}

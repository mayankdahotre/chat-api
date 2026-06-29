export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  route?: string[];
  streaming?: boolean;
}

export type SseEventType = "start" | "token" | "metadata" | "done" | "error";

export interface SseEvent {
  type: SseEventType;
  content: string;
  nodes?: string[];
}

export interface SessionInfo {
  exists: boolean;
  session?: {
    active_domain: string | null;
    is_active: number;
    created_at: string;
    updated_at: string;
  };
  messages?: Array<{
    role: MessageRole;
    content: string;
    created_at: string;
  }>;
}

export interface HealthResponse {
  status: string;
  version: string;
}

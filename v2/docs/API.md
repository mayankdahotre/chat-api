# API Reference

Base URL: `http://localhost:8000/api/v1`

All endpoints return JSON unless noted. The chat endpoint streams **Server-Sent Events (SSE)**.

---

## Health Check

### `GET /health`

Returns server status.

**Response `200 OK`**

```json
{
  "status": "ok",
  "version": "2.0.0"
}
```

**Example**

```powershell
curl http://localhost:8000/api/v1/health
```

---

## Streaming Chat

### `POST /chat/stream`

Send a user message and receive a streamed AI response via SSE.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User message (min 1 character) |
| `thread_id` | string | No | Conversation thread UUID. Auto-generated if omitted. |

**Request Example**

```json
{
  "message": "Give me a financial statement table.",
  "thread_id": "2bf8a02c-2dc0-4ab6-8a59-db580a6eeab9"
}
```

**Response**

- **Content-Type:** `text/event-stream`
- **Header:** `X-Thread-Id` — the conversation thread ID (use this for follow-up messages)

**SSE Event Stream**

Each line is a Server-Sent Event in the format:

```
data: {"type": "<event_type>", "content": "<payload>", ...}

```

| Event Type | Description | Extra Fields |
|------------|-------------|--------------|
| `start` | Stream opened | `thread_id` |
| `token` | Partial response text | `content` |
| `metadata` | Graph execution complete | `nodes`, `thread_id` |
| `done` | Stream closed | — |
| `error` | Error (e.g. ended session) | `content` |

**Full Example Stream**

```
data: {"type": "start", "content": "", "thread_id": "abc-123"}

data: {"type": "token", "content": "Here is your "}

data: {"type": "token", "content": "financial statement table:\n\n"}

data: {"type": "token", "content": "## Financial Statement Summary\n\n..."}

data: {"type": "metadata", "content": "", "nodes": ["intent", "finance"], "thread_id": "abc-123"}

data: {"type": "done", "content": ""}
```

**cURL Example**

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me a financial statement table."}'
```

**PowerShell Example**

```powershell
$body = @{ message = "Give me a financial statement table." } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/chat/stream" `
  -Method POST -ContentType "application/json" -Body $body
```

**Python Example**

```python
import httpx
import json

with httpx.Client() as client:
    with client.stream(
        "POST",
        "http://localhost:8000/api/v1/chat/stream",
        json={"message": "Give me a financial statement table."},
    ) as response:
        thread_id = response.headers["x-thread-id"]
        for line in response.iter_lines():
            if line.startswith("data: "):
                event = json.loads(line[6:])
                if event["type"] == "token":
                    print(event["content"], end="", flush=True)
        print(f"\nThread: {thread_id}")
```

**JavaScript (Browser) Example**

```javascript
const response = await fetch("http://localhost:8000/api/v1/chat/stream", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "Give me a financial statement table." }),
});

const threadId = response.headers.get("X-Thread-Id");
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const text = decoder.decode(value);
  for (const line of text.split("\n")) {
    if (line.startsWith("data: ")) {
      const event = JSON.parse(line.slice(6));
      if (event.type === "token") process.stdout.write(event.content);
    }
  }
}
```

---

## Session History

### `GET /chat/sessions/{thread_id}`

Retrieve session metadata and full message history for a thread.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `thread_id` | string | Conversation thread UUID |

**Response `200 OK` — Session exists**

```json
{
  "thread_id": "2bf8a02c-2dc0-4ab6-8a59-db580a6eeab9",
  "exists": true,
  "session": {
    "thread_id": "2bf8a02c-2dc0-4ab6-8a59-db580a6eeab9",
    "active_domain": "marketing",
    "is_active": 1,
    "created_at": "2025-06-25 03:58:55",
    "updated_at": "2025-06-25 04:01:12"
  },
  "messages": [
    {
      "role": "user",
      "content": "Give me a financial statement table.",
      "created_at": "2025-06-25 03:58:56"
    },
    {
      "role": "assistant",
      "content": "Here is your financial statement table:\n\n## Financial Statement Summary\n...",
      "created_at": "2025-06-25 03:58:57"
    }
  ]
}
```

**Response `200 OK` — Session not found**

```json
{
  "thread_id": "unknown-id",
  "exists": false
}
```

**Example**

```powershell
curl http://localhost:8000/api/v1/chat/sessions/2bf8a02c-2dc0-4ab6-8a59-db580a6eeab9
```

---

## Multi-Turn Conversation Pattern

Always pass the same `thread_id` across turns to maintain session context:

```
Turn 1: POST /chat/stream  { "message": "Give me a financial statement table." }
        → Save thread_id from X-Thread-Id header

Turn 2: POST /chat/stream  { "message": "Why is COGS high in Q2?", "thread_id": "<saved>" }
        → Finance self-loop (nodes: ["finance"])

Turn 3: POST /chat/stream  { "message": "Show me marketing performance instead.", "thread_id": "<saved>" }
        → Domain shift (nodes: ["intent", "marketing"])

Turn 4: POST /chat/stream  { "message": "I am done, thank you.", "thread_id": "<saved>" }
        → Session end (nodes: ["marketing", "terminal"])
        → is_active becomes 0
```

---

## Error Handling

| Scenario | SSE Event | HTTP Status |
|----------|-----------|-------------|
| Message to ended session | `{"type": "error", "content": "Session has ended..."}` | 200 |
| Empty message | Validation error | 422 |
| Server error | Connection dropped | 500 |

After a session is terminated (`is_active = 0`), further messages on the same `thread_id` return an error event. Start a new conversation by omitting `thread_id`.

---

## Interactive Documentation

FastAPI auto-generates interactive docs:

| URL | Format |
|-----|--------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/openapi.json | OpenAPI 3.0 spec |

import json
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage

from app.chat.graph import copilot_graph
from app.chat.state import CopilotState
from app.config import get_settings
from app.crud.app_session import ensure_session, get_session, reset_session, save_message


def _sse_event(event_type: str, content: str, **extra) -> str:
    payload = {"type": event_type, "content": content, **extra}
    return f"data: {json.dumps(payload)}\n\n"


async def _tokenize_response(text: str, chunk_size: int = 12) -> AsyncGenerator[str, None]:
    words = text.split(" ")
    buffer: list[str] = []
    char_count = 0

    for word in words:
        buffer.append(word)
        char_count += len(word) + 1
        if char_count >= chunk_size:
            yield " ".join(buffer) + " "
            buffer = []
            char_count = 0

    if buffer:
        yield " ".join(buffer)


async def stream_chat(user_input: str) -> AsyncGenerator[str, None]:
    session_id = get_settings().default_session_id
    await ensure_session(session_id)
    session = await get_session(session_id)

    active_domain = session["active_domain"] if session else None

    await save_message(session_id, "user", user_input)

    initial_state: CopilotState = {
        "messages": [HumanMessage(content=user_input)],
        "thread_id": session_id,
        "user_input": user_input,
        "intent": "continue",
        "active_domain": active_domain,
        "response_text": "",
        "route_to": "intent",
        "session_active": True,
    }

    yield _sse_event("start", "")

    final_response = ""
    visited_nodes: list[str] = []
    final_intent = "continue"
    session_active = True

    async for event in copilot_graph.astream(initial_state):
        for node_name, node_output in event.items():
            visited_nodes.append(node_name)
            response_text = node_output.get("response_text", "")
            if response_text:
                final_response = response_text
            if "intent" in node_output:
                final_intent = node_output["intent"]
            if "session_active" in node_output:
                session_active = node_output["session_active"]

    if final_response:
        async for token in _tokenize_response(final_response):
            yield _sse_event("token", token)

        session_ended = final_intent == "terminate" and "terminal" in visited_nodes
        if session_ended:
            await reset_session(session_id)
        else:
            await save_message(session_id, "assistant", final_response.strip())

    yield _sse_event("metadata", "", nodes=visited_nodes)
    yield _sse_event("done", "")

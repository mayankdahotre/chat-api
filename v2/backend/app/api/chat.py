from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.chat.sse import stream_chat
from app.config import get_settings
from app.crud.app_session import get_messages, get_session, reset_session

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        stream_chat(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/chat/reset")
async def reset_chat_session():
    session_id = get_settings().default_session_id
    await reset_session(session_id)
    return {"status": "ok", "message": "Conversation reset."}


@router.get("/chat/sessions")
async def get_chat_session():
    session_id = get_settings().default_session_id
    session = await get_session(session_id)
    if not session:
        return {"exists": False}
    messages = await get_messages(session_id)
    return {
        "exists": True,
        "session": session,
        "messages": messages,
    }


@router.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}

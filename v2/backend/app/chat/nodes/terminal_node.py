from langchain_core.messages import AIMessage

from app.chat.state import CopilotState


async def terminal_node(state: CopilotState) -> dict:
    intent = state.get("intent", "terminate")

    if intent == "ambiguous":
        message = (
            "I'm not sure how to help with that request. I specialize in:\n\n"
            "- **Finance**: financial statements, revenue, COGS, balance sheets\n"
            "- **Marketing**: campaign performance, CAC, LTV, ROAS, CTR\n\n"
            "Please ask a question related to one of these domains, or say "
            "\"I'm done\" when you're finished."
        )
        session_active = True
    else:
        message = (
            "Thank you for using the Analytics Copilot. "
            "Your session has been wrapped up. Feel free to start a new conversation anytime."
        )
        session_active = False

    return {
        "intent": intent,
        "response_text": message,
        "route_to": "end",
        "session_active": session_active,
        "active_domain": None,
        "messages": [AIMessage(content=message)],
    }

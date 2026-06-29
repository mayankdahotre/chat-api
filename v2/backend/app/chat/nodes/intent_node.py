from langchain_core.messages import AIMessage

from app.chat.intent import CLARIFICATION_MESSAGE, classify_intent
from app.chat.state import CopilotState
from app.crud.app_session import update_session_domain


async def intent_node(state: CopilotState) -> dict:
    user_input = state["user_input"]
    active_domain = state.get("active_domain")

    intent = classify_intent(user_input, active_domain)

    if intent == "clarify_domain":
        return {
            "intent": intent,
            "active_domain": None,
            "route_to": "end",
            "response_text": CLARIFICATION_MESSAGE,
            "messages": [AIMessage(content=CLARIFICATION_MESSAGE)],
            "session_active": True,
        }

    route_map = {
        "finance_statement": "finance",
        "marketing_statement": "marketing",
        "terminate": "terminal",
        "shift_to_finance": "finance",
        "shift_to_marketing": "marketing",
        "ambiguous": "terminal",
        "continue": active_domain or "terminal",
    }

    route_to = route_map.get(intent, "terminal")

    # Stay in active domain for follow-ups instead of hitting terminal
    if intent == "ambiguous" and active_domain in ("finance", "marketing"):
        route_to = active_domain

    if intent in ("finance_statement", "shift_to_finance"):
        await update_session_domain(state["thread_id"], "finance")
        active_domain = "finance"
    elif intent in ("marketing_statement", "shift_to_marketing"):
        await update_session_domain(state["thread_id"], "marketing")
        active_domain = "marketing"

    return {
        "intent": intent,
        "active_domain": active_domain,
        "route_to": route_to,
        "session_active": intent != "terminate",
    }

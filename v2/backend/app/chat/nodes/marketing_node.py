from langchain_core.messages import AIMessage

from app.chat.intent import classify_intent
from app.chat.state import CopilotState
from app.crud.marketing import answer_marketing_question, build_marketing_statement_markdown


async def marketing_node(state: CopilotState) -> dict:
    user_input = state["user_input"]
    intent = state.get("intent", "")

    # Re-check intent for domain switches when entered via self-loop
    if intent in ("continue", ""):
        intent = classify_intent(user_input, "marketing")

    if intent == "shift_to_finance":
        return {
            "response_text": "",
            "route_to": "intent",
            "intent": "shift_to_finance",
            "active_domain": None,
        }

    if intent == "terminate":
        return {
            "response_text": "",
            "route_to": "terminal",
            "intent": "terminate",
            "session_active": False,
        }

    if intent in ("marketing_statement", "shift_to_marketing"):
        response = await build_marketing_statement_markdown()
        response = (
            "Switching to the **Marketing** domain. "
            "Here is your marketing performance statement:\n\n" + response
            if intent == "shift_to_marketing"
            else "Here is your marketing performance statement:\n\n" + response
        )
    else:
        response = await answer_marketing_question(user_input)

    return {
        "response_text": response,
        "route_to": "end",
        "active_domain": "marketing",
        "messages": [AIMessage(content=response)],
        "session_active": True,
    }

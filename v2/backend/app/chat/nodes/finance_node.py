from langchain_core.messages import AIMessage

from app.chat.intent import classify_intent
from app.chat.state import CopilotState
from app.crud.finance import answer_finance_question, build_financial_statement_markdown


async def finance_node(state: CopilotState) -> dict:
    user_input = state["user_input"]
    intent = state.get("intent", "")

    # Re-check intent for domain switches when entered via self-loop
    if intent in ("continue", ""):
        intent = classify_intent(user_input, "finance")

    if intent == "shift_to_marketing":
        return {
            "response_text": "",
            "route_to": "intent",
            "intent": "shift_to_marketing",
            "active_domain": None,
        }

    if intent == "terminate":
        return {
            "response_text": "",
            "route_to": "terminal",
            "intent": "terminate",
            "session_active": False,
        }

    if intent in ("finance_statement", "shift_to_finance"):
        response = await build_financial_statement_markdown()
        response = (
            "Switching to the **Finance** domain. "
            "Here is your financial statement table:\n\n" + response
            if intent == "shift_to_finance"
            else "Here is your financial statement table:\n\n" + response
        )
    else:
        response = await answer_finance_question(user_input)

    return {
        "response_text": response,
        "route_to": "end",
        "active_domain": "finance",
        "messages": [AIMessage(content=response)],
        "session_active": True,
    }

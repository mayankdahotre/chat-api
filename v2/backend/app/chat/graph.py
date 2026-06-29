from langgraph.graph import END, StateGraph

from app.chat.intent import (
    _is_domain_switch_request,
    _is_generic_statement_request,
    _mentions_finance,
    _mentions_marketing,
    classify_domain_intent,
)
from app.chat.nodes.finance_node import finance_node
from app.chat.nodes.intent_node import intent_node
from app.chat.nodes.marketing_node import marketing_node
from app.chat.nodes.terminal_node import terminal_node
from app.chat.state import CopilotState


def _needs_intent_routing(state: CopilotState) -> bool:
    """Send to Intent when domain is unclear or user wants to switch."""
    user_input = state.get("user_input", "")
    active_domain = state.get("active_domain")

    if _is_generic_statement_request(user_input):
        return True
    if _is_domain_switch_request(user_input):
        return True
    if active_domain == "finance" and _mentions_marketing(user_input) and not _mentions_finance(user_input):
        return True
    if active_domain == "marketing" and _mentions_finance(user_input) and not _mentions_marketing(user_input):
        return True
    return False


def _route_entry(state: CopilotState) -> str:
    """Route active sessions directly to domain nodes (Node 2/3 self-loop on new turns)."""
    active_domain = state.get("active_domain")
    user_input = state.get("user_input", "")

    if _needs_intent_routing(state):
        return "intent"

    if active_domain == "finance":
        domain_intent = classify_domain_intent(user_input, "finance")
        if domain_intent in ("continue", "terminate"):
            return "finance"
        return "intent"

    if active_domain == "marketing":
        domain_intent = classify_domain_intent(user_input, "marketing")
        if domain_intent in ("continue", "terminate"):
            return "marketing"
        return "intent"

    return "intent"


def _route_from_intent(state: CopilotState) -> str:
    route = state.get("route_to", "terminal")
    if route == "finance":
        return "finance"
    if route == "marketing":
        return "marketing"
    if route == "end":
        return "end"
    return "terminal"


def _route_from_finance(state: CopilotState) -> str:
    route = state.get("route_to", "end")
    if route == "intent":
        return "intent"
    if route == "terminal":
        return "terminal"
    return "end"


def _route_from_marketing(state: CopilotState) -> str:
    route = state.get("route_to", "end")
    if route == "intent":
        return "intent"
    if route == "terminal":
        return "terminal"
    return "end"


def build_graph():
    """
    4-Node Topology:
      Node 1 (intent)    -> finance | marketing | terminal
      Node 2 (finance)   -> intent (shift) | terminal | END
      Node 3 (marketing) -> intent (shift) | terminal | END
      Node 4 (terminal)  -> END

    Self-loop (Node 2->2, Node 3->3) is achieved via conditional entry routing
    on subsequent turns when active_domain is set.
    """
    graph = StateGraph(CopilotState)

    graph.add_node("intent", intent_node)
    graph.add_node("finance", finance_node)
    graph.add_node("marketing", marketing_node)
    graph.add_node("terminal", terminal_node)

    graph.set_conditional_entry_point(
        _route_entry,
        {
            "intent": "intent",
            "finance": "finance",
            "marketing": "marketing",
        },
    )

    graph.add_conditional_edges(
        "intent",
        _route_from_intent,
        {
            "finance": "finance",
            "marketing": "marketing",
            "terminal": "terminal",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "finance",
        _route_from_finance,
        {
            "intent": "intent",
            "terminal": "terminal",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "marketing",
        _route_from_marketing,
        {
            "intent": "intent",
            "terminal": "terminal",
            "end": END,
        },
    )

    graph.add_edge("terminal", END)

    return graph.compile()


copilot_graph = build_graph()

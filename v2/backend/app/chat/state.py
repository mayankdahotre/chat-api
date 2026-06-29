import operator
from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

IntentType = Literal[
    "finance_statement",
    "marketing_statement",
    "terminate",
    "continue",
    "shift_to_finance",
    "shift_to_marketing",
    "clarify_domain",
    "ambiguous",
]

DomainType = Literal["finance", "marketing", None]


class CopilotState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    thread_id: str
    user_input: str
    intent: IntentType
    active_domain: DomainType
    response_text: str
    route_to: str
    session_active: bool

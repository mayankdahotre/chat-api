import re

from app.chat.state import DomainType, IntentType

TERMINATE_PATTERNS = [
    r"\b(done|finished|no more questions|that'?s all|thank you|thanks|goodbye|bye)\b",
    r"\bi am done\b",
    r"\bno further questions\b",
]

FINANCE_SPECIFIC_PATTERNS = [
    r"\bfinanc\w*\b",
    r"\brevenue\b",
    r"\bcogs\b",
    r"\bbalance sheet\b",
    r"\baccounting\b",
    r"\bnet income\b",
    r"\bgross profit\b",
    r"\boperating expenses?\b",
    r"\bledger\b",
    r"\bincome statement\b",
    r"\bprofit and loss\b",
    r"\bp&l\b",
]

MARKETING_SPECIFIC_PATTERNS = [
    r"\bmarket\w*\b",
    r"\bcac\b",
    r"\bltv\b",
    r"\broas\b",
    r"\bctr\b",
    r"\bcampaign\b",
    r"\bacquisition\b",
    r"\bclick.?through\b",
    r"\bcustomer acquisition\b",
    r"\bad spend\b",
]

GENERIC_STATEMENT_PATTERNS = [
    r"\bfinanc\w*\s+state?m?ents?\b",
    r"\bperformance state?m?ents?\b",
    r"\bstate?m?ents?\s+table\b",
    r"\b(give|giev|show|get|display|provide|pleas\w*)\b.*\b(table|state?m?ents?|report)\b",
    r"\b(table|state?m?ents?|report)\b.*\b(give|giev|show|get|display|provide|pleas\w*)\b",
    r"^(state?m?ents?|report|table)s?$",
    r"\bthe state?m?ents?\b",
]

DOMAIN_SWITCH_PATTERNS = [
    r"\b(switch|change|move|go)\b.*\b(finance|marketing|route|domain)\b",
    r"\b(finance|marketing)\b.*\b(instead|rather)\b",
    r"\binstead\b.*\b(finance|marketing)\b",
    r"\bchange\b.*\broute\b",
]

DOMAIN_CHOICE_FINANCE = [
    r"^(finance|financial|1|option 1|first)$",
    r"\bfinance domain\b",
    r"\bfor finance\b",
    r"\bi want finance\b",
    r"\bchoose finance\b",
]

DOMAIN_CHOICE_MARKETING = [
    r"^(marketing|2|option 2|second)$",
    r"\bmarketing domain\b",
    r"\bfor marketing\b",
    r"\bi want marketing\b",
    r"\bchoose marketing\b",
]

CLARIFICATION_MESSAGE = (
    "I'd be happy to pull a statement for you. Which domain would you like?\n\n"
    "1. **Finance** — financial statement (revenue, COGS, net income, balance sheet)\n"
    "2. **Marketing** — marketing performance statement (CAC, LTV, ROAS, CTR, campaigns)\n\n"
    "Please reply with **Finance** or **Marketing**."
)


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_finance(text: str) -> bool:
    return _matches_any(text, FINANCE_SPECIFIC_PATTERNS)


def _mentions_marketing(text: str) -> bool:
    return _matches_any(text, MARKETING_SPECIFIC_PATTERNS)


def _is_domain_switch_request(text: str) -> bool:
    return _matches_any(text, DOMAIN_SWITCH_PATTERNS)


def _is_domain_choice_finance(text: str) -> bool:
    return _matches_any(text, DOMAIN_CHOICE_FINANCE)


def _is_domain_choice_marketing(text: str) -> bool:
    return _matches_any(text, DOMAIN_CHOICE_MARKETING)


def _is_generic_statement_request(text: str) -> bool:
    return _matches_any(text, GENERIC_STATEMENT_PATTERNS)


def _is_financial_statement_phrase(text: str) -> bool:
    return bool(re.search(r"\bfinanc\w*\s+stat\w+\b", text, re.IGNORECASE))


def _is_explicit_finance_statement(text: str) -> bool:
    """User said 'finance statement' (domain named), not just 'financial statement'."""
    return bool(re.search(r"\bfinance\s+stat\w+\b", text, re.IGNORECASE))


def _wants_finance_domain(text: str) -> bool:
    if _is_explicit_finance_statement(text):
        return True
    return _is_domain_choice_finance(text) or (
        _mentions_finance(text)
        and not _mentions_marketing(text)
        and not _is_financial_statement_phrase(text)
    )


def _wants_marketing_domain(text: str) -> bool:
    return _is_domain_choice_marketing(text) or (
        _mentions_marketing(text) and not _mentions_finance(text)
    )


def classify_intent(user_input: str, active_domain: DomainType = None) -> IntentType:
    text = user_input.strip().lower()

    if _matches_any(text, TERMINATE_PATTERNS):
        return "terminate"

    is_finance = _mentions_finance(text)
    is_marketing = _mentions_marketing(text)
    is_generic = _is_generic_statement_request(text)
    is_switch = _is_domain_switch_request(text)

    # "financial statement" (ambiguous) → clarify unless domain already switching
    if _is_financial_statement_phrase(text) and not _is_explicit_finance_statement(text):
        if active_domain == "marketing":
            return "shift_to_finance" if _is_explicit_finance_statement(text) else "clarify_domain"
        if active_domain == "finance":
            return "continue"
        return "clarify_domain"

    # Domain switch takes priority when already in a session
    if active_domain == "marketing" and _wants_finance_domain(text):
        return "shift_to_finance"
    if active_domain == "finance" and _wants_marketing_domain(text):
        return "shift_to_marketing"

    if _is_domain_choice_finance(text) and not _is_domain_choice_marketing(text):
        return "finance_statement"
    if _is_domain_choice_marketing(text) and not _is_domain_choice_finance(text):
        return "marketing_statement"

    # Generic statement without a clear domain → ask Finance or Marketing
    if is_generic and not is_finance and not is_marketing:
        return "clarify_domain"

    # "change route" / "switch domain" without naming a domain → clarify
    if is_switch and not is_finance and not is_marketing:
        return "clarify_domain"

    if active_domain == "finance":
        if is_marketing and not is_finance:
            return "shift_to_marketing"
        if is_finance or _is_follow_up(text):
            return "continue"
        if is_marketing:
            return "shift_to_marketing"

    if active_domain == "marketing":
        if is_finance and not is_marketing:
            return "shift_to_finance"
        if is_marketing or _is_follow_up(text):
            return "continue"
        if is_finance:
            return "shift_to_finance"

    if is_finance and is_marketing:
        if "marketing" in text or "market" in text:
            return "marketing_statement"
        return "finance_statement"

    if is_finance and not is_marketing:
        return "finance_statement"
    if is_marketing and not is_finance:
        return "marketing_statement"

    if active_domain and _is_follow_up(text):
        return "continue"

    return "ambiguous"


def classify_domain_intent(user_input: str, domain: DomainType) -> IntentType:
    return classify_intent(user_input, domain)


def _is_follow_up(text: str) -> bool:
    follow_up_signals = [
        r"\bwhy\b",
        r"\bhow\b",
        r"\bwhat\b",
        r"\bexplain\b",
        r"\btell me\b",
        r"\bmore\b",
        r"\bdetails?\b",
        r"\bbreakdown\b",
        r"\bcompare\b",
        r"\bvs\b",
        r"\bhighest\b",
        r"\blowest\b",
        r"\btrend\b",
        r"\bimprove\b",
        r"\bq[1-4]\b",
    ]
    return _matches_any(text, follow_up_signals)

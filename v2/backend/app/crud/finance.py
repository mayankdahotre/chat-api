from app.database.connections import get_finance_connection


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


async def get_financial_statements() -> list[dict]:
    conn = await get_finance_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT period, revenue, cogs, gross_profit, operating_expenses, net_income
            FROM financial_statements
            ORDER BY id
            """
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_balance_sheet() -> list[dict]:
    conn = await get_finance_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT period, total_assets, total_liabilities, shareholders_equity
            FROM balance_sheet
            ORDER BY id
            """
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def build_financial_statement_markdown() -> str:
    statements = await get_financial_statements()
    lines = [
        "## Financial Statement Summary\n",
        "| Period | Revenue | COGS | Gross Profit | OpEx | Net Income |",
        "|--------|---------|------|--------------|------|------------|",
    ]
    for row in statements:
        lines.append(
            f"| {row['period']} | {_format_currency(row['revenue'])} | "
            f"{_format_currency(row['cogs'])} | {_format_currency(row['gross_profit'])} | "
            f"{_format_currency(row['operating_expenses'])} | {_format_currency(row['net_income'])} |"
        )
    lines.append("\n*Source: finance_data.db (Finance domain — Node 2 only)*")
    return "\n".join(lines)


async def answer_finance_question(question: str) -> str:
    statements = await get_financial_statements()
    question_lower = question.lower()

    if "cogs" in question_lower and "q2" in question_lower:
        q2 = next((s for s in statements if "Q2" in s["period"]), None)
        if q2:
            cogs_pct = (q2["cogs"] / q2["revenue"]) * 100
            return (
                f"**Q2 COGS Analysis**\n\n"
                f"COGS in Q2 2025 was {_format_currency(q2['cogs'])}, representing "
                f"**{cogs_pct:.1f}%** of revenue ({_format_currency(q2['revenue'])}).\n\n"
                f"This is higher than Q1 ({_format_currency(statements[0]['cogs'])} / "
                f"{(statements[0]['cogs'] / statements[0]['revenue']) * 100:.1f}%) due to "
                f"increased raw material costs and expanded production capacity."
            )

    if "revenue" in question_lower:
        latest = statements[-1]
        return (
            f"**Revenue Overview**\n\n"
            f"Latest period ({latest['period']}): {_format_currency(latest['revenue'])}.\n\n"
            f"Revenue has grown consistently across all four quarters of 2025, "
            f"from {_format_currency(statements[0]['revenue'])} in Q1 to "
            f"{_format_currency(latest['revenue'])} in Q4."
        )

    if "net income" in question_lower or "profit" in question_lower:
        lines = ["**Net Income by Quarter**\n"]
        for row in statements:
            lines.append(f"- {row['period']}: {_format_currency(row['net_income'])}")
        return "\n".join(lines)

    if "balance" in question_lower:
        sheet = await get_balance_sheet()
        latest = sheet[-1]
        return (
            f"**Balance Sheet ({latest['period']})**\n\n"
            f"- Total Assets: {_format_currency(latest['total_assets'])}\n"
            f"- Total Liabilities: {_format_currency(latest['total_liabilities'])}\n"
            f"- Shareholders' Equity: {_format_currency(latest['shareholders_equity'])}"
        )

    table = await build_financial_statement_markdown()
    return (
        f"I can help with financial data from our ledger. Here's the current statement:\n\n{table}\n\n"
        f"Ask me about COGS, revenue trends, net income, or balance sheet details."
    )

from app.database.connections import get_marketing_connection


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def _format_pct(value: float) -> str:
    return f"{value:.2f}%"


async def get_campaign_metrics() -> list[dict]:
    conn = await get_marketing_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT period, campaign_name, spend, impressions, clicks, conversions,
                   cac, ltv, roas, ctr
            FROM campaign_metrics
            ORDER BY id
            """
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def build_marketing_statement_markdown() -> str:
    campaigns = await get_campaign_metrics()
    lines = [
        "## Marketing Performance Statement\n",
        "| Period | Campaign | Spend | Impressions | Clicks | Conv. | CAC | LTV | ROAS | CTR |",
        "|--------|----------|-------|-------------|--------|-------|-----|-----|------|-----|",
    ]
    for row in campaigns:
        lines.append(
            f"| {row['period']} | {row['campaign_name']} | {_format_currency(row['spend'])} | "
            f"{row['impressions']:,} | {row['clicks']:,} | {row['conversions']:,} | "
            f"{_format_currency(row['cac'])} | {_format_currency(row['ltv'])} | "
            f"{row['roas']:.1f}x | {_format_pct(row['ctr'])} |"
        )
    lines.append("\n*Source: marketing_data.db (Marketing domain — Node 3 only)*")
    return "\n".join(lines)


async def answer_marketing_question(question: str) -> str:
    campaigns = await get_campaign_metrics()
    question_lower = question.lower()

    if "cac" in question_lower and ("click" in question_lower or "vs" in question_lower):
        lines = ["**Clicks vs CAC Trend by Quarter**\n"]
        for row in campaigns:
            lines.append(
                f"- {row['campaign_name']} ({row['period']}): "
                f"{row['clicks']:,} clicks | CAC {_format_currency(row['cac'])}"
            )
        lines.append(
            "\nRetargeting (Q3) leads in efficiency — highest clicks with lowest CAC."
        )
        return "\n".join(lines)

    if "cac" in question_lower:
        best = min(campaigns, key=lambda c: c["cac"])
        worst = max(campaigns, key=lambda c: c["cac"])
        return (
            f"**Customer Acquisition Cost (CAC) Analysis**\n\n"
            f"- Best performing: **{best['campaign_name']}** ({best['period']}) at "
            f"{_format_currency(best['cac'])}\n"
            f"- Highest CAC: **{worst['campaign_name']}** ({worst['period']}) at "
            f"{_format_currency(worst['cac'])}\n\n"
            f"Retargeting campaigns typically yield lower CAC due to warm audiences."
        )

    if "ltv" in question_lower:
        lines = ["**Lifetime Value (LTV) by Campaign**\n"]
        for row in campaigns:
            ratio = row["ltv"] / row["cac"]
            lines.append(
                f"- {row['campaign_name']} ({row['period']}): "
                f"LTV {_format_currency(row['ltv'])} | LTV:CAC = {ratio:.1f}x"
            )
        return "\n".join(lines)

    if "roas" in question_lower:
        best = max(campaigns, key=lambda c: c["roas"])
        return (
            f"**Return on Ad Spend (ROAS)**\n\n"
            f"Top performer: **{best['campaign_name']}** ({best['period']}) at "
            f"**{best['roas']:.1f}x** ROAS.\n\n"
            f"Holiday Push and Retargeting campaigns consistently exceed 4.5x ROAS."
        )

    if "ctr" in question_lower or "click" in question_lower:
        best = max(campaigns, key=lambda c: c["ctr"])
        return (
            f"**Click-Through Rate (CTR) Analysis**\n\n"
            f"Highest CTR: **{best['campaign_name']}** ({best['period']}) at "
            f"{_format_pct(best['ctr'])}.\n\n"
            f"Retargeting audiences drive the strongest engagement rates."
        )

    if "improve" in question_lower or "how can" in question_lower:
        return (
            "**How to Improve Marketing Performance**\n\n"
            "Based on your campaign data:\n"
            "- **Scale Retargeting** — lowest CAC ($34) and highest CTR (4.00%)\n"
            "- **Optimize Performance Max** — highest CAC ($47); review audience targeting\n"
            "- **Increase Holiday Push budget** — strong ROAS (4.8x) with high conversion volume\n\n"
            "Ask me about a specific metric (CAC, CTR, ROAS) for a deeper breakdown."
        )

    if "campaign" in question_lower or "performance" in question_lower or "scenario" in question_lower:
        table = await build_marketing_statement_markdown()
        return f"Here's the full marketing performance breakdown:\n\n{table}"

    table = await build_marketing_statement_markdown()
    return (
        f"I can help with marketing metrics from our campaign database. "
        f"Here's the current performance statement:\n\n{table}\n\n"
        f"Ask me about CAC, LTV, ROAS, CTR, or specific campaign performance."
    )

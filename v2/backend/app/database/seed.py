import aiosqlite


async def seed_finance_data(conn: aiosqlite.Connection) -> None:
    cursor = await conn.execute("SELECT COUNT(*) FROM financial_statements")
    row = await cursor.fetchone()
    if row and row[0] > 0:
        return

    statements = [
        ("Q1 2025", 2_450_000, 980_000, 1_470_000, 620_000, 850_000),
        ("Q2 2025", 2_680_000, 1_180_000, 1_500_000, 640_000, 860_000),
        ("Q3 2025", 2_910_000, 1_020_000, 1_890_000, 680_000, 1_210_000),
        ("Q4 2025", 3_150_000, 1_100_000, 2_050_000, 710_000, 1_340_000),
    ]
    await conn.executemany(
        """
        INSERT INTO financial_statements
        (period, revenue, cogs, gross_profit, operating_expenses, net_income)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        statements,
    )

    balance_sheet = [
        ("Q1 2025", 8_200_000, 3_100_000, 5_100_000),
        ("Q2 2025", 8_450_000, 3_250_000, 5_200_000),
        ("Q3 2025", 8_900_000, 3_300_000, 5_600_000),
        ("Q4 2025", 9_300_000, 3_400_000, 5_900_000),
    ]
    await conn.executemany(
        """
        INSERT INTO balance_sheet (period, total_assets, total_liabilities, shareholders_equity)
        VALUES (?, ?, ?, ?)
        """,
        balance_sheet,
    )
    await conn.commit()


async def seed_marketing_data(conn: aiosqlite.Connection) -> None:
    cursor = await conn.execute("SELECT COUNT(*) FROM campaign_metrics")
    row = await cursor.fetchone()
    if row and row[0] > 0:
        return

    campaigns = [
        ("Q1 2025", "Brand Awareness", 120_000, 4_500_000, 135_000, 2_700, 44.44, 320.0, 3.2, 3.0),
        ("Q2 2025", "Performance Max", 185_000, 6_200_000, 198_000, 3_960, 46.72, 380.0, 4.1, 3.19),
        ("Q3 2025", "Retargeting", 95_000, 2_800_000, 112_000, 2_800, 33.93, 410.0, 5.6, 4.0),
        ("Q4 2025", "Holiday Push", 210_000, 7_500_000, 285_000, 5_700, 36.84, 450.0, 4.8, 3.8),
    ]
    await conn.executemany(
        """
        INSERT INTO campaign_metrics
        (period, campaign_name, spend, impressions, clicks, conversions, cac, ltv, roas, ctr)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        campaigns,
    )
    await conn.commit()

from app.database.connections import (
    get_app_storage_connection,
    get_finance_connection,
    get_marketing_connection,
)
from app.database.seed import seed_finance_data, seed_marketing_data


async def initialize_databases() -> None:
    await _init_app_storage()
    await _init_finance_db()
    await _init_marketing_db()


async def _init_app_storage() -> None:
    conn = await get_app_storage_connection()
    try:
        await conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                thread_id TEXT PRIMARY KEY,
                active_domain TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (thread_id) REFERENCES sessions(thread_id)
            );

            CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
            """
        )
        await conn.commit()
    finally:
        await conn.close()


async def _init_finance_db() -> None:
    conn = await get_finance_connection()
    try:
        await conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS financial_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL,
                revenue REAL NOT NULL,
                cogs REAL NOT NULL,
                gross_profit REAL NOT NULL,
                operating_expenses REAL NOT NULL,
                net_income REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS balance_sheet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL,
                total_assets REAL NOT NULL,
                total_liabilities REAL NOT NULL,
                shareholders_equity REAL NOT NULL
            );
            """
        )
        await conn.commit()
        await seed_finance_data(conn)
    finally:
        await conn.close()


async def _init_marketing_db() -> None:
    conn = await get_marketing_connection()
    try:
        await conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS campaign_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL,
                campaign_name TEXT NOT NULL,
                spend REAL NOT NULL,
                impressions INTEGER NOT NULL,
                clicks INTEGER NOT NULL,
                conversions INTEGER NOT NULL,
                cac REAL NOT NULL,
                ltv REAL NOT NULL,
                roas REAL NOT NULL,
                ctr REAL NOT NULL
            );
            """
        )
        await conn.commit()
        await seed_marketing_data(conn)
    finally:
        await conn.close()

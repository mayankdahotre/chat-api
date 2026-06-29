import aiosqlite

from app.config import get_settings


async def get_app_storage_connection() -> aiosqlite.Connection:
    settings = get_settings()
    settings.app_storage_db.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(settings.app_storage_db)
    conn.row_factory = aiosqlite.Row
    return conn


async def get_finance_connection() -> aiosqlite.Connection:
    settings = get_settings()
    settings.finance_db.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(settings.finance_db)
    conn.row_factory = aiosqlite.Row
    return conn


async def get_marketing_connection() -> aiosqlite.Connection:
    settings = get_settings()
    settings.marketing_db.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(settings.marketing_db)
    conn.row_factory = aiosqlite.Row
    return conn

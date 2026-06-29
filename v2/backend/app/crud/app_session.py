from app.database.connections import get_app_storage_connection


async def reset_session(session_id: str) -> None:
    conn = await get_app_storage_connection()
    try:
        await conn.execute("DELETE FROM messages WHERE thread_id = ?", (session_id,))
        await conn.execute(
            """
            INSERT INTO sessions (thread_id, active_domain, is_active)
            VALUES (?, NULL, 1)
            ON CONFLICT(thread_id) DO UPDATE SET
                active_domain = NULL,
                is_active = 1,
                updated_at = datetime('now')
            """,
            (session_id,),
        )
        await conn.commit()
    finally:
        await conn.close()


async def ensure_session(thread_id: str) -> None:
    conn = await get_app_storage_connection()
    try:
        await conn.execute(
            """
            INSERT OR IGNORE INTO sessions (thread_id, active_domain, is_active)
            VALUES (?, NULL, 1)
            """,
            (thread_id,),
        )
        await conn.commit()
    finally:
        await conn.close()


async def update_session_domain(thread_id: str, domain: str | None) -> None:
    conn = await get_app_storage_connection()
    try:
        await conn.execute(
            """
            UPDATE sessions
            SET active_domain = ?, updated_at = datetime('now')
            WHERE thread_id = ?
            """,
            (domain, thread_id),
        )
        await conn.commit()
    finally:
        await conn.close()


async def deactivate_session(thread_id: str) -> None:
    conn = await get_app_storage_connection()
    try:
        await conn.execute(
            """
            UPDATE sessions
            SET is_active = 0, active_domain = NULL, updated_at = datetime('now')
            WHERE thread_id = ?
            """,
            (thread_id,),
        )
        await conn.commit()
    finally:
        await conn.close()


async def get_session(thread_id: str) -> dict | None:
    conn = await get_app_storage_connection()
    try:
        cursor = await conn.execute(
            "SELECT thread_id, active_domain, is_active, created_at, updated_at FROM sessions WHERE thread_id = ?",
            (thread_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()


async def save_message(thread_id: str, role: str, content: str) -> None:
    conn = await get_app_storage_connection()
    try:
        await conn.execute(
            "INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
            (thread_id, role, content),
        )
        await conn.execute(
            "UPDATE sessions SET updated_at = datetime('now') WHERE thread_id = ?",
            (thread_id,),
        )
        await conn.commit()
    finally:
        await conn.close()


async def get_messages(thread_id: str, limit: int = 20) -> list[dict]:
    conn = await get_app_storage_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE thread_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (thread_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in reversed(rows)]
    finally:
        await conn.close()

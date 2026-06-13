"""Async SQLite для хранения прогресса онбординга и UTM-сессий."""

import aiosqlite
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "onboarding.db"


async def init_db():
    """Инициализация таблиц SQLite."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица прогресса онбординга
        await db.execute("""
            CREATE TABLE IF NOT EXISTS onboarding_progress (
                user_id       INTEGER PRIMARY KEY,
                current_step  INTEGER DEFAULT 0,
                last_activity TIMESTAMP,
                notified_48h  BOOLEAN DEFAULT FALSE,
                notified_96h  BOOLEAN DEFAULT FALSE,
                interrupted_state TEXT DEFAULT NULL
            )
        """)

        # Таблица UTM-сессий
        await db.execute("""
            CREATE TABLE IF NOT EXISTS utm_session (
                user_id      INTEGER PRIMARY KEY,
                nick         TEXT,
                promo_code   TEXT,
                last_updated TIMESTAMP
            )
        """)

        await db.commit()
    logger.info("SQLite базы данных инициализирована: %s", DB_PATH)


# ── Онбординг ───────────────────────────────────────────────────────────

async def get_onboarding_step(user_id: int) -> int:
    """Вернуть текущий шаг онбординга (0 = не начал)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT current_step FROM onboarding_progress WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def set_onboarding_step(user_id: int, step: int):
    """Установить шаг онбординга и обновить last_activity."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO onboarding_progress (user_id, current_step, last_activity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                current_step = ?,
                last_activity = ?
        """, (user_id, step, datetime.now(), step, datetime.now()))
        await db.commit()


async def update_onboarding_field(user_id: int, field: str, value):
    """Обновить произвольное поле в onboarding_progress."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"""
            UPDATE onboarding_progress SET {field} = ?
            WHERE user_id = ?
        """, (value, user_id))
        await db.commit()


async def get_onboarding_user(user_id: int) -> dict | None:
    """Получить всю запись прогресса пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM onboarding_progress WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def get_all_onboarding_users() -> list[dict]:
    """Получить всех пользователей с активным онбордингом (step > 0 и < 8)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM onboarding_progress
            WHERE current_step > 0 AND current_step < 8
            ORDER BY last_activity
        """) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def save_interrupted_state(user_id: int, state_data: str):
    """Сохранить прерванное состояние онбординга (для UTM-генератора)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE onboarding_progress SET interrupted_state = ?
            WHERE user_id = ?
        """, (state_data, user_id))
        await db.commit()


async def get_interrupted_state(user_id: int) -> str | None:
    """Получить прерванное состояние онбординга."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT interrupted_state FROM onboarding_progress WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def clear_interrupted_state(user_id: int):
    """Очистить прерванное состояние."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE onboarding_progress SET interrupted_state = NULL
            WHERE user_id = ?
        """, (user_id,))
        await db.commit()


# ── UTM-сессии ──────────────────────────────────────────────────────────

async def get_utm_session(user_id: int) -> dict | None:
    """Получить UTM-сессию пользователя (ник + промокод)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM utm_session WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def save_utm_session(user_id: int, nick: str, promo_code: str):
    """Сохранить UTM-сессию (ник + промокод)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO utm_session (user_id, nick, promo_code, last_updated)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                nick = ?,
                promo_code = ?,
                last_updated = ?
        """, (user_id, nick, promo_code, datetime.now(), nick, promo_code, datetime.now()))
        await db.commit()


async def delete_utm_session(user_id: int):
    """Удалить UTM-сессию пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM utm_session WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

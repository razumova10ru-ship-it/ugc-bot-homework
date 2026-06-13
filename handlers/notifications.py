"""Уведомления о застрявших участниках онбординга.

APScheduler задача раз в час сканирует участников с незавершённым онбордингом.
Пороги:
- 48ч → напоминание участнику
- 96ч → эскалация куратору @alena_tam
"""

import logging
from datetime import datetime, timedelta

from aiogram import Router, Bot

from db.onboarding_db import get_all_onboarding_users, update_onboarding_field

router = Router()

logger = logging.getLogger(__name__)

# Пороги уведомлений
THRESHOLD_48H = timedelta(hours=48)
THRESHOLD_96H = timedelta(hours=96)

# Тексты напоминаний
REMINDER_48H_TEXT = (
    "⏰ <b>Напоминание: онбординг не завершён</b>\n\n"
    "Привет! Вижу, ты ещё не закончил онбординг. "
    "Это важно для твоего успеха в программе — каждый шаг приближает тебя к заработку.\n\n"
    "Нажми /start чтобы продолжить с того места, где остановился.\n\n"
    "Если есть вопросы или сложности — напиши куратору Алёне: @alena_tam"
)

REMINDER_96H_TEXT = (
    "⚠️ <b>Срочно: онбординг не пройден</b>\n\n"
    "Привет! Ты не проходишь онбординг уже более 4 дней. "
    "Это критично — без завершения ты не получишь доступ к обучению и не сможешь зарабатывать.\n\n"
    "Нажми /start прямо сейчас и заверши оставшиеся шаги.\n\n"
    "Если нужна помощь — пиши куратору: @alena_tam"
)


async def check_stalled_users(bot: Bot):
    """Проверка застрявших участников онбординга.

    Запускается APScheduler раз в час.
    """
    try:
        users = await get_all_onboarding_users()
        now = datetime.now()

        logger.info("Проверка застрявших участников: найдено %d активных онбордингов", len(users))

        for user in users:
            user_id = user["user_id"]
            current_step = user["current_step"]
            last_activity = user["last_activity"]
            notified_48h = user["notified_48h"]
            notified_96h = user["notified_96h"]

            # Парсим last_activity
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00").replace("+00:00", ""))

            time_since = now - last_activity

            # Проверка 96ч (эскалация куратору)
            if time_since >= THRESHOLD_96H and not notified_96h:
                await escalate_to_curator(bot, user_id, current_step, last_activity)
                await update_onboarding_field(user_id, "notified_96h", True)
                logger.info("Эскалация куратору: user_id=%s, шаг=%d", user_id, current_step)

            # Проверка 48ч (напоминание участнику)
            elif time_since >= THRESHOLD_48H and not notified_48h:
                await remind_user(bot, user_id, current_step)
                await update_onboarding_field(user_id, "notified_48h", True)
                logger.info("Напоминание участнику: user_id=%s, шаг=%d", user_id, current_step)

    except Exception as e:
        logger.exception("Ошибка при проверке застрявших участников: %s", e)


async def remind_user(bot: Bot, user_id: int, current_step: int):
    """Отправить напоминание участнику."""
    try:
        await bot.send_message(
            user_id,
            REMINDER_48H_TEXT if current_step < 6 else REMINDER_96H_TEXT,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("Не удалось отправить напоминание пользователю %s: %s", user_id, e)


async def escalate_to_curator(bot: Bot, user_id: int, current_step: int, last_activity: datetime):
    """Отправить уведомление куратору о застрявшем участнике."""
    import os

    curator_chat_id = os.getenv("CURATOR_CHAT_ID")
    if not curator_chat_id:
        logger.warning("CURATOR_CHAT_ID не задан, пропускаем эскалацию")
        return

    step_names = {
        1: "Доступ к обучению",
        2: "Аккаунты",
        3: "Дашборд",
        4: "Реферальная ссылка",
        5: "Настройка аккаунта",
        6: "Первый Reels",
    }

    try:
        # Получаем ник пользователя
        try:
            chat = await bot.get_chat(user_id)
            nick = f"@{chat.username}" if chat.username else chat.full_name
        except Exception:
            nick = f"user_id={user_id}"

        await bot.send_message(
            curator_chat_id,
            f"🚨 <b>Застрявший участник онбординга</b>\n\n"
            f"👤 Участник: {nick}\n"
            f"📍 Шаг: {current_step} ({step_names.get(current_step, 'Неизвестно')})\n"
            f"⏰ Последняя активность: {last_activity.strftime('%d.%m.%Y %H:%M')}\n"
            f"🕐 Не активен: {(datetime.now() - last_activity).total_seconds() / 3600:.1f} часов\n\n"
            f"Требуется помощь куратора!",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("Не удалось отправить эскалацию куратору: %s", e)


def setup_scheduler(bot):
    """Настройка APScheduler планировщика."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    scheduler = AsyncIOScheduler()

    # Задача раз в час
    scheduler.add_job(
        check_stalled_users,
        trigger=IntervalTrigger(hours=1),
        id="check_stalled_onboarding",
        name="Проверка застрявших участников онбординга",
        kwargs={"bot": bot},
    )

    scheduler.start()
    logger.info("APScheduler запущен: проверка застрявших участников раз в час")

    return scheduler

import logging
import sys
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import start, manager, form, education, navigation, fallback, menu, onboarding, utm, notifications
from db.onboarding_db import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не задан. Установите переменную окружения или .env файл.")
        sys.exit(1)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Глобальный фильтр: бот отвечает только в личных чатах
    dp.message.filter(F.chat.type == "private")
    dp.callback_query.filter(F.message.chat.type == "private")

    # Порядок важен: навигация и менеджер — перед формой,
    # чтобы callback'и без привязки к состоянию перехватывались правильно
    dp.include_router(start.router)
    dp.include_router(navigation.router)
    dp.include_router(manager.router)
    dp.include_router(menu.router)  # постоянное меню
    dp.include_router(onboarding.router)  # онбординг-трек
    dp.include_router(utm.router)  # UTM-генератор
    dp.include_router(notifications.router)  # уведомления
    dp.include_router(form.router)
    dp.include_router(education.router)
    dp.include_router(fallback.router)  # заглушка — последним

    # Инициализация SQLite
    await init_db()

    # Настройка APScheduler (проверка застрявших участников раз в час)
    from handlers.notifications import setup_scheduler
    scheduler = setup_scheduler(bot)

    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
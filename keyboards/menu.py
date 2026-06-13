"""Постоянное меню (Reply Keyboard) с 6 кнопками.

Доступно на всех этапах воронки, не перекрывается inline-кнопками.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_kb() -> ReplyKeyboardMarkup:
    """Основное меню с 6 кнопками.

    Кнопки:
    1. 🔖 Создать реферальную ссылку
    2. 📊 Мой прогресс
    3. 📚 Обучение
    4. ❓ Вопрос-ответ
    5. 👥 Группа
    6. 👤 Менеджер
    """
    keyboard = [
        [
            KeyboardButton(text="🔖 Создать реферальную ссылку"),
            KeyboardButton(text="📊 Мой прогресс"),
        ],
        [
            KeyboardButton(text="📚 Обучение"),
            KeyboardButton(text="❓ Вопрос-ответ"),
        ],
        [
            KeyboardButton(text="👥 Группа"),
            KeyboardButton(text="👤 Менеджер"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )

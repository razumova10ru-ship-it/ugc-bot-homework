"""Клавиатуры для UTM-генератора."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def link_type_kb() -> InlineKeyboardMarkup:
    """Шаг 1: выбор типа ссылки."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Контент (Reels, Shorts, Story...)",
                    callback_data="utm_type_content",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📍 Шапка профиля (Bio)",
                    callback_data="utm_type_bio",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Автоматизация (рассылки, воронки)",
                    callback_data="utm_type_automation",
                )
            ],
        ]
    )


def platform_kb() -> InlineKeyboardMarkup:
    """Шаг 2: выбор платформы."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📸 Instagram",
                    callback_data="utm_platform_instagram",
                ),
                InlineKeyboardButton(
                    text="🎵 TikTok",
                    callback_data="utm_platform_tiktok",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📺 YouTube",
                    callback_data="utm_platform_youtube",
                ),
                InlineKeyboardButton(
                    text="✈️ Telegram",
                    callback_data="utm_platform_telegram",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💬 VK",
                    callback_data="utm_platform_vk",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✍️ Другое",
                    callback_data="utm_platform_other",
                ),
            ],
        ]
    )


def content_format_kb() -> InlineKeyboardMarkup:
    """Шаг 4: выбор формата контента."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Reels",
                    callback_data="utm_format_reels",
                ),
                InlineKeyboardButton(
                    text="▶️ Shorts",
                    callback_data="utm_format_shorts",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📸 Story",
                    callback_data="utm_format_story",
                ),
                InlineKeyboardButton(
                    text="📝 Пост",
                    callback_data="utm_format_post",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎥 Видео",
                    callback_data="utm_format_video",
                ),
            ],
        ]
    )


def products_kb() -> InlineKeyboardMarkup:
    """Шаг 6: выбор продукта с собственным вебинаром."""
    from config.products import PRODUCTS

    keyboard = []
    for product in PRODUCTS:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=product["name"],
                    callback_data=f"utm_product_{product['callback_id']}",
                )
            ]
        )

    # Кнопка "Другое" для программ без вебинара
    keyboard.append(
        [
            InlineKeyboardButton(
                text="📦 Другое (ведёт на Vibe Coding)",
                callback_data="utm_product_other",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def use_saved_data_kb(nick: str, promo_code: str) -> InlineKeyboardMarkup:
    """Предложение использовать сохранённые данные."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, использовать",
                    callback_data="utm_use_saved_yes",
                ),
                InlineKeyboardButton(
                    text="🔄 Ввести заново",
                    callback_data="utm_use_saved_no",
                ),
            ],
        ]
    )


def finish_utm_kb() -> InlineKeyboardMarkup:
    """Завершение UTM-генератора."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔖 Создать ещё одну ссылку",
                    callback_data="utm_start",
                ),
            ],
        ]
    )

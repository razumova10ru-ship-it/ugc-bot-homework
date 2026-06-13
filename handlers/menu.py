"""Обработчики кнопок постоянного меню."""

import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from config import (
    GROUP_TOPIC_QA_LINK,
    GROUP_INVITE_LINK,
    MANAGER_LINK,
    EDUCATION_FORM_LINK,
    DASHBOARD_FORM_LINK,
)
from states.utm import UTMStates

router = Router()
router.message.filter(F.chat.type == "private")
logger = logging.getLogger(__name__)


@router.message(F.text == "🔖 Создать реферальную ссылку")
async def menu_create_referral(message: types.Message, state: FSMContext):
    """Запуск UTM-генератора."""
    from db.onboarding_db import get_utm_session
    from keyboards.utm import link_type_kb, use_saved_data_kb

    user_id = message.from_user.id

    # Проверяем, есть ли сохранённая сессия
    session = await get_utm_session(user_id)

    if session and session.get("nick") and session.get("promo_code"):
        # Предлагаем использовать сохранённые данные
        await message.answer(
            f"🔖 <b>Генератор реферальных ссылок</b>\n\n"
            f"У тебя есть сохранённые данные:\n"
            f"👤 Ник: <code>{session['nick']}</code>\n"
            f"🔑 Промокод: <code>{session['promo_code']}</code>\n\n"
            f"Использовать их?",
            parse_mode="HTML",
            reply_markup=use_saved_data_kb(session["nick"], session["promo_code"]),
        )
    else:
        # Начинаем с выбора типа ссылки
        await state.set_state(UTMStates.choosing_link_type)
        await message.answer(
            "🔖 <b>Генератор реферальных ссылок</b>\n\n"
            "Выбери тип ссылки:",
            reply_markup=link_type_kb(),
            parse_mode="HTML",
        )


@router.message(F.text == "📊 Мой прогресс")
async def menu_my_progress(message: types.Message):
    """Показать текущий прогресс онбординга."""
    from db.onboarding_db import get_onboarding_step

    user_id = message.from_user.id
    step = await get_onboarding_step(user_id)

    step_names = {
        0: "Не начал",
        1: "Доступ к обучению",
        2: "Аккаунты",
        3: "Дашборд",
        4: "Реферальная ссылка",
        5: "Настройка аккаунта",
        6: "Первый Reels",
        7: "Завершено ✅",
    }

    step_name = step_names.get(step, "Неизвестно")

    await message.answer(
        f"📊 <b>Твой прогресс</b>\n\n"
        f"Шаг {step}: {step_name}\n\n"
        f"Продолжай проходить онбординг — каждый шаг приближает тебя к заработку! 💪",
        parse_mode="HTML",
    )


@router.message(F.text == "📚 Обучение")
async def menu_education(message: types.Message):
    """Ссылка на форму выбора обучения."""
    await message.answer(
        "📚 <b>Выбрать обучение</b>\n\n"
        f"Ознакомься с реестром программ и выбери подходящее обучение:\n\n"
        f"{EDUCATION_FORM_LINK}\n\n"
        f"После заполнения формы вернись в бота для продолжения онбординга.",
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@router.message(F.text == "❓ Вопрос-ответ")
async def menu_faq(message: types.Message):
    """Ссылка на топик Вопрос-ответ."""
    await message.answer(
        "❓ <b>Вопрос-ответ</b>\n\n"
        f"Загляни в наш топик с ответами на частые вопросы:\n\n"
        f"{GROUP_TOPIC_QA_LINK}\n\n"
        f"Если не нашёл ответ — напиши куратору Алёне.",
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@router.message(F.text == "👥 Группа")
async def menu_group(message: types.Message):
    """Ссылка на группу."""
    await message.answer(
        "👥 <b>Рабочая группа</b>\n\n"
        f"Вступай в нашу рабочую группу:\n\n"
        f"{GROUP_INVITE_LINK}\n\n"
        f"Там все креаторы, кураторы и важные анонсы!",
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@router.message(F.text == "👤 Менеджер")
async def menu_manager(message: types.Message):
    """Ссылка на менеджера."""
    from keyboards.inline import nav_row

    manager_text = "Алёна, привет! У меня есть вопросы при общении с ботом-куратором"

    await message.answer(
        f"👤 <b>Связь с менеджером</b>\n\n"
        f"Напиши Алёне — она поможет с любыми вопросами:\n\n"
        f"<a href=\"{MANAGER_LINK}\">Перейти в чат с менеджером</a>\n\n"
        f"Или скопируй и отправь это сообщение:\n\n"
        f"<code>{manager_text}</code>",
        reply_markup=_menu_nav_kb(),
        parse_mode="HTML",
    )


# ── Клавиатуры ──────────────────────────────────────────────────────────

def _link_type_kb():
    """Клавиатура для выбора типа UTM-ссылки."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Ссылка на контент (Reels/Story)",
                    callback_data="utm_type_content",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👤 Ссылка для шапки профиля",
                    callback_data="utm_type_bio",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Ссылка для автоматизации (ManyChat)",
                    callback_data="utm_type_automation",
                ),
            ],
        ]
    )


def _menu_nav_kb():
    """Навигационная кнопка для возврата в меню."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В начало", callback_data="nav_start")],
        ]
    )

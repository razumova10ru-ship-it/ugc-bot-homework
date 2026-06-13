"""Онбординг-трек: 7 шагов для новых участников.

Запускается автоматически при вступлении в Telegram-группу.
Каждый шаг разблокируется только после подтверждения предыдущего.
"""

import logging
import os
from datetime import datetime

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from db.onboarding_db import (
    get_onboarding_step,
    set_onboarding_step,
    get_interrupted_state,
    clear_interrupted_state,
)
from states.onboarding import OnboardingStates
from keyboards.menu import get_main_menu_kb
from config import (
    GROUP_TOPIC_ACCOUNTS_LINK,
    DASHBOARD_FORM_LINK,
    PARTNERS_LINK,
    GROUP_TOPIC_QA_LINK,
)

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(~F.data.startswith("utm_"))
logger = logging.getLogger(__name__)

# ── Тексты шагов ────────────────────────────────────────────────────────

STEP_1_TEXT = (
    "🎓 <b>Шаг 1: Доступ к обучению</b>\n\n"
    "На почту придёт письмо от GetCourse — в нём будет указана стоимость программы, "
    "но для тебя как UGC-креатора курс полностью <b>БЕСПЛАТНЫЙ</b>.\n\n"
    "Это автоматическое письмо системы, не пугайся суммы. "
    "В течение 48 часов придёт второе письмо — уже с доступом к курсу.\n\n"
    "⏰ Если доступ не пришёл в течение 48 часов — напиши куратору."
)

STEP_2_TEXT = (
    "👤 <b>Шаг 2: Аккаунты</b>\n\n"
    "Следующий шаг — определиться с аккаунтами для контента. "
    "Ты можешь вести контент со своих личных аккаунтов или создать новые специально для этого.\n\n"
    "Вся информация по созданию и настройке аккаунтов — в нашем топике:\n"
    f"{GROUP_TOPIC_ACCOUNTS_LINK}\n\n"
    "Если нужна помощь или есть вопросы — напиши куратору Алёне, она поможет разобраться.\n\n"
    "Как определишься — нажми «Готово»."
)

STEP_3_TEXT = (
    "📊 <b>Шаг 3: Внесение ссылок в Дашборд</b>\n\n"
    "Занеси ссылки на свои рабочие аккаунты в анкету Дашборда — "
    "кураторы смогут отслеживать твои публикации и давать обратную связь. "
    "Это важно для твоего роста в программе.\n\n"
    f"Заполни форму: {DASHBOARD_FORM_LINK}\n\n"
    "После заполнения нажми «Готово»."
)

STEP_4_TEXT = (
    "🔗 <b>Шаг 4: Реферальная ссылка</b>\n\n"
    "Реферальная ссылка — это твой главный инструмент заработка в программе. "
    "Ты зарабатываешь <b>15–24%</b> с каждой продажи, которая прошла через твою ссылку.\n\n"
    "Важно: одна ссылка — это только начало. Успешные креаторы размещают <b>10–15</b> реферальных ссылок "
    "в разных местах:\n"
    "• Шапка профиля Instagram / TikTok / YouTube\n"
    "• Ссылка-агрегатор (Taplink, Linktree и др.)\n"
    "• Автоматизация в ManyChat или ChatPlace\n"
    "• Хайлайтс с Story о продукте\n"
    "• Описание под каждым Reels\n\n"
    "Сначала зарегистрируйся как партнёр и создай первую ссылку через UTM-генератор.\n\n"
    f"🔖 Регистрация партнёра: {PARTNERS_LINK}"
)

STEP_5_TEXT = (
    "⚙️ <b>Шаг 5: Настройка аккаунта (шапка / хайлайтс)</b>\n\n"
    "Супер, ты создал реферальную ссылку! Теперь размести её в шапке профиля — "
    "это первое место, куда смотрит аудитория.\n\n"
    "Оформи хайлайтс: закреплённые сторис с информацией о продукте. "
    "Как это сделать — в уроке 38 раздела <b>Обучение блогингу</b>.\n\n"
    "Если возникнут вопросы — напиши куратору Алёне."
)

STEP_6_TEXT = (
    "🎬 <b>Шаг 6: Первый Reels</b>\n\n"
    "Сними и выложи первый Reels! "
    "Пришли ссылку на публикацию сюда — я передам её куратору Алёне для обратной связи.\n\n"
    "Отправь ссылку на свой первый Reels 👇"
)

STEP_7_TEXT = (
    "🎉 <b>Поздравляю! Ты прошёл все шаги онбординга!</b>\n\n"
    "Твоя ссылка передана куратору — жди обратной связи.\n\n"
    "Следи за обновлениями в группе в ветке <b>Вопрос-ответ</b>:\n"
    f"{GROUP_TOPIC_QA_LINK}\n\n"
    "Успехов в создании контента! 🚀"
)


# ── Клавиатуры ──────────────────────────────────────────────────────────

def step_1_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Получил доступ", callback_data="onboarding_step_1_done")]]
    )


def step_2_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Готово", callback_data="onboarding_step_2_done")]]
    )


def step_3_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Готово", callback_data="onboarding_step_3_done")]]
    )


def step_4_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔖 Создать реферальную ссылку", callback_data="utm_start_from_onboarding")],
            [InlineKeyboardButton(text="✅ Готово", callback_data="onboarding_step_4_done")],
        ]
    )


def step_5_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔖 Создать реферальную ссылку", callback_data="utm_start_from_onboarding")],
            [InlineKeyboardButton(text="✅ Готово", callback_data="onboarding_step_5_done")],
        ]
    )


def step_6_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📊 Мой прогресс", callback_data="nav_start")]]
    )


# ── Триггер: вступление в группу ────────────────────────────────────────

@router.my_chat_member()
async def on_chat_member_update(message: types.Message, bot: Bot):
    """Триггер: участник вступил в группу → запускаем онбординг в ЛС."""
    from aiogram.types import ChatMemberUpdated
    from aiogram.enums import ChatMemberStatus

    # Проверяем, что это обновление членства в группе (не в ЛС)
    if message.chat.type != "group" and message.chat.type != "supergroup":
        return

    old_member = message.old_chat_member
    new_member = message.new_chat_member

    # Проверяем переход из participant/left в member
    was_member = old_member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.RESTRICTED)
    is_member = new_member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)

    if was_member and is_member:
        user_id = new_member.user.id
        await start_onboarding(user_id, bot)


async def start_onboarding(user_id: int, bot: Bot):
    """Запуск онбординга для нового участника."""
    from db.onboarding_db import get_onboarding_step
    from services.sheets import save_user_data, update_onboarding_field

    # Проверяем, не начал ли уже онбординг
    current_step = await get_onboarding_step(user_id)
    if current_step > 0:
        logger.info("Пользователь %s уже начал онбординг (шаг %d)", user_id, current_step)
        return

    # Начинаем с шага 1
    await set_onboarding_step(user_id, 1)

    # Создаём запись в Google Sheets если нет
    user_data = {
        "user_id": user_id,
        "source": "онбординг (группа)",
        "full_name": "",
        "telegram_nick": "",
        "email": "",
        "phone": "",
        "content_experience": "",
        "editing_level": "",
        "platform_access": "",
        "education_form_filled": False,
        "joined_group": True,
        "photo_sent": False,
    }
    save_user_data(user_data)
    await update_onboarding_field(user_id, "onboarding_step", 1)

    try:
        # Получаем имя пользователя для логирования
        try:
            chat = await bot.get_chat(user_id)
            user_name = chat.full_name or chat.username or f"user_id={user_id}"
        except Exception:
            user_name = f"user_id={user_id}"

        await bot.send_message(
            user_id,
            "🎉 <b>Добро пожаловать в команду UGC-креаторов!</b>\n\n"
            "Я твой бот-куратор. Помогу пройти онбординг и начать зарабатывать.\n\n"
            "Всего 7 простых шагов — погнали! 🚀",
            parse_mode="HTML",
            reply_markup=get_main_menu_kb(),
        )
        await bot.send_message(
            user_id,
            STEP_1_TEXT,
            parse_mode="HTML",
            reply_markup=step_1_kb(),
        )
        logger.info("Запущен онбординг для пользователя %s", user_name)
    except Exception as e:
        logger.error("Не удалось отправить сообщение пользователю %s: %s", user_id, e)


# ── Обработчики шагов ───────────────────────────────────────────────────

@router.callback_query(F.data == "onboarding_step_1_done")
async def step_1_done(callback: types.CallbackQuery, state: FSMContext):
    """Шаг 1 подтверждён → переходим к шагу 2."""
    from services.sheets import update_onboarding_field

    user_id = callback.from_user.id
    await set_onboarding_step(user_id, 2)
    await update_onboarding_field(user_id, "onboarding_step", 2)
    await callback.answer()

    # Отправляем сообщение шага 2
    await callback.message.answer(
        STEP_2_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=step_2_kb(),
    )


@router.callback_query(F.data == "onboarding_step_2_done")
async def step_2_done(callback: types.CallbackQuery, state: FSMContext):
    """Шаг 2 подтверждён → переходим к шагу 3."""
    from services.sheets import update_onboarding_field

    user_id = callback.from_user.id
    await set_onboarding_step(user_id, 3)
    await update_onboarding_field(user_id, "onboarding_step", 3)
    await callback.answer()

    await callback.message.answer(
        STEP_3_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=step_3_kb(),
    )


@router.callback_query(F.data == "onboarding_step_3_done")
async def step_3_done(callback: types.CallbackQuery, state: FSMContext):
    """Шаг 3 подтверждён → переходим к шагу 4."""
    from services.sheets import update_onboarding_field

    user_id = callback.from_user.id
    await set_onboarding_step(user_id, 4)
    await update_onboarding_field(user_id, "onboarding_step", 4)
    await callback.answer()

    await callback.message.answer(
        STEP_4_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=step_4_kb(),
    )


@router.callback_query(F.data == "onboarding_step_4_done")
async def step_4_done(callback: types.CallbackQuery, state: FSMContext):
    """Шаг 4 подтверждён → переходим к шагу 5."""
    from services.sheets import update_onboarding_field

    user_id = callback.from_user.id
    await set_onboarding_step(user_id, 5)
    await update_onboarding_field(user_id, "onboarding_step", 5)
    await callback.answer()

    await callback.message.answer(
        STEP_5_TEXT,
        parse_mode="HTML",
        reply_markup=step_5_kb(),
    )


@router.callback_query(F.data == "onboarding_step_5_done")
async def step_5_done(callback: types.CallbackQuery, state: FSMContext):
    """Шаг 5 подтверждён → переходим к шагу 6."""
    from services.sheets import update_onboarding_field

    user_id = callback.from_user.id
    await set_onboarding_step(user_id, 6)
    await update_onboarding_field(user_id, "onboarding_step", 6)
    await callback.answer()

    await callback.message.answer(
        STEP_6_TEXT,
        parse_mode="HTML",
        reply_markup=step_6_kb(),
    )


@router.message(OnboardingStates.waiting_for_reels_link, F.text)
async def process_reels_link(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ссылки на Reels (шаг 6)."""
    from services.sheets import update_onboarding_field

    text = message.text.strip()

    # Простая валидация: должна содержать http или быть ссылкой
    if not text.startswith(("http://", "https://")):
        await message.answer(
            "⚠️ Пожалуйста, отправь именно <b>ссылку</b> на публикацию (начинается с https://).\n\n"
            "Это может быть ссылка на Reels в Instagram, TikTok или YouTube Shorts.",
            parse_mode="HTML",
        )
        return

    user_id = message.from_user.id
    await set_onboarding_step(user_id, 7)

    # Сохраняем ссылку и статус завершения в Sheets
    await update_onboarding_field(user_id, "reels_link", text)
    await update_onboarding_field(user_id, "onboarding_step", 7)
    await update_onboarding_field(user_id, "onboarding_completed", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Отправляем куратору
    CURATOR_CHAT_ID = int(os.getenv("CURATOR_CHAT_ID", 0))
    if CURATOR_CHAT_ID:
        try:
            await bot.send_message(
                CURATOR_CHAT_ID,
                f"🎬 Новый Reels от участника!\n\n"
                f"User ID: {user_id}\n"
                f"Ник: @{message.from_user.username or 'не указан'}\n"
                f"Ссылка: {text}",
            )
        except Exception as e:
            logger.error("Не удалось отправить ссылку куратору: %s", e)

    await message.answer(
        STEP_7_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_main_menu_kb(),
    )


# ── Команда /start с продолжением онбординга ────────────────────────────

@router.message(Command("start"))
async def cmd_start_with_resume(message: types.Message, state: FSMContext):
    """Обработка /start: если проходил онбординг — предложить продолжить."""
    from db.onboarding_db import get_onboarding_step

    user_id = message.from_user.id
    current_step = await get_onboarding_step(user_id)

    if current_step > 0 and current_step < 7:
        # Предложить продолжить
        step_names = {
            1: "Доступ к обучению",
            2: "Аккаунты",
            3: "Дашборд",
            4: "Реферальная ссылка",
            5: "Настройка аккаунта",
            6: "Первый Reels",
        }
        step_name = step_names.get(current_step, "Неизвестно")

        await message.answer(
            f"👋 С возвращением!\n\n"
            f"Ты останавливался на шаге <b>{current_step}: {step_name}</b>.\n\n"
            "Хочешь продолжить онбординг?",
            parse_mode="HTML",
            reply_markup=_resume_kb(current_step),
        )
        return

    # Если не начал или завершил — обычное приветствие
    # (обработается в handlers/start.py)


def _resume_kb(step: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Продолжить", callback_data=f"onboarding_resume_{step}")],
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="onboarding_restart")],
        ]
    )


@router.callback_query(F.data.startswith("onboarding_resume_"))
async def resume_onboarding(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Возобновление онбординга с указанного шага."""
    step = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    # Проверяем прерванное состояние (если было прерывание UTM)
    interrupted = await get_interrupted_state(user_id)
    if interrupted:
        # Восстанавливаем состояние
        from aiogram.fsm.storage.memory import MemoryStorage
        await state.set_data(eval(interrupted))
        await clear_interrupted_state(user_id)
        await callback.answer("Возвращаемся к онбордингу...")
        return

    # Отправляем сообщение текущего шага
    step_texts = {
        1: (STEP_1_TEXT, step_1_kb()),
        2: (STEP_2_TEXT, step_2_kb()),
        3: (STEP_3_TEXT, step_3_kb()),
        4: (STEP_4_TEXT, step_4_kb()),
        5: (STEP_5_TEXT, step_5_kb()),
        6: (STEP_6_TEXT, step_6_kb()),
    }

    text, kb = step_texts.get(step, (STEP_1_TEXT, step_1_kb()))
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "onboarding_restart")
async def restart_onboarding(callback: types.CallbackQuery, state: FSMContext):
    """Перезапуск онбординга с начала."""
    user_id = callback.from_user.id
    await set_onboarding_step(user_id, 1)
    await callback.message.answer(
        "🔄 Начинаем онбординг заново!\n\n" + STEP_1_TEXT,
        parse_mode="HTML",
        reply_markup=step_1_kb(),
    )
    await callback.answer()

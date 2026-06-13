from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import MANAGER_LINK, GROUP_INVITE_LINK, EDUCATION_FORM_LINK


# ── Навигация ──────────────────────────────────────────────────────────

def nav_row(exclude: set[str] | None = None) -> list[list[InlineKeyboardButton]]:
    """Вспомогательная функция — ряд навигационных кнопок."""
    exclude = exclude or set()
    buttons: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    if "group" not in exclude:
        row.append(InlineKeyboardButton(text="Вступить в группу", callback_data="nav_join_group"))
    if "manager" not in exclude:
        row.append(InlineKeyboardButton(text="Написать менеджеру", callback_data="manager"))
    if row:
        buttons.append(row)
    if "start" not in exclude:
        buttons.append([InlineKeyboardButton(text="🏠 В начало", callback_data="nav_start")])
    return buttons


# ── Основные экраны ────────────────────────────────────────────────────

def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Узнать подробнее", callback_data="offer")],
            [InlineKeyboardButton(text="Я уже хочу участвовать", callback_data="join")],
            [InlineKeyboardButton(text="Задать вопрос менеджеру", callback_data="manager")],
        ]
    )


def offer_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Я уже хочу участвовать", callback_data="join")],
            [InlineKeyboardButton(text="Задать вопрос менеджеру", callback_data="manager")],
            [InlineKeyboardButton(text="🏠 В начало", callback_data="nav_start")],
        ]
    )


# ── Анкета ─────────────────────────────────────────────────────────────

def source_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Threads", callback_data="source_threads")],
            [InlineKeyboardButton(text="Telegram", callback_data="source_telegram")],
            [InlineKeyboardButton(text="От друга", callback_data="source_friend")],
            [InlineKeyboardButton(text="Другое", callback_data="source_other")],
        ]
    )


def content_experience_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Снимаю и создаю регулярно — это часть моей жизни",
                    callback_data="exp_regular",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Иногда создаю контент. Хочется больше",
                    callback_data="exp_sometimes",
                )
            ],
            [InlineKeyboardButton(text="Небольшой опыт", callback_data="exp_little")],
        ]
    )


def editing_level_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Базовый — могу склеить и обрезать",
                    callback_data="edit_basic",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Уверенный — эффекты, переходы, субтитры",
                    callback_data="edit_confident",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Продвинутый — переходы, цветокоррекция, motion",
                    callback_data="edit_advanced",
                )
            ],
        ]
    )


def platform_access_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, всё работает стабильно",
                    callback_data="platform_yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Частично, к некоторым платформам есть не всегда",
                    callback_data="platform_partial",
                )
            ],
        ]
    )


def pd_consent_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Даю согласие на обработку моих персональных данных",
                    callback_data="pd_consent_yes",
                )
            ],
        ]
    )


def privacy_policy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="С Политикой конфиденциальности ознакомлен(а) и согласен(а)",
                    callback_data="privacy_yes",
                )
            ],
        ]
    )


def offer_accept_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Принимаю условия оферты",
                    callback_data="offer_accept_yes",
                )
            ],
        ]
    )


# ── После анкеты ───────────────────────────────────────────────────────

def after_form_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вступить в группу", callback_data="nav_join_group")],
            [InlineKeyboardButton(text="Задать вопрос менеджеру", callback_data="manager")],
        ]
    )


# ── Группа ──────────────────────────────────────────────────────────────

def group_join_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вступить в группу", url=GROUP_INVITE_LINK)],
            [InlineKeyboardButton(text="Я вступил в группу", callback_data="check_group")],
            [InlineKeyboardButton(text="Написать менеджеру", callback_data="manager")],
            [InlineKeyboardButton(text="🏠 В начало", callback_data="nav_start")],
        ]
    )


# ── Обучение ────────────────────────────────────────────────────────────

def education_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="Выбрать обучение", url=EDUCATION_FORM_LINK)],
        [InlineKeyboardButton(text="✅ Я заполнил(а) форму", callback_data="education_form_done")],
    ]
    rows.extend(nav_row(exclude={"group"}))
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Запрос фото ─────────────────────────────────────────────────────────

def photo_request_kb() -> InlineKeyboardMarkup:
    rows = []
    rows.extend(nav_row(exclude={"group"}))
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── После фото (финал) ──────────────────────────────────────────────────

def photo_done_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="Написать менеджеру", url=MANAGER_LINK)],
    ]
    rows.extend(nav_row(exclude={"manager"}))
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Менеджер ────────────────────────────────────────────────────────────

def manager_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="Написать менеджеру", url=MANAGER_LINK)],
    ]
    rows.extend(nav_row(exclude={"manager"}))
    return InlineKeyboardMarkup(inline_keyboard=rows)
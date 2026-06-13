from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton

from keyboards.inline import nav_row
from config import MANAGER_LINK

router = Router()
router.callback_query.filter(F.message.chat.type == "private")

MANAGER_TEXT = "Алёна, привет! У меня есть вопросы при общении с ботом-куратором"


def manager_with_copy_kb() -> InlineKeyboardMarkup:
    """Клавиатура: кнопка перехода к менеджеру + кнопка копирования текста + навигация."""
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="Написать менеджеру", url=MANAGER_LINK)],
        [InlineKeyboardButton(
            text="📋 Скопировать текст",
            copy_text=CopyTextButton(text=MANAGER_TEXT),
        )],
    ]
    rows.extend(nav_row(exclude={"manager"}))
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "manager")
async def contact_manager(callback: types.CallbackQuery):
    await callback.message.answer(
        f"Скопируй и отправь это сообщение менеджеру:\n\n"
        f"<code>{MANAGER_TEXT}</code>\n\n"
        f"Или нажми кнопку ниже, чтобы перейти в чат с менеджером.",
        reply_markup=manager_with_copy_kb(),
        parse_mode="HTML",
    )
    await callback.answer()
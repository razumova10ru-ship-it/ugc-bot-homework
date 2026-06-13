import logging
import os

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton

from keyboards.inline import nav_row
from config import MANAGER_LINK
from states.form import FormStates
from services.sheets import save_user_data

router = Router()
router.message.filter(F.chat.type == "private")
logger = logging.getLogger(__name__)

PHOTO_DIR = "user_photos"


def photo_done_with_copy_kb(copy_text: str) -> InlineKeyboardMarkup:
    """Клавиатура: кнопка перехода к менеджеру + кнопка копирования текста + навигация."""
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="Написать менеджеру", url=MANAGER_LINK)],
        [InlineKeyboardButton(
            text="📋 Скопировать текст для менеджера",
            copy_text=CopyTextButton(text=copy_text),
        )],
    ]
    rows.extend(nav_row(exclude={"manager"}))
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(FormStates.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    os.makedirs(PHOTO_DIR, exist_ok=True)

    photo = message.photo[-1]
    data = await state.get_data()
    user_id = message.from_user.id
    file_path = os.path.join(PHOTO_DIR, f"{user_id}_{photo.file_id}.jpg")

    await message.bot.download(file=photo.file_id, destination=file_path)
    logger.info("Фото сохранено: %s", file_path)

    # Обновляем таблицу — фото отправлено
    data["user_id"] = user_id
    data["photo_sent"] = True
    save_user_data(data)

    manager_text = "Алёна, привет! Я заполнил(а) Анкету на получение доступа к курсу"
    await message.answer(
        f"Фотография получена! ✅\n\n"
        f"Для завершения оформления доступа к обучению напиши менеджеру. "
        f"Нажми кнопку ниже — откроется чат с менеджером. "
        f"Скопируй и отправь ему это сообщение:\n\n"
        f"<code>{manager_text}</code>",
        reply_markup=photo_done_with_copy_kb(manager_text),
        parse_mode="HTML",
    )

    # Сообщение с инструкцией на будущее
    await message.answer(
        f"🎯 <b>Что дальше?</b>\n\n"
        f"Пока менеджер оформляет доступ, ты можешь настроить профиль и подготовить реферальные ссылки.\n\n"
        f"Когда оформишь профиль и понадобятся ссылки для размещения — возвращайся в бот и используй "
        f"конструктор меток (кнопка 🔖 <b>Создать реферальную ссылку</b> в меню).\n\n"
        f"Он создаст UTM-ссылки для:\n"
        f"• Шапки профиля\n"
        f"• Reels / TikTok / YouTube Shorts\n"
        f"• Автоматизации (ManyChat и др.)\n\n"
        f"Это твой главный инструмент заработка в программе! 💰",
        parse_mode="HTML",
    )
    await state.clear()


@router.message(FormStates.waiting_for_photo, F.document)
async def process_photo_document(message: types.Message, state: FSMContext):
    """Обработка фото, отправленных как файл (без сжатия)."""
    doc = message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await message.answer("Пожалуйста, отправьте фотографию (изображение).")
        return

    os.makedirs(PHOTO_DIR, exist_ok=True)
    data = await state.get_data()
    user_id = message.from_user.id
    file_path = os.path.join(PHOTO_DIR, f"{user_id}_{doc.file_id}.jpg")

    await message.bot.download(file=doc.file_id, destination=file_path)
    logger.info("Фото-документ сохранено: %s", file_path)

    data["user_id"] = user_id
    data["photo_sent"] = True
    save_user_data(data)

    manager_text = "Алёна, привет! Я заполнил(а) Анкету на получение доступа к курсу"
    await message.answer(
        f"Фотография получена! ✅\n\n"
        f"Для завершения оформления доступа к обучению напиши менеджеру. "
        f"Нажми кнопку ниже — откроется чат с менеджером. "
        f"Скопируй и отправь ему это сообщение:\n\n"
        f"<code>{manager_text}</code>",
        reply_markup=photo_done_with_copy_kb(manager_text),
        parse_mode="HTML",
    )

    # Сообщение с инструкцией на будущее
    await message.answer(
        f"🎯 <b>Что дальше?</b>\n\n"
        f"Пока менеджер оформляет доступ, ты можешь настроить профиль и подготовить реферальные ссылки.\n\n"
        f"Когда оформишь профиль и понадобятся ссылки для размещения — возвращайся в бот и используй "
        f"конструктор меток (кнопка 🔖 <b>Создать реферальную ссылку</b> в меню).\n\n"
        f"Он создаст UTM-ссылки для:\n"
        f"• Шапки профиля\n"
        f"• Reels / TikTok / YouTube Shorts\n"
        f"• Автоматизации (ManyChat и др.)\n\n"
        f"Это твой главный инструмент заработка в программе! 💰",
        parse_mode="HTML",
    )
    await state.clear()


@router.message(FormStates.waiting_for_photo)
async def process_photo_invalid(message: types.Message):
    await message.answer("Пожалуйста, отправьте фотографию (изображение).")
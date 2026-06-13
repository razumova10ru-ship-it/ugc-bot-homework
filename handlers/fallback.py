"""Обработчики-заглушки: отвечают, когда пользователь пишет текст
или нажимает неактуальную кнопку вне ожидаемого шага."""

import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

router = Router()
router.message.filter(F.chat.type == "private")
logger = logging.getLogger(__name__)

NO_STATE_TEXT = (
    "Привет! 👋 Я бот-куратор проекта UGC-креаторов Зерокодер.\n\n"
    "Я работаю с кнопками — просто нажмите /start, чтобы начать."
)

IN_FLOW_TEXT = (
    "Пожалуйста, используйте кнопки ниже для навигации 🙂\n\n"
    "Если что-то пошло не так, нажмите /start, чтобы начать заново."
)


@router.message(F.text)
async def text_fallback(message: types.Message, state: FSMContext):
    """Ловит текстовые сообщения, не перехваченные другими обработчиками."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(NO_STATE_TEXT)
    else:
        logger.info(
            "Текст вне обработчика: state=%s, user=%s",
            current_state,
            message.from_user.id,
        )
        await message.answer(IN_FLOW_TEXT)


@router.message()
async def general_fallback(message: types.Message, state: FSMContext):
    """Ловит стикеры, голосовые и прочие необработанные типы сообщений."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(NO_STATE_TEXT)
    else:
        await message.answer(IN_FLOW_TEXT)



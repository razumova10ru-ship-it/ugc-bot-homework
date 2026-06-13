import os

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from keyboards.inline import start_kb
from keyboards.menu import get_main_menu_kb

router = Router()
router.message.filter(F.chat.type == "private")

WELCOME_PHOTO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photo_ugc_bot.png")

WELCOME_TEXT = (
    "👋 Привет!\n\n"
    "🧑‍💻 Это бот-куратор проекта UGC-креаторов Зерокодер.\n\n"
    "Здесь ты узнаешь, как устроено сотрудничество, получишь доступ "
    "к обучению и сможешь присоединиться к нашей команде креаторов. 🚀\n\n"
    "Пользуйся меню внизу для быстрой навигации 👇"
)


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    photo = FSInputFile(WELCOME_PHOTO)
    await message.answer_photo(
        photo=photo,
        caption=WELCOME_TEXT,
        reply_markup=start_kb(),
        parse_mode="HTML",
    )
    # Отправляем постоянное меню
    await message.answer("Меню доступно внизу 👇", reply_markup=get_main_menu_kb())
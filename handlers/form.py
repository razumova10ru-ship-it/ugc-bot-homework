import logging

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from keyboards.inline import (
    source_kb,
    content_experience_kb,
    editing_level_kb,
    platform_access_kb,
    pd_consent_kb,
    privacy_policy_kb,
    offer_accept_kb,
    after_form_kb,
)
from states.form import FormStates
from config import PD_CONSENT_LINK, PRIVACY_POLICY_LINK, OFFER_LINK
from services.sheets import save_user_data

router = Router()
router.message.filter(F.chat.type == "private")
logger = logging.getLogger(__name__)

# Маппинги для человекочитаемых значений
SOURCE_MAP = {
    "source_threads": "Threads",
    "source_telegram": "Telegram",
    "source_friend": "От друга",
    "source_other": "Другое",
}

EXPERIENCE_MAP = {
    "exp_regular": "Снимаю и создаю регулярно — это часть моей жизни",
    "exp_sometimes": "Иногда создаю контент. Хочется больше",
    "exp_little": "Небольшой опыт",
}

EDITING_MAP = {
    "edit_basic": "Базовый — могу склеить и обрезать",
    "edit_confident": "Уверенный — эффекты, переходы, субтитры",
    "edit_advanced": "Продвинутый — переходы, цветокоррекция, motion",
}

PLATFORM_MAP = {
    "platform_yes": "Да, всё работает стабильно",
    "platform_partial": "Частично, к некоторым платформам есть не всегда",
}


# ── Старт анкеты ──────────────────────────────────────────────────────

FORM_INTRO = (
    "Отлично, давай двигаться дальше.\n\n"
    "Чтобы мы могли добавить тебя в рабочую группу в Telegram и выдать бесплатный доступ "
    "к обучению новой профессии от университета Зерокодер, нужно заполнить короткую анкету.\n\n"
    "Это поможет нам понять, кто ты, какой у тебя опыт и как лучше подключить тебя к проекту.\n\n"
    "И вот первый вопрос. Откуда узнали о наборе креаторов в Зерокодер?"
)


# ── Старт анкеты перенесён в navigation.py (callback_data="join") ──────

# ── 1. Откуда узнали ──────────────────────────────────────────────────

@router.callback_query(
    FormStates.waiting_for_source, F.data.startswith("source_")
)
async def process_source(callback: types.CallbackQuery, state: FSMContext):
    source = SOURCE_MAP.get(callback.data, callback.data)
    await state.update_data(source=source)
    await state.set_state(FormStates.waiting_for_full_name)
    await callback.message.answer("Ваши ФИО:")
    await callback.answer()


# ── 2. ФИО ─────────────────────────────────────────────────────────────

@router.message(FormStates.waiting_for_full_name, F.text)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(FormStates.waiting_for_telegram_nick)
    await message.answer("Ник в Телеграме:")


# ── 3. Ник ──────────────────────────────────────────────────────────────

@router.message(FormStates.waiting_for_telegram_nick, F.text)
async def process_telegram_nick(message: types.Message, state: FSMContext):
    await state.update_data(telegram_nick=message.text.strip())
    await state.set_state(FormStates.waiting_for_email)
    await message.answer("Электронная почта, на которую придёт обучение:")


# ── 4. Email ────────────────────────────────────────────────────────────

@router.message(FormStates.waiting_for_email, F.text)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        await message.answer("Похоже, это не email. Введите корректный адрес:")
        return
    await state.update_data(email=email)
    await state.set_state(FormStates.waiting_for_phone)
    await message.answer("Номер телефона для связи:")


# ── 5. Телефон ──────────────────────────────────────────────────────────

@router.message(FormStates.waiting_for_phone, F.text)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(FormStates.waiting_for_content_experience)
    await message.answer("Твой опыт в создании контента:", reply_markup=content_experience_kb())


# ── 6. Опыт ──────────────────────────────────────────────────────────────

@router.callback_query(
    FormStates.waiting_for_content_experience, F.data.startswith("exp_")
)
async def process_experience(callback: types.CallbackQuery, state: FSMContext):
    experience = EXPERIENCE_MAP.get(callback.data, callback.data)
    await state.update_data(content_experience=experience)
    await state.set_state(FormStates.waiting_for_editing_level)
    await callback.message.answer("Уровень монтажа:", reply_markup=editing_level_kb())
    await callback.answer()


# ── 7. Уровень монтажа ──────────────────────────────────────────────────

@router.callback_query(
    FormStates.waiting_for_editing_level, F.data.startswith("edit_")
)
async def process_editing(callback: types.CallbackQuery, state: FSMContext):
    editing = EDITING_MAP.get(callback.data, callback.data)
    await state.update_data(editing_level=editing)
    await state.set_state(FormStates.waiting_for_platform_access)
    await callback.message.answer(
        "Есть ли у тебя стабильный доступ ко всем основным платформам "
        "для публикации контента (YouTube, Instagram*, TikTok)?\n"
        "*Meta признана экстремистской организацией в РФ.",
        reply_markup=platform_access_kb(),
    )
    await callback.answer()


# ── 8. Доступ к платформам ──────────────────────────────────────────────

@router.callback_query(
    FormStates.waiting_for_platform_access, F.data.startswith("platform_")
)
async def process_platform(callback: types.CallbackQuery, state: FSMContext):
    platform = PLATFORM_MAP.get(callback.data, callback.data)
    await state.update_data(platform_access=platform)
    await state.set_state(FormStates.waiting_for_pd_consent)
    await callback.message.answer(
        f"Согласие на обработку персональных данных\n\n"
        f"<a href=\"{PD_CONSENT_LINK}\">Текст согласия</a>\n\n"
        f"Я даю согласие ООО «Зерокодер» на обработку моих персональных данных "
        f"в соответствии с текстом СОГЛАСИЯ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ, "
        f"включая сбор, хранение и передачу данных третьим лицам для целей "
        f"участия в проекте UGC-креаторов",
        reply_markup=pd_consent_kb(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await callback.answer()


# ── 9. Согласие на ПД ──────────────────────────────────────────────────

@router.callback_query(FormStates.waiting_for_pd_consent, F.data == "pd_consent_yes")
async def process_pd_consent(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(pd_consent=True)
    await state.set_state(FormStates.waiting_for_privacy_policy)
    await callback.message.answer(
        f"<a href=\"{PRIVACY_POLICY_LINK}\">Политика конфиденциальности</a>\n\n"
        f"Я подтверждаю, что ознакомлен(а) с ПОЛИТИКОЙ КОНФИДЕНЦИАЛЬНОСТИ "
        f"и принимаю её условия",
        reply_markup=privacy_policy_kb(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await callback.answer()


# ── 10. Политика конфиденциальности ─────────────────────────────────────

@router.callback_query(FormStates.waiting_for_privacy_policy, F.data == "privacy_yes")
async def process_privacy(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(privacy_accepted=True)
    await state.set_state(FormStates.waiting_for_offer_accept)
    await callback.message.answer(
        f"ДОГОВОР ОФЕРТЫ на оказание услуг по созданию и продвижению "
        f"пользовательского контента (UGC)\n\n"
        f"<a href=\"{OFFER_LINK}\">Текст договора оферты</a>\n\n"
        f"Я ознакомлен(а) с ДОГОВОРОМ ОФЕРТЫ на оказание услуг по созданию и "
        f"продвижению пользовательского контента (UGC) и полностью принимаю её условия (акцепт оферты).",
        reply_markup=offer_accept_kb(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await callback.answer()


# ── 11. Принятие оферты → завершение анкеты ─────────────────────────────

AFTER_FORM_TEXT = (
    "Супер, спасибо!\n"
    "Анкета заполнена, теперь мы можем подключить тебя к проекту.\n\n"
    "Вступай в рабочую группу в Telegram"
)


@router.callback_query(FormStates.waiting_for_offer_accept, F.data == "offer_accept_yes")
async def process_offer_accept(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(offer_accepted=True, user_id=callback.from_user.id)
    await state.set_state(FormStates.waiting_for_group_join)
    # Сохраняем данные в Google Sheets сразу — чтобы видеть потеряшек
    data = await state.get_data()
    save_user_data(data)
    await callback.message.answer(AFTER_FORM_TEXT, reply_markup=after_form_kb())
    await callback.answer()
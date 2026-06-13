"""UTM-генератор: создание реферальных ссылок с UTM-метками.

7 шагов для контента:
1. Выбор типа ссылки (контент / шапка / автоматизация)
2. Выбор платформы (+ шаг 2б для "Другое")
3. Ввод ника
4. Выбор формата контента (только для "контент")
5. Ввод описания креатива (только для "контент")
6. Выбор продукта
7. Ввод промокода (gcpc)

5 шагов для остальных типов.
"""

import logging
import re

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext

from db.onboarding_db import (
    get_onboarding_step,
    save_interrupted_state,
    clear_interrupted_state,
    save_utm_session,
    get_utm_session,
)
from states.utm import UTMStates
from states.onboarding import OnboardingStates
from config.products import PRODUCTS, get_product_by_slug, get_product_by_callback_id, FALLBACK_PRODUCT
from keyboards.utm import (
    link_type_kb,
    platform_kb,
    content_format_kb,
    products_kb,
    use_saved_data_kb,
    finish_utm_kb,
)

router = Router()
router.message.filter(F.chat.type == "private")
logger = logging.getLogger(__name__)

# ── Константы ───────────────────────────────────────────────────────────

PARTNERS_LINK = "https://university.zerocoder.ru/partners"

# Тексты шагов
TEXT_STEP_1 = (
    "🔖 <b>Генератор реферальных ссылок</b>\n\n"
    "Выбери тип ссылки:"
)

TEXT_STEP_2 = (
    "📱 <b>Выбери платформу</b>\n\n"
    "Где будет размещена ссылка?"
)

TEXT_STEP_2B = (
    "✍️ <b>Введи название платформы</b>\n\n"
    "На английском языке, без пробелов.\n\n"
    "Примеры: pinterest, twitch, x, linkedin\n\n"
    "⚠️ Только латинские буквы и цифры, длина 2–30 символов."
)

TEXT_STEP_3 = (
    "👤 <b>Введи свой ник</b> (без @)\n\n"
    "Это будет utm_campaign — идентификатор кампании.\n"
    "Пример: ivanova_creates\n\n"
    "⚠️ Только латиница, цифры и _ (нижнее подчёркивание), 2–40 символов."
)

TEXT_STEP_4 = (
    "🎬 <b>Выбери формат контента</b>:"
)

TEXT_STEP_5 = (
    "🏷 <b>Придумай название для этого креатива</b>\n\n"
    "Оно войдёт в utm_content вместе с форматом:\n"
    "  {format}_твоё_название\n\n"
    "Примеры:\n"
    "  reels_python_hook_01\n"
    "  story_free_lesson\n"
    "  post_ai_tools_review\n\n"
    "Правила:\n"
    "• Только латиница, цифры и _ (нижнее подчёркивание)\n"
    "• Без пробелов\n"
    "• Максимум 30 символов\n"
    "• Напиши что-то понятное — по этому названию ты потом найдёшь, какой именно ролик сработал\n\n"
    "Введи название:"
)

TEXT_STEP_6 = (
    "📦 <b>Выбери продукт</b>\n\n"
    "<b>Базовый подход:</b> размещайте вебинар, который относится либо к курсу, который вы сами проходите, либо к теме вашего блога. Можно не ограничиваться одним — пробуйте вести аудиторию на разные вебинары и тестировать разные автоматизации, чтобы понять, что заходит лучше.\n\n"
    "<b>Пример:</b> основная тема блога — ваше обучение вайбкодингу, но в какой-то момент вы выпускаете видео о том, как генерите картинки в нейросетях. Под это видео логично настроить автоматизацию по кодовому слову, которая ведёт уже на вебинар по визуалу с ИИ, — потому что человек пришёл именно за этой темой.\n\n"
    "<b>Ниже — вебинар под каждую программу.</b> Выберите программу из списка.\n\n"
    "💡 <b>Если твоей программы нет в списке:</b>\n"
    "У этих программ пока нет актуального вебинара:\n"
    "• Нейросети: от принципов к практике\n"
    "• Создание сайтов на WordPress\n"
    "• ИИ-копирайтинг\n"
    "• Нейросети для жизни\n"
    "• ИИ для бухгалтеров и финансистов\n\n"
    "Для них используйте кнопку «Другое» — ссылка будет вести на универсальный вебинар по Vibe Coding (https://zerocoder.ru/claude-code). Он заходит широкой аудитории и хорошо конвертирует.\n\n"
    "Выбери программу:"
)

TEXT_STEP_7 = (
    "🔑 <b>Введи свой партнёрский промокод (gcpc)</b>\n\n"
    "Это хвост, который GetCourse добавляет к твоим ссылкам.\n"
    "Пример: 612b3\n\n"
    "Где найти: перейди в раздел партнёрства и скопируй свой хвост.\n"
    f"🔗 Регистрация партнёра: {PARTNERS_LINK}\n\n"
    "⚠️ Только латинские буквы и цифры, от 3 до 15 символов."
)

TEXT_INVALID_PLATFORM = (
    "⚠️ Неверный формат платформы.\n\n"
    "Введи название на английском, без пробелов и спецсимволов.\n"
    "Примеры: pinterest, twitch, x, linkedin\n\n"
    "Длина: от 2 до 30 символов."
)

TEXT_INVALID_NICK = (
    "⚠️ Неверный формат ника.\n\n"
    "Используй только латинские буквы, цифры и _ (нижнее подчёркивание).\n"
    "Пример: ivanova_creates\n\n"
    "Длина: от 2 до 40 символов."
)

TEXT_INVALID_CREATIVE_ID = (
    "⚠️ Неверный формат названия.\n\n"
    "Используй только латинские буквы, цифры и _ (нижнее подчёркивание).\n"
    "Пример: python_hook_01\n\n"
    "Длина: от 2 до 30 символов."
)

TEXT_INVALID_PROMO = (
    "⚠️ Неверный формат промокода.\n\n"
    "Промокод должен содержать только латинские буквы и цифры.\n"
    "Длина: от 3 до 15 символов.\n\n"
    "Пример: 612b3"
)

# ── Вспомогательные функции ─────────────────────────────────────────────


def build_utm_url(data: dict, product: dict) -> str:
    """Собрать итоговую UTM-ссылку."""
    base_url = f"https://zerocoder.ru/{product['slug']}"

    params = {
        "gcpc": data["utm_promo_code"],
        "utm_source": "ugc" if data.get("utm_link_type") != "automation" else "automation",
        "utm_medium": data["utm_platform"],
        "utm_campaign": data["utm_nick"],
    }

    # utm_content только для типа "контент"
    if data.get("utm_link_type") == "content":
        params["utm_content"] = data["utm_content_full"]

    # utm_term — продукт, или fallback если нет вебинара
    if product.get("has_webinar"):
        params["utm_term"] = product["slug"]
    else:
        params["utm_term"] = FALLBACK_PRODUCT["slug"]

    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{base_url}?{query}"


def get_link_type_label(link_type: str) -> str:
    """Человекочитаемое название типа ссылки."""
    labels = {
        "content": "Контент",
        "bio": "Шапка профиля",
        "automation": "Автоматизация",
    }
    return labels.get(link_type, link_type)


def get_format_label(fmt: str) -> str:
    """Человекочитаемое название формата."""
    labels = {
        "reels": "Reels",
        "shorts": "Shorts",
        "story": "Story",
        "post": "Пост",
        "video": "Видео",
    }
    return labels.get(fmt, fmt)


# ── Старт UTM-генератора ────────────────────────────────────────────────


@router.callback_query(F.data == "utm_start")
@router.callback_query(F.data == "utm_start_from_onboarding")
async def utm_start(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Запуск UTM-генератора."""
    user_id = callback.from_user.id

    # Проверяем, есть ли сохранённая сессия
    session = await get_utm_session(user_id)

    if session and session.get("nick") and session.get("promo_code"):
        # Предлагаем использовать сохранённые данные
        await callback.message.answer(
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
        await callback.message.answer(
            TEXT_STEP_1,
            parse_mode="HTML",
            reply_markup=link_type_kb(),
        )

    await callback.answer()


@router.callback_query(F.data == "utm_use_saved_yes")
async def utm_use_saved_yes(callback: types.CallbackQuery, state: FSMContext):
    """Использовать сохранённые данные — сразу к выбору типа ссылки."""
    await state.set_state(UTMStates.choosing_link_type)
    await callback.message.answer(
        TEXT_STEP_1,
        parse_mode="HTML",
        reply_markup=link_type_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "utm_use_saved_no")
async def utm_use_saved_no(callback: types.CallbackQuery, state: FSMContext):
    """Ввести заново — очищаем сессию и начинаем сначала."""
    from db.onboarding_db import delete_utm_session
    await delete_utm_session(callback.from_user.id)
    await state.set_state(UTMStates.choosing_link_type)
    await callback.message.answer(
        TEXT_STEP_1,
        parse_mode="HTML",
        reply_markup=link_type_kb(),
    )
    await callback.answer()


# ── Шаг 1: Выбор типа ссылки ────────────────────────────────────────────


@router.callback_query(UTMStates.choosing_link_type, F.data.startswith("utm_type_"))
async def utm_choose_link_type(callback: types.CallbackQuery, state: FSMContext):
    """Выбор типа ссылки → переход к выбору платформы."""
    link_type_map = {
        "utm_type_content": "content",
        "utm_type_bio": "bio",
        "utm_type_automation": "automation",
    }
    link_type = link_type_map.get(callback.data)
    if not link_type:
        await callback.answer("Неверный тип ссылки", show_alert=True)
        return

    await state.update_data(utm_link_type=link_type)
    await state.set_state(UTMStates.choosing_platform)

    logger.info("UTM шаг 1: user_id=%s, тип=%s", callback.from_user.id, link_type)

    await callback.message.answer(
        TEXT_STEP_2,
        parse_mode="HTML",
        reply_markup=platform_kb(),
    )
    await callback.answer()


# ── Шаг 2: Выбор платформы ──────────────────────────────────────────────


@router.callback_query(UTMStates.choosing_platform, F.data.startswith("utm_platform_"))
async def utm_choose_platform(callback: types.CallbackQuery, state: FSMContext):
    """Выбор платформы → ввод ника или своя платформа."""
    platform_map = {
        "utm_platform_instagram": "instagram",
        "utm_platform_tiktok": "tiktok",
        "utm_platform_youtube": "youtube",
        "utm_platform_telegram": "telegram",
        "utm_platform_vk": "vk",
        "utm_platform_other": "other",
    }
    platform = platform_map.get(callback.data)
    if not platform:
        await callback.answer("Неверная платформа", show_alert=True)
        return

    await state.update_data(utm_platform=platform)
    logger.info("UTM шаг 2: user_id=%s, платформа=%s", callback.from_user.id, platform)

    if platform == "other":
        # Переход к шагу 2б — ввод своей платформы
        await state.set_state(UTMStates.entering_custom_platform)
        await callback.message.answer(TEXT_STEP_2B)
    else:
        # Переход к шагу 3 — ввод ника
        await state.set_state(UTMStates.entering_nick)
        await callback.message.answer(
            TEXT_STEP_3,
            parse_mode="HTML",
        )

    await callback.answer()


# ── Шаг 2б: Ввод своей платформы ────────────────────────────────────────


@router.message(UTMStates.entering_custom_platform, F.text)
async def utm_enter_custom_platform(message: types.Message, state: FSMContext):
    """Ввод своей платформы."""
    text = message.text.strip()

    # Валидация: только латиница и цифры, 2-30 символов
    if not re.match(r"^[a-zA-Z0-9]{2,30}$", text):
        await message.answer(TEXT_INVALID_PLATFORM)
        return

    await state.update_data(utm_platform=text)
    await state.set_state(UTMStates.entering_nick)

    logger.info("UTM шаг 2б: user_id=%s, платформа=%s", message.from_user.id, text)

    await message.answer(
        TEXT_STEP_3,
        parse_mode="HTML",
    )


# ── Шаг 3: Ввод ника ────────────────────────────────────────────────────


@router.message(UTMStates.entering_nick, F.text)
async def utm_enter_nick(message: types.Message, state: FSMContext):
    """Ввод ника → выбор формата (для контента) или продукта."""
    nick = message.text.strip()

    # Валидация: латиница, цифры, подчёркивания, 2-40 символов
    if not re.match(r"^[a-zA-Z0-9_]{2,40}$", nick):
        await message.answer(TEXT_INVALID_NICK)
        return

    await state.update_data(utm_nick=nick)
    logger.info("UTM шаг 3: user_id=%s, ник=%s", message.from_user.id, nick)

    # Проверяем тип ссылки
    data = await state.get_data()
    link_type = data.get("utm_link_type")

    if link_type == "content":
        # Для контента → шаг 4: выбор формата
        await state.set_state(UTMStates.choosing_content_format)
        await message.answer(
            TEXT_STEP_4,
            reply_markup=content_format_kb(),
        )
    else:
        # Для bio/automation → шаг 6: выбор продукта
        await state.set_state(UTMStates.choosing_product)
        await message.answer(
            TEXT_STEP_6,
            reply_markup=products_kb(),
        )


# ── Шаг 4: Выбор формата контента (только для "контент") ───────────────


@router.callback_query(UTMStates.choosing_content_format, F.data.startswith("utm_format_"))
async def utm_choose_content_format(callback: types.CallbackQuery, state: FSMContext):
    """Выбор формата контента → ввод описания креатива."""
    format_map = {
        "utm_format_reels": "reels",
        "utm_format_shorts": "shorts",
        "utm_format_story": "story",
        "utm_format_post": "post",
        "utm_format_video": "video",
    }
    content_format = format_map.get(callback.data)
    if not content_format:
        await callback.answer("Неверный формат", show_alert=True)
        return

    await state.update_data(utm_content_format=content_format)
    await state.set_state(UTMStates.entering_creative_id)

    logger.info("UTM шаг 4: user_id=%s, формат=%s", callback.from_user.id, content_format)

    # Формируем текст с подстановкой формата
    text = TEXT_STEP_5.format(format=content_format)
    await callback.message.answer(text)
    await callback.answer()


# ── Шаг 5: Ввод описания креатива (только для "контент") ───────────────


@router.message(UTMStates.entering_creative_id, F.text)
async def utm_enter_creative_id(message: types.Message, state: FSMContext):
    """Ввод описания креатива → выбор продукта."""
    creative_id = message.text.strip()

    # Валидация: латиница, цифры, подчёркивания, 2-30 символов
    if not re.match(r"^[a-zA-Z0-9_]{2,30}$", creative_id):
        await message.answer(TEXT_INVALID_CREATIVE_ID)
        return

    # Собираем итоговый utm_content
    data = await state.get_data()
    content_format = data.get("utm_content_format")
    utm_content_full = f"{content_format}_{creative_id}"

    await state.update_data(utm_creative_id=creative_id, utm_content_full=utm_content_full)
    await state.set_state(UTMStates.choosing_product)

    logger.info("UTM шаг 5: user_id=%s, creative_id=%s, utm_content=%s", message.from_user.id, creative_id, utm_content_full)

    await message.answer(
        TEXT_STEP_6,
        reply_markup=products_kb(),
    )


# ── Шаг 6: Выбор продукта ───────────────────────────────────────────────


@router.callback_query(UTMStates.choosing_product, F.data.startswith("utm_product_"))
async def utm_choose_product(callback: types.CallbackQuery, state: FSMContext):
    """Выбор продукта → ввод промокода."""
    callback_id = callback.data.replace("utm_product_", "")

    # Если выбрано "Другое" — используем fallback продукт (Vibe Coding)
    if callback_id == "other":
        from config.products import FALLBACK_PRODUCT
        product = FALLBACK_PRODUCT
        product_name = "Другое (Vibe Coding)"
    else:
        product = get_product_by_callback_id(callback_id)
        if not product:
            await callback.answer("Неверный продукт", show_alert=True)
            return
        product_name = product["name"]

    await state.update_data(utm_product_slug=product["slug"], utm_product_name=product_name)
    await state.set_state(UTMStates.entering_promo_code)

    logger.info("UTM шаг 6: user_id=%s, продукт=%s", callback.from_user.id, product["slug"])

    await callback.message.answer(
        TEXT_STEP_7,
        parse_mode="HTML",
    )
    await callback.answer()


# ── Шаг 7: Ввод промокода ───────────────────────────────────────────────


@router.message(UTMStates.entering_promo_code, F.text)
async def utm_enter_promo_code(message: types.Message, state: FSMContext, bot: Bot):
    """Ввод промокода → генерация ссылки."""
    text = message.text.strip()

    # Очищаем от лишних символов: ?gcpc=, gcpc=, &
    promo_code = text
    promo_code = promo_code.replace("?gcpc=", "").replace("gcpc=", "").replace("&", "").strip()

    # Валидация: латиница и цифры, 3-15 символов
    if not re.match(r"^[a-zA-Z0-9]{3,15}$", promo_code):
        await message.answer(TEXT_INVALID_PROMO)
        return

    # Сохраняем промокод
    await state.update_data(utm_promo_code=promo_code)
    logger.info("UTM шаг 7: user_id=%s, промокод=%s", message.from_user.id, promo_code)

    # Генерируем ссылку
    await generate_and_send_link(message, state, bot)


# ── Генерация и отправка ссылки ─────────────────────────────────────────


async def generate_and_send_link(message: types.Message, state: FSMContext, bot: Bot):
    """Генерация и отправка готовой UTM-ссылки."""
    data = await state.get_data()

    link_type = data.get("utm_link_type")
    platform = data.get("utm_platform")
    nick = data.get("utm_nick")
    product_slug = data.get("utm_product_slug")
    product_name = data.get("utm_product_name")
    promo_code = data.get("utm_promo_code", "")

    # Получаем продукт
    product = get_product_by_slug(product_slug)
    if not product:
        product = FALLBACK_PRODUCT

    # Собираем ссылку
    full_url = build_utm_url(data, product)

    # Сохраняем сессию (ник + промокод) в SQLite
    user_id = message.from_user.id
    await save_utm_session(user_id, nick, promo_code)

    # Сохраняем UTM-данные в Google Sheets
    try:
        from services.sheets import update_onboarding_field
        update_onboarding_field(user_id, "utm_nick", nick)
        update_onboarding_field(user_id, "utm_promo_code", promo_code)
        update_onboarding_field(user_id, "last_utm_link", full_url)
        logger.info("UTM-данные сохранены в Google Sheets для пользователя %s", user_id)
    except Exception as e:
        logger.error("Не удалось сохранить UTM-данные в Google Sheets: %s", e)

    # Отправляем 3 сообщения
    # Сообщение 1: ссылка
    await message.answer(
        f"🔗 <b>Твоя реферальная ссылка готова:</b>\n\n"
        f"<code>{full_url}</code>\n\n"
        f"Нажми и удерживай для копирования.",
        parse_mode="HTML",
    )

    # Сообщение 2: расшифровка
    link_type_label = get_link_type_label(link_type)
    platform_label = platform.capitalize() if platform else "N/A"

    result_text = (
        f"📍 <b>Параметры ссылки:</b>\n\n"
        f"🏷 Тип: {link_type_label}\n"
        f"📱 Платформа: {platform_label}\n"
        f"👤 Ник (кампания): {nick}\n"
    )

    if link_type == "content":
        content_format = data.get("utm_content_format", "N/A")
        creative_id = data.get("utm_creative_id", "N/A")
        utm_content = data.get("utm_content_full", "N/A")
        result_text += (
            f"🎬 Формат: {get_format_label(content_format)}\n"
            f"🏷 Креатив: {creative_id}\n"
            f"📌 utm_content: {utm_content}\n"
        )

    result_text += (
        f"📦 Продукт: {product_name}\n"
        f"🔑 Промокод: {promo_code}"
    )

    await message.answer(result_text, parse_mode="HTML")

    # Сообщение 3: завершение
    await message.answer(
        "✅ Сохрани ссылку и используй её в контенте.\n\n"
        f"По utm_content={data.get('utm_content_full', 'N/A')} ты сможешь отследить именно этот креатив в аналитике.\n\n"
        "Хочешь создать ещё одну?",
        reply_markup=finish_utm_kb(),
    )

    # Восстанавливаем онбординг если было прерывание
    await restore_onboarding_if_needed(message, state, bot)


# ── Восстановление онбординга ───────────────────────────────────────────


async def restore_onboarding_if_needed(message: types.Message, state: FSMContext, bot: Bot):
    """Проверка и восстановление онбординга после UTM."""
    from db.onboarding_db import get_interrupted_state, clear_interrupted_state
    from handlers.onboarding import STEP_4_TEXT, STEP_5_TEXT, step_4_kb, step_5_kb

    user_id = message.from_user.id
    interrupted_step = await get_interrupted_state(user_id)

    if interrupted_step:
        # Был прерван онбординг — восстанавливаем
        await clear_interrupted_state(user_id)

        step = int(interrupted_step)
        if step == 4:
            await message.answer(
                "↩️ <b>Возвращаемся к онбордингу</b>\n\n" + STEP_4_TEXT,
                parse_mode="HTML",
                reply_markup=step_4_kb(),
            )
        elif step == 5:
            await message.answer(
                "↩️ <b>Возвращаемся к онбордингу</b>\n\n" + STEP_5_TEXT,
                parse_mode="HTML",
                reply_markup=step_5_kb(),
            )

        logger.info("Восстановлен онбординг для пользователя %s (шаг %d)", user_id, step)

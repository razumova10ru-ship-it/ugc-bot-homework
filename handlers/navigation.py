"""Навигация между экранами — работает из любого состояния FSM."""

import logging

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext

from keyboards.inline import start_kb, offer_kb, group_join_kb, manager_kb, education_kb, photo_request_kb
from states.form import FormStates
from config import GROUP_ID, GROUP_INVITE_LINK, EDUCATION_FORM_LINK
from services.sheets import save_user_data

from handlers.start import WELCOME_TEXT
from handlers.offer import OFFER_TEXT
from handlers.form import FORM_INTRO, source_kb

router = Router()
router.callback_query.filter(F.message.chat.type == "private")
# Исключаем callback'ы UTM-генератора
router.callback_query.filter(~F.data.startswith("utm_"))
logger = logging.getLogger(__name__)

GROUP_WELCOME_TEXT = (
    "Вступайте в группу UGC-креаторов по ссылке: "
    f"{GROUP_INVITE_LINK}\n\n"
    "Там у нас находятся различные топики. И это наша основная группа по коммуникации и проекту.\n\n"
    "• Первым делом загляните в «Начни отсюда».\n\n"
    "• В разделах <b>ВАЖНО! Новости и анонсы</b> и <b>Аккаунты</b> находятся памятки. "
    "После получения доступа к обучению Зерокодер, следующее, что вам необходимо сделать, "
    "— это определиться с тем, какие аккаунты в социальных сетях вы будете вести. "
    "Вы как креатор можете создать новый аккаунт/аккаунты или вести свои имеющиеся аккаунты.\n\n"
    "• В разделе <b>Визитка</b> расскажите о себе.\n\n"
    "• В разделе <b>«Вопрос-ответ»</b> представлены различные вопросы и ответы. "
    "Если у вас появится какой-то вопрос, вы можете задать его кураторам, "
    "или можете воспользоваться топиком и задать его в топик.\n\n"
    "• В разделе <b>«Обучение блогингу»</b> у нас структурировано обучение по блогингу "
    "и монетизации контента. Там ответы на все интересующие вас вопросы, "
    "и само по себе оно для вас как дополнительный бонус — можно узнать много нового для себя. "
    "Рекомендуем начать его проходить вместе с созданием аккаунтов. Здесь всё индивидуально. "
    "У каждого креатора разные навыки в блогинге... И кому-то нужна большая поддержка, кому-то меньшая.\n\n"
    "• <b>Монетизация блога</b> — это бонус от Зерокодер. Каждый участник может стать партнёром "
    "и делать продажи со своего блога, получая процент от продаж — мы помогаем на каждом этапе. "
    "Также у нас предусмотрен ежемесячный конкурс для лучших креаторов с лучшими охватами "
    "и премия за залетевшие ролики (топик Конкурс от Зерокодер май-июнь).\n\n"
    "• <b>Сертификация UGC креатор</b>. Выпустите определённое количество контента, "
    "и мы дополнительно выдадим ценный Сертификат, подтверждающий сертификацию "
    "от крупного EdTech бренда, как приятное дополнение к кейсу.\n\n"
    "• Ну и, наконец, топик <b>Болталка</b>. Это наш общий топик, где мы обсуждаем все вопросы."
)


# ── В начало ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "nav_start")
async def nav_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(WELCOME_TEXT, reply_markup=start_kb())
    await callback.answer()


# ── Узнать подробнее (из любого состояния) ──────────────────────────────

@router.callback_query(F.data == "offer")
async def nav_offer(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(OFFER_TEXT, reply_markup=offer_kb(), parse_mode="HTML")
    await callback.answer()


# ── Начать анкету (из любого состояния) ────────────────────────────────

@router.callback_query(F.data == "join")
async def nav_join(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(FormStates.waiting_for_source)
    await callback.message.answer(FORM_INTRO, reply_markup=source_kb())
    await callback.answer()


# ── Вступить в группу (из любого состояния) ────────────────────────────

@router.callback_query(F.data == "nav_join_group")
async def nav_join_group(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("offer_accepted"):
        await state.set_state(FormStates.waiting_for_source)
        await callback.message.answer(
            "Сначала нужно заполнить анкету — это займёт пару минут.\n\n" + FORM_INTRO,
            reply_markup=source_kb(),
        )
        await callback.answer()
        return

    await state.set_state(FormStates.waiting_for_group_join)
    await callback.message.answer(GROUP_WELCOME_TEXT, reply_markup=group_join_kb(),
                                    parse_mode="HTML")
    await callback.answer()


# ── Проверка вступления в группу ────────────────────────────────────────

@router.callback_query(F.data == "check_group")
async def nav_check_group(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if not data.get("offer_accepted"):
        await state.set_state(FormStates.waiting_for_source)
        await callback.message.answer(
            "Сначала нужно заполнить анкету — это займёт пару минут.\n\n" + FORM_INTRO,
            reply_markup=source_kb(),
        )
        await callback.answer()
        return

    user_id = callback.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            await state.set_state(FormStates.waiting_for_education_form)
            data["user_id"] = user_id
            data["joined_group"] = True
            await state.update_data(joined_group=True)
            save_user_data(data)

            education_text = (
                "Остался последний шаг — получить бесплатное обучение от университета Зерокодер. "
                "Для этого нужно сделать буквально пару действий. "
                "Ознакомиться с реестром программ и выбирай подходящее обучение:\n\n"
                f"{EDUCATION_FORM_LINK}\n\n"
                "После заполнения формы нажми кнопку ниже ✅"
            )
            await callback.message.answer(education_text, reply_markup=education_kb(),
                                             disable_web_page_preview=True)
        else:
            await callback.message.answer(
                "Похоже, ты ещё не вступил в группу. Вступи, пожалуйста, "
                "и затем нажми «Я вступил в группу» ещё раз.",
                reply_markup=group_join_kb(),
            )
    except Exception:
        logger.exception("Ошибка проверки членства в группе")
        await callback.message.answer(
            "Не удалось проверить членство в группе. "
            "Нажми «Я вступил в группу» ещё раз.",
            reply_markup=group_join_kb(),
        )
    await callback.answer()


# ── Заполнил форму обучения → запрос фото ──────────────────────────────

@router.callback_query(F.data == "education_form_done")
async def education_form_done(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FormStates.waiting_for_photo)
    await state.update_data(education_form_filled=True, user_id=callback.from_user.id)
    data = await state.get_data()
    save_user_data(data)

    await callback.message.answer(
        "Отлично! Форма заполнена ✅\n\n"
        "📧 <b>Важно:</b> на почту придёт письмо от GetCourse — в нём будет указана "
        "стоимость программы, но для тебя как UGC-креатора курс полностью <b>БЕСПЛАТНЫЙ</b>.\n\n"
        "Это автоматическое письмо системы, не пугайся суммы. "
        "В течение 48 часов придёт второе письмо — уже с доступом к курсу.\n\n"
        "Теперь прикрепи, пожалуйста, свою фотографию.\n"
        "Она нужна для передачи данных в службу технической поддержки "
        "и оформления доступа к обучению.",
        reply_markup=photo_request_kb(),
        parse_mode="HTML",
    )
    await callback.answer()
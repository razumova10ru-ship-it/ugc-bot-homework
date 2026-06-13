from aiogram.fsm.state import State, StatesGroup


class FormStates(StatesGroup):
    waiting_for_source = State()
    waiting_for_full_name = State()
    waiting_for_telegram_nick = State()
    waiting_for_email = State()
    waiting_for_phone = State()
    waiting_for_content_experience = State()
    waiting_for_editing_level = State()
    waiting_for_platform_access = State()
    waiting_for_pd_consent = State()
    waiting_for_privacy_policy = State()
    waiting_for_offer_accept = State()
    waiting_for_group_join = State()
    waiting_for_education_form = State()
    waiting_for_photo = State()
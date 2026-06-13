"""FSM-состояния для онбординг-трека."""

from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """8 шагов онбординга + отдельные состояния для переходов."""

    # Шаг 1 — Доступ к обучению (ожидание подтверждения)
    waiting_for_access_confirm = State()

    # Шаг 2 — Аккаунты (ожидание подтверждения)
    waiting_for_accounts_confirm = State()

    # Шаг 3 — Дашборд (ожидание подтверждения)
    waiting_for_dashboard_confirm = State()

    # Шаг 4 — Реферальная ссылка (ожидание подтверждения)
    waiting_for_referral_confirm = State()

    # Шаг 5 — Настройка аккаунта (ожидание подтверждения)
    waiting_for_profile_confirm = State()

    # Шаг 6 — Первый Reels (ожидание ссылки)
    waiting_for_reels_link = State()

    # Шаг 7 — Завершение (финал)
    onboarding_complete = State()

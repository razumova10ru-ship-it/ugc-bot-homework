"""Состояния UTM-генератора."""

from aiogram.fsm.state import StatesGroup, State


class UTMStates(StatesGroup):
    """Состояния для UTM-генератора."""

    choosing_link_type = State()          # Шаг 1: тип ссылки (контент / bio / автоматизация)
    choosing_platform = State()           # Шаг 2: платформа
    entering_custom_platform = State()    # Шаг 2б: ввод своей платформы
    entering_nick = State()               # Шаг 3: ввод ника
    choosing_content_format = State()     # Шаг 4: формат контента (только для "контент")
    entering_creative_id = State()        # Шаг 5: описание креатива (только для "контент")
    choosing_product = State()            # Шаг 6: продукт
    entering_promo_code = State()         # Шаг 7: промокод (gcpc)

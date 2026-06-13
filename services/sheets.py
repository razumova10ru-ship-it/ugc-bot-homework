import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

_sheets_available = False

try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SPREADSHEET_ID, GOOGLE_SHEET_NAME

    if os.path.exists(GOOGLE_CREDENTIALS_FILE) and GOOGLE_SPREADSHEET_ID and GOOGLE_SPREADSHEET_ID != "your_spreadsheet_id_here":
        _sheets_available = True
        SCOPE = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
    else:
        logger.warning("Google Sheets не настроен — credentials.json или GOOGLE_SPREADSHEET_ID отсутствуют. Данные будут логироваться в консоль.")
except ImportError:
    logger.warning("Библиотека gspread не установлена. Данные будут логироваться в консоль.")


def _get_sheet():
    """Авторизация и подключение к Google Sheets."""
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_CREDENTIALS_FILE, SCOPE
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(GOOGLE_SPREADSHEET_ID)
    return spreadsheet.worksheet(GOOGLE_SHEET_NAME)


def _find_row_by_user_id(sheet, user_id: int) -> int | None:
    """Ищет строку по user_id (столбец A). Возвращает номер строки или None."""
    try:
        col_values = sheet.col_values(1)  # Столбец A — user_id
        for i, val in enumerate(col_values, start=1):
            if val == str(user_id):
                return i
    except Exception:
        logger.exception("Ошибка при поиске строки в Google Sheets")
    return None


def update_onboarding_field(user_id: int, field: str, value) -> bool:
    """Обновить поле онбординга или UTM для пользователя в Google Sheets.

    Столбцы для онбординга и UTM (добавляются к существующим):
    N - Текущий шаг онбординга
    O - Ссылка на Reels
    P - Дата завершения онбординга
    Q - UTM-ник
    R - UTM-промокод
    S - Последняя UTM-ссылка
    T - notified_48h
    U - notified_96h
    """
    logger.info("Обновление поля онбординга %s для пользователя %s: %s", field, user_id, value)

    if not _sheets_available:
        logger.info("Google Sheets недоступен. Онбординг: user_id=%s, field=%s, value=%s", user_id, field, value)
        return True

    try:
        sheet = _get_sheet()
        row_num = _find_row_by_user_id(sheet, user_id)

        if row_num:
            # Находим номер столбца для поля
            col_map = {
                "onboarding_step": 14,       # Столбец N
                "reels_link": 15,            # Столбец O
                "onboarding_completed": 16,  # Столбец P
                "utm_nick": 17,              # Столбец Q
                "utm_promo_code": 18,        # Столбец R
                "last_utm_link": 19,         # Столбец S
                "notified_48h": 20,          # Столбец T
                "notified_96h": 21,          # Столбец U
            }
            col = col_map.get(field)
            if col:
                sheet.update_cell(row_num, col, value)
                logger.info("Поле %s обновлено для пользователя %s (строка %s, столбец %s)", field, user_id, row_num, col)
                return True
            else:
                logger.warning("Неизвестное поле %s для обновления", field)
                return False
        else:
            logger.warning("Пользователь %s не найден в таблице для обновления поля %s", user_id, field)
            return False
    except Exception:
        logger.exception("Ошибка при обновлении поля онбординга в Google Sheets")
        return False


def save_user_data(data: dict) -> bool:
    """Сохраняет данные пользователя в Google Sheets.

    Если строка с таким user_id уже существует — обновляет её.
    Иначе — добавляет новую строку.

    Столбцы: user_id | Откуда узнал | ФИО | Ник Telegram | Email |
    Телефон | Опыт | Уровень монтажа | Доступ к платформам |
    Анкета обучения | Вступил в группу | Фото отправлено | Дата регистрации
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = data.get("user_id", "")

    row = [
        str(user_id),
        data.get("source", ""),
        data.get("full_name", ""),
        data.get("telegram_nick", ""),
        data.get("email", ""),
        data.get("phone", ""),
        data.get("content_experience", ""),
        data.get("editing_level", ""),
        data.get("platform_access", ""),
        "✅" if data.get("education_form_filled") else "",
        "✅" if data.get("joined_group") else "",
        "✅" if data.get("photo_sent") else "",
        now,
    ]

    if not _sheets_available:
        logger.info("Данные пользователя (без Sheets): %s", row)
        return True

    try:
        sheet = _get_sheet()
        existing_row = _find_row_by_user_id(sheet, user_id)

        if existing_row:
            sheet.update(f"A{existing_row}:M{existing_row}", [row])
            logger.info("Данные пользователя %s обновлены в Google Sheets (строка %s)", user_id, existing_row)
        else:
            sheet.append_row(row)
            logger.info("Данные пользователя %s добавлены в Google Sheets", user_id)
        return True
    except Exception:
        logger.exception("Ошибка при сохранении в Google Sheets")
        logger.info("Данные пользователя (fallback): %s", row)
        return False
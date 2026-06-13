import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "alena_tam")
MANAGER_LINK = f"https://t.me/{MANAGER_USERNAME}"

GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Лист1")

GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK", "https://t.me/+lKEFgtP1D6QxYzky")
EDUCATION_FORM_LINK = os.getenv(
    "EDUCATION_FORM_LINK",
    "https://forms.yandex.ru/u/69cba45a90fa7b60db57445b",
)

PD_CONSENT_LINK = os.getenv(
    "PD_CONSENT_LINK",
    "https://disk.yandex.ru/i/M_bmW0hrV2Zj-g",
)
PRIVACY_POLICY_LINK = os.getenv(
    "PRIVACY_POLICY_LINK",
    "https://disk.yandex.ru/i/YnBKJQ7zG7zxCQ",
)
OFFER_LINK = os.getenv(
    "OFFER_LINK",
    "https://disk.yandex.ru/i/ty56A5VlzlTEZQ",
)

GROUP_TOPIC_ACCOUNTS_LINK = os.getenv(
    "GROUP_TOPIC_ACCOUNTS_LINK",
    "https://t.me/c/3831898083/159",
)
GROUP_TOPIC_QA_LINK = os.getenv(
    "GROUP_TOPIC_QA_LINK",
    "https://t.me/c/3831898083/36",
)
DASHBOARD_FORM_LINK = os.getenv(
    "DASHBOARD_FORM_LINK",
    "https://forms.yandex.ru/cloud/6a0c6056493639001e3430ba/",
)
PARTNERS_LINK = os.getenv(
    "PARTNERS_LINK",
    "https://university.zerocoder.ru/partners",
)

from .products import (
    PRODUCTS,
    FALLBACK_PRODUCT,
    get_product_by_slug,
    get_products_with_webinar,
    get_products_without_webinar,
)

__all__ = [
    "BOT_TOKEN",
    "GROUP_ID",
    "MANAGER_USERNAME",
    "MANAGER_LINK",
    "GOOGLE_CREDENTIALS_FILE",
    "GOOGLE_SPREADSHEET_ID",
    "GOOGLE_SHEET_NAME",
    "GROUP_INVITE_LINK",
    "EDUCATION_FORM_LINK",
    "PD_CONSENT_LINK",
    "PRIVACY_POLICY_LINK",
    "OFFER_LINK",
    "GROUP_TOPIC_ACCOUNTS_LINK",
    "GROUP_TOPIC_QA_LINK",
    "DASHBOARD_FORM_LINK",
    "PARTNERS_LINK",
    "PRODUCTS",
    "FALLBACK_PRODUCT",
    "get_product_by_slug",
    "get_products_with_webinar",
    "get_products_without_webinar",
]

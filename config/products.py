"""Список продуктов для UTM-генератора.

Редактируется без перевыкатки бота.
Каждый продукт: callback_id (для кнопок, макс 52 символа),
                slug (для URL), название, есть ли вебинар.
"""

PRODUCTS = [
    # Программы с собственными вебинарами
    {"callback_id": "vizual-s-ai", "slug": "praktikum-vizualnyj-kontent-s-ai", "name": "Визуал с ИИ", "has_webinar": True},
    {"callback_id": "vibe-marketing", "slug": "open-lesson-on-vibe-marketing-with-ai", "name": "Vibe Marketing", "has_webinar": True},
    {"callback_id": "vibe-coding", "slug": "claude-code", "name": "Vibe Coding", "has_webinar": True},
    {"callback_id": "automation-n8n", "slug": "open-lesson-on-visual-automation-n8n", "name": "Автоматизация с n8n", "has_webinar": True},
    {"callback_id": "neuro-health", "slug": "neyroseti-dlya-zdorovya", "name": "Нейросети для здоровья", "has_webinar": True},
    {"callback_id": "neuro-pro", "slug": "online-workshop-for-professionals", "name": "Нейро-Про (Neuro Pro)", "has_webinar": True},
    {"callback_id": "perplexity", "slug": "bolshoy-praktikum-po-ii-agentu-perplexity-computer", "name": "Perplexity", "has_webinar": True},
    {"callback_id": "neuro-money", "slug": "podrabotka-na-ii-dlya-kazhdogo", "name": "Нейроденьги 2", "has_webinar": True},
    {"callback_id": "yandex-ai", "slug": "great-practical-workshop-on-the-ai-ecosystem-of-yandex-r", "name": "ИИ-Экосистема Яндекса", "has_webinar": True},
    {"callback_id": "ai-presentations", "slug": "big-practical-on-presentations-with-ai", "name": "ИИ-презентации", "has_webinar": True},
    {"callback_id": "chinese-ai", "slug": "new-practical-course-on-chinese-neural-networks", "name": "Китайские нейросети", "has_webinar": True},
]

# Программы БЕЗ вебинара — ведут на Vibe Coding
PRODUCTS_WITHOUT_WEBINAR = [
    {"name": "Нейросети: от принципов к практике"},
    {"name": "Создание сайтов на WordPress"},
    {"name": "ИИ-копирайтинг"},
    {"name": "Нейросети для жизни"},
    {"name": "ИИ для бухгалтеров и финансистов"},
]

# Fallback-продукт для программ без вебинара
FALLBACK_PRODUCT = {"slug": "claude-code", "name": "Vibe Coding"}


def get_product_by_callback_id(callback_id: str) -> dict | None:
    """Найти продукт по callback_id."""
    for product in PRODUCTS:
        if product.get("callback_id") == callback_id:
            return product
    return None


def get_product_by_slug(slug: str) -> dict | None:
    """Найти продукт по slug."""
    for product in PRODUCTS:
        if product["slug"] == slug:
            return product
    return None


def get_products_with_webinar() -> list[dict]:
    """Вернуть список продуктов с вебинарами."""
    return PRODUCTS


def get_products_without_webinar() -> list[dict]:
    """Вернуть список продуктов без вебинаров."""
    return PRODUCTS_WITHOUT_WEBINAR

---
name: ugc-onboarding-bot
description: Telegram-бот для автоматизации онбординга UGC-креаторов Zerocoder с UTM-генератором и Google Sheets интеграцией
metadata:
  type: project
  stack: Python, aiogram 3.x, SQLite, Google Sheets API, Docker
  status: production
---

# 🤖 UGC Onboarding Bot — навык для Claude Code

Этот навык предоставляет доступ к проекту Telegram-бота для автоматизации онбординга UGC-креаторов Zerocoder.

## 🎯 Назначение

Бот автоматизирует входную воронку для новых участников программы UGC-креаторов:
- Сбор анкетных данных (10 шагов)
- Проверка вступления в Telegram-группу
- Интеграция с Google Sheets
- UTM-генератор для создания реферальных ссылок
- Система уведомлений о застрявших участниках (48ч/96ч)

## 📁 Структура проекта

```
ugc-bot-homework/
├── bot.py                     # Точка входа
├── config/
│   ├── __init__.py           # ENV переменные
│   └── products.py           # Продукты Zerocoder
├── db/
│   └── onboarding_db.py      # SQLite операции
├── handlers/
│   ├── start.py              # Приветствие
│   ├── navigation.py         # Навигация
│   ├── form.py               # Анкета
│   ├── education.py          # Фото/обучение
│   ├── onboarding.py         # 7 шагов онбординга
│   ├── utm.py                # UTM-генератор
│   └── notifications.py      # Уведомления
├── keyboards/
│   ├── inline.py             # Inline кнопки
│   ├── menu.py               # Главное меню
│   └── utm.py                # UTM кнопки
├── states/
│   ├── form.py
│   ├── onboarding.py
│   └── utm.py
├── services/
│   └── sheets.py             # Google Sheets
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🚀 Команды

### Запуск локально

```bash
cd ugc-bot-homework
pip install -r requirements.txt
python bot.py
```

### Через Docker

```bash
docker compose up -d
docker compose logs -f
```

## 🔖 UTM-генератор

### 7 шагов для контента

1. **Тип ссылки** → Контент
2. **Платформа** → Instagram / TikTok / YouTube / Telegram / VK / Другое
3. **Ник** → `ivanova_creates`
4. **Формат** → Reels / Shorts / Story / Пост / Видео
5. **Креатив** → `python_hook_01`
6. **Продукт** → Визуал с ИИ / Vibe Coding / ... / Другое
7. **Промокод** → `612b3`

### Формула ссылки

```
https://zerocoder.ru/{slug}?gcpc={promo_code}
  &utm_source=ugc|automation
  &utm_medium={platform}
  &utm_campaign={nick}
  &utm_content={format}_{creative_id}
  &utm_term={product_slug|fallback}
```

### Продукты

**11 программ с вебинарами:**
- Визуал с ИИ
- Vibe Marketing
- Vibe Coding
- Автоматизация с n8n
- Нейросети для здоровья
- Нейро-Про
- Perplexity
- Нейроденьги 2
- ИИ-Экосистема Яндекса
- ИИ-презентации
- Китайские нейросети

**Без вебинара (ведут на Vibe Coding):**
- Нейросети: от принципов к практике
- Создание сайтов на WordPress
- ИИ-копирайтинг
- Нейросети для жизни
- ИИ для бухгалтеров и финансистов

## 📊 Google Sheets

| Столбец | Поле | Описание |
|---------|------|----------|
| A | user_id | ID Telegram |
| B–M | Анкета | Данные пользователя |
| N | onboarding_step | Текущий шаг |
| O | reels_link | Ссылка на Reels |
| P | onboarding_completed | Дата завершения |
| Q | utm_nick | UTM-ник |
| R | utm_promo_code | Промокод |
| S | last_utm_link | Последняя ссылка |
| T–U | notified | Уведомления 48ч/96ч |

## 🔐 Валидация

| Поле | Regex | Пример |
|------|-------|--------|
| Платформа | `^[a-zA-Z0-9]{2,30}$` | `pinterest` |
| Ник | `^[a-zA-Z0-9_]{2,40}$` | `ivanova_creates` |
| Креатив | `^[a-zA-Z0-9_]{2,30}$` | `python_hook_01` |
| Промокод | `^[a-zA-Z0-9]{3,15}$` | `612b3` |

## 📈 Метрики

- **Время онбординга:** 30–40 мин → 5 мин (**87% экономии**)
- **Конверсия в Reels:** 45% → 68% (**+23%**)
- **Ошибки в UTM:** 60% → <5% (**92% улучшение**)
- **Экономия кураторов:** 6–8 часов/неделю

## 🔗 Ссылки

- **Репозиторий:** https://github.com/razumova10ru-ship-it/ugc-bot-homework

## 👨‍💻 Автор

**Разумова Валерия**  
Бизнес-ассистент СЕО Zerocoder  
Проект реализован в рамках обучения Vibe Coding / Claude Code

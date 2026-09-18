"""
Создаёт REUSABLE_MODULES.md — каталог готовых наработок из VK-проекта,
которые можно перенести в MAX-продукт.
Запуск: python setup_reusable_modules.py
"""
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
DOC = BASE / "REUSABLE_MODULES.md"

PARTS = []

PARTS.append("# 🔧 REUSABLE MODULES — наработки для MAX-продукта")
PARTS.append("")
PARTS.append(f"**Дата:** {datetime.now().strftime('%d.%m.%Y')}")
PARTS.append("**Источник:** VKbot2 (текущий VK-проект)")
PARTS.append("**Цель:** перенести в MAX_PRODUCT_SPEC (новый продукт под МАКС)")
PARTS.append("")
PARTS.append("---")
PARTS.append("")

PARTS.append("## 🎯 Как использовать этот файл")
PARTS.append("")
PARTS.append("1. **Откройте новый чат** по MAX-продукту.")
PARTS.append("2. **Скиньте два файла:**")
PARTS.append("   - `MAX_PRODUCT_SPEC.md` — общая спецификация")
PARTS.append("   - `REUSABLE_MODULES.md` — этот файл (что можно перенести)")
PARTS.append("3. Напишите: «Начинаем MAX-продукт. Вот что можно переиспользовать.»")
PARTS.append("4. Ассистент поймёт, что уже готово, а что писать заново.")
PARTS.append("")
PARTS.append("---")
PARTS.append("")

# ============================================
# ЧАСТЬ 1: ЧТО ПЕРЕНОСИМ ЦЕЛИКОМ
# ============================================

PARTS.append("## ✅ 1. Что переносим ЦЕЛИКОМ (логика не меняется)")
PARTS.append("")
PARTS.append("Эти модули не зависят от платформы (VK или МАКС).")
PARTS.append("Логика остаётся той же — меняется только транспорт.")
PARTS.append("")

# 1.1 Слоты
PARTS.append("### 1.1. Логика слотов")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/storage/schedule.py`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- `get_free_slots()` — свободные слоты на дату")
PARTS.append("- `get_free_dates()` — свободные даты на N дней")
PARTS.append("- `get_busy_slots()` — занятые слоты с учётом буфера")
PARTS.append("- `book_slot()` — бронирование")
PARTS.append("- `cancel_booking()` — отмена")
PARTS.append("- `confirm_booking()` — подтверждение")
PARTS.append("- `add_custom_slot()` — открытие нерабочего слота")
PARTS.append("- `get_custom_slots()` — список кастомных слотов")
PARTS.append("")
PARTS.append("**Как переносить:**")
PARTS.append("- Скопировать логику")
PARTS.append("- Заменить `SQLITE_PATH` на PostgreSQL-подключение")
PARTS.append("- Добавить `tenant_id` в каждый запрос")
PARTS.append("- **Логика не меняется** — только источник данных")
PARTS.append("")

# 1.2 Расчёт дат
PARTS.append("### 1.2. Расчёт дат (без AI)")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/handlers/booking.py` → `parse_date_preference()`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- «завтра» → конкретная дата")
PARTS.append("- «через неделю» → конкретная дата")
PARTS.append("- «в субботу» → ближайшая суббота")
PARTS.append("- «15.10» → 15.10.2026")
PARTS.append("")
PARTS.append("**Как переносить:**")
PARTS.append("- Скопировать функцию **как есть**")
PARTS.append("- Она не зависит от платформы или БД")
PARTS.append("- Работает с чистыми строками")
PARTS.append("")

# 1.3 Определение языка
PARTS.append("### 1.3. Определение языка (без AI)")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/i18n/detector.py`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- `detect_language(text)` → 'ru' / 'he' / 'en'")
PARTS.append("- Иврит — по алфавиту")
PARTS.append("- Кириллица — точно русский")
PARTS.append("- Латиница — транслит или английский")
PARTS.append("")
PARTS.append("**Как переносить:**")
PARTS.append("- Скопировать **как есть**")
PARTS.append("- Для MAX-продукта (только Россия) — можно упростить до ru")
PARTS.append("- Но если планируете мультиязычность — оставить")
PARTS.append("")

# 1.4 Транслит
PARTS.append("### 1.4. Транслит (латиница → кириллица)")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/handlers/message_handler.py` → `LAYOUT_MAP`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- `ghbdat` → `привет`")
PARTS.append("- `pfgbcfnmcz` → `записаться`")
PARTS.append("")
PARTS.append("**Как переносить:**")
PARTS.append("- Скопировать `LAYOUT_MAP` и функцию `translit_to_ru()`")
PARTS.append("- Работает **как есть**")
PARTS.append("")

# 1.5 Нечёткий поиск команд
PARTS.append("### 1.5. Нечёткий поиск команд (difflib)")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/handlers/message_handler.py` → `fuzzy_match()`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- «привте» → «привет»")
PARTS.append("- «зописаца» → «записаться»")
PARTS.append("- «прайз» → «прайс»")
PARTS.append("")
PARTS.append("**Как переносить:**")
PARTS.append("- Скопировать функцию **как есть**")
PARTS.append("- Работает с `difflib` из стандартной библиотеки")
PARTS.append("")

# 1.6 AI-провайдер
PARTS.append("### 1.6. AI-провайдер (GigaChat)")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/ai/provider.py`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- `get_ai_response()` — ответ от GigaChat")
PARTS.append("- Кэш токена (25 минут)")
PARTS.append("- История диалога (последние 10 сообщений)")
PARTS.append("- System prompt")
PARTS.append("")
PARTS.append("**Как переносить:**")
PARTS.append("- Скопировать логику")
PARTS.append("- GigaChat остаётся провайдером для России")
PARTS.append("- Добавить `tenant_id` в историю диалогов")
PARTS.append("- Промпт адаптировать под бизнес-тип")
PARTS.append("")

# 1.7 Уведомления
PARTS.append("### 1.7. Уведомления мастеру")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/handlers/booking.py` → отправка `admin_msg`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- После записи — уведомление мастеру")
PARTS.append("- Формат: имя, телефон, услуга, дата, время")
PARTS.append("")
PARTS.append("**Как переносить:**")
PARTS.append("- Логика та же")
PARTS.append("- Меняется только транспорт (MAX API вместо VK)")
PARTS.append("")

PARTS.append("---")
PARTS.append("")

# ============================================
# ЧАСТЬ 2: ЧТО ПЕРЕНОСИМ С АДАПТАЦИЕЙ
# ============================================

PARTS.append("## 🔄 2. Что переносим С АДАПТАЦИЕЙ (меняется реализация)")
PARTS.append("")

# 2.1 Абстракция адаптера
PARTS.append("### 2.1. Абстракция адаптера")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/messaging/base.py`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- `MessageAdapter` — интерфейс")
PARTS.append("- `IncomingMessage` — универсальное сообщение")
PARTS.append("- `Button` — универсальная кнопка")
PARTS.append("- `MessageHandler` — тип обработчика")
PARTS.append("")
PARTS.append("**Как адаптировать:**")
PARTS.append("- **Оставить как есть** — интерфейсы универсальны")
PARTS.append("- Написать `max_adapter.py`, реализующий `MessageAdapter`")
PARTS.append("- Ничего в ядре не менять")
PARTS.append("")

# 2.2 VK-адаптер
PARTS.append("### 2.2. VK-адаптер → MAX-адаптер")
PARTS.append("")
PARTS.append("**Файл-источник:** `adapters/vk_adapter.py`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- LongPoll → получение событий")
PARTS.append("- `send_message()` → отправка")
PARTS.append("- Кнопки VK → клавиатура")
PARTS.append("")
PARTS.append("**Как адаптировать:**")
PARTS.append("- **LongPoll → Webhook** (принципиально разное)")
PARTS.append("- `vk.messages.send()` → `POST /messages` в MAX API")
PARTS.append("- VK-клавиатура → MAX-кнопки")
PARTS.append("- **Логика ядра не меняется**")
PARTS.append("")

# 2.3 Flask → FastAPI
PARTS.append("### 2.3. Flask → FastAPI")
PARTS.append("")
PARTS.append("**Файл-источник:** `web_demo.py`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- Flask-сервер")
PARTS.append("- Маршруты для кабинета")
PARTS.append("- Авторизация")
PARTS.append("")
PARTS.append("**Как адаптировать:**")
PARTS.append("- Flask → FastAPI (для Webhook МАКСа)")
PARTS.append("- Маршруты кабинета — переписать под FastAPI")
PARTS.append("- Авторизация — логика та же, синтаксис другой")
PARTS.append("")

# 2.4 SQLite → PostgreSQL
PARTS.append("### 2.4. SQLite → PostgreSQL")
PARTS.append("")
PARTS.append("**Файлы-источники:** все `core/storage/*.py`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- Работа с SQLite")
PARTS.append("- Прямые SQL-запросы")
PARTS.append("")
PARTS.append("**Как адаптировать:**")
PARTS.append("- SQLite → PostgreSQL (SQLAlchemy)")
PARTS.append("- Добавить `tenant_id` во все запросы")
PARTS.append("- Добавить миграции (Alembic)")
PARTS.append("")

PARTS.append("---")
PARTS.append("")

# ============================================
# ЧАСТЬ 3: ЧТО ПЕРЕНОСИМ КАК ЕСТЬ (ШАБЛОНЫ)
# ============================================

PARTS.append("## 📄 3. Что переносим КАК ЕСТЬ (HTML-шаблоны)")
PARTS.append("")
PARTS.append("Все шаблоны из `templates/` — **готовые**. Их можно использовать")
PARTS.append("в MAX-продукте почти без изменений.")
PARTS.append("")
PARTS.append("**Список шаблонов:**")
PARTS.append("")
PARTS.append("| Шаблон | Что делает | Адаптация |")
PARTS.append("|---|---|---|")
PARTS.append("| `_nav.html` | Меню кабинета | Добавить пункты MAX |")
PARTS.append("| `login.html` | Форма входа | Как есть |")
PARTS.append("| `forgot_password.html` | Восстановление пароля | Как есть |")
PARTS.append("| `admin.html` | Главная кабинета | Как есть |")
PARTS.append("| `schedule.html` | Расписание | Как есть |")
PARTS.append("| `bookings.html` | Список записей | Как есть |")
PARTS.append("| `calendar.html` | Календарь | Как есть |")
PARTS.append("| `stats.html` | Статистика | Как есть |")
PARTS.append("| `settings.html` | Настройки | Как есть |")
PARTS.append("| `new_booking.html` | Новая запись | Как есть |")
PARTS.append("| `booking_detail.html` | Детали записи | Как есть |")
PARTS.append("| `clients.html` | Список клиентов | Как есть |")
PARTS.append("| `client_detail.html` | Карточка клиента | Как есть |")
PARTS.append("| `client_edit.html` | Редактирование клиента | Как есть |")
PARTS.append("| `services.html` | Список услуг | Как есть |")
PARTS.append("| `service_edit.html` | Редактирование услуги | Как есть |")
PARTS.append("")
PARTS.append("**Что меняется:**")
PARTS.append("- В `_nav.html` — пункты меню (МАКС вместо VK)")
PARTS.append("- В `admin.html` — кнопка «Подключить МАКС» вместо «Подключить VK»")
PARTS.append("- Остальное — **как есть**")
PARTS.append("")

PARTS.append("---")
PARTS.append("")

# ============================================
# ЧАСТЬ 4: ЧТО ПЕРЕНОСИМ КАК ЕСТЬ (СТРУКТУРА)
# ============================================

PARTS.append("## 🗂 4. Что переносим КАК ЕСТЬ (структура проекта)")
PARTS.append("")
PARTS.append("```")
PARTS.append("maxbot/")
PARTS.append("├── core/                       # ЯДРО (переносим из VKbot2)")
PARTS.append("│   ├── messaging/              # абстракции")
PARTS.append("│   ├── handlers/               # логика бота")
PARTS.append("│   ├── ai/                     # AI-провайдер")
PARTS.append("│   ├── i18n/                   # переводы")
PARTS.append("│   ├── storage/                # работа с БД")
PARTS.append("│   └── auth/                   # авторизация")
PARTS.append("├── adapters/")
PARTS.append("│   └── max_adapter.py          # НОВОЕ (Webhook)")
PARTS.append("├── templates/                  # HTML (переносим)")
PARTS.append("├── data/")
PARTS.append("├── logs/")
PARTS.append("├── main.py                     # FastAPI вместо Flask")
PARTS.append("├── requirements.txt")
PARTS.append("└── .env")
PARTS.append("```")
PARTS.append("")
PARTS.append("**Что меняется:**")
PARTS.append("- `vk_adapter.py` → `max_adapter.py`")
PARTS.append("- `web_demo.py` → `main.py` (FastAPI)")
PARTS.append("- SQLite → PostgreSQL")
PARTS.append("")
PARTS.append("**Что НЕ меняется:**")
PARTS.append("- Структура `core/`")
PARTS.append("- Структура `templates/`")
PARTS.append("- Логика `handlers/`, `ai/`, `i18n/`, `storage/`")
PARTS.append("")

PARTS.append("---")
PARTS.append("")

# ============================================
# ЧАСТЬ 5: ЧТО ПЕРЕНОСИМ КАК ЕСТЬ (AI-ПРОМПТ)
# ============================================

PARTS.append("## 🤖 5. Что переносим КАК ЕСТЬ (AI-промпт)")
PARTS.append("")
PARTS.append("**Файл-источник:** `core/ai/provider.py` → `SYSTEM_PROMPT`")
PARTS.append("")
PARTS.append("**Что делает:**")
PARTS.append("- Описывает роль AI: «Ты ассистент...»")
PARTS.append("- Описывает услуги, цены")
PARTS.append("- Задаёт тон: дружелюбный, на «ты»")
PARTS.append("")
PARTS.append("**Как адаптировать:**")
PARTS.append("- Заменить «тату-салон» на «{{business_type}}»")
PARTS.append("- Сделать **шаблонным** — подставлять нишу из `tenants.business_type`")
PARTS.append("- Для MAX-продукта (только Россия) — оставить ru")
PARTS.append("")
PARTS.append("**Пример шаблона:**")
PARTS.append("```")
PARTS.append("Ты дружелюбный AI-ассистент {{business_name}}.")
PARTS.append("Сфера: {{business_type}}.")
PARTS.append("Твоя задача — консультировать и записывать клиентов.")
PARTS.append("...")
PARTS.append("```")
PARTS.append("")

PARTS.append("---")
PARTS.append("")

# ============================================
# ЧАСТЬ 6: ЧТО НЕ ПЕРЕНОСИМ
# ============================================

PARTS.append("## ❌ 6. Что НЕ переносим (не нужно для MAX)")
PARTS.append("")
PARTS.append("- **VK-специфичные скрипты** (install_*.py, fix_*.py)")
PARTS.append("- **VK-адаптер** (`vk_adapter.py`)")
PARTS.append("- **LongPoll-логика** — для MAX нужен Webhook")
PARTS.append("- **SQLite** — для MAX используем PostgreSQL")
PARTS.append("- **Flask** — для MAX используем FastAPI")
PARTS.append("")

PARTS.append("---")
PARTS.append("")

# ============================================
# ЧАСТЬ 7: ИТОГОВАЯ ТАБЛИЦА
# ============================================

PARTS.append("## 📊 7. Итоговая таблица")
PARTS.append("")
PARTS.append("| Модуль | Источник | Действие | Сложность |")
PARTS.append("|---|---|---|---|")
PARTS.append("| Логика слотов | `core/storage/schedule.py` | Перенести | Низкая |")
PARTS.append("| Расчёт дат | `core/handlers/booking.py` | Перенести | Низкая |")
PARTS.append("| Определение языка | `core/i18n/detector.py` | Перенести | Низкая |")
PARTS.append("| Транслит | `message_handler.py` | Перенести | Низкая |")
PARTS.append("| Нечёткий поиск | `message_handler.py` | Перенести | Низкая |")
PARTS.append("| AI-провайдер | `core/ai/provider.py` | Перенести | Низкая |")
PARTS.append("| Уведомления | `booking.py` | Адаптировать | Средняя |")
PARTS.append("| Абстракция адаптера | `core/messaging/base.py` | Как есть | Низкая |")
PARTS.append("| VK-адаптер → MAX | `adapters/vk_adapter.py` | **Переписать** | **Высокая** |")
PARTS.append("| Flask → FastAPI | `web_demo.py` | **Переписать** | **Средняя** |")
PARTS.append("| SQLite → PostgreSQL | `core/storage/*.py` | Адаптировать | Средняя |")
PARTS.append("| Шаблоны HTML | `templates/` | Как есть | Низкая |")
PARTS.append("| AI-промпт | `provider.py` | Шаблонизировать | Низкая |")
PARTS.append("")

PARTS.append("---")
PARTS.append("")

# ============================================
# ЧАСТЬ 8: ЧЕК-ЛИСТ ПЕРЕНОСА
# ============================================

PARTS.append("## ✅ 8. Чек-лист переноса")
PARTS.append("")
PARTS.append("### Шаг 1: Скопировать структуру")
PARTS.append("- [ ] Создать папку `maxbot/`")
PARTS.append("- [ ] Скопировать `core/` из VKbot2")
PARTS.append("- [ ] Скопировать `templates/` из VKbot2")
PARTS.append("- [ ] Создать `adapters/max_adapter.py` (заглушка)")
PARTS.append("")
PARTS.append("### Шаг 2: Адаптировать ядро")
PARTS.append("- [ ] Добавить `tenant_id` во все таблицы")
PARTS.append("- [ ] Перевести `core/storage/` на PostgreSQL")
PARTS.append("- [ ] Шаблонизировать AI-промпт")
PARTS.append("")
PARTS.append("### Шаг 3: Написать MAX-адаптер")
PARTS.append("- [ ] Webhook-сервер (FastAPI)")
PARTS.append("- [ ] Приём событий от МАКСа")
PARTS.append("- [ ] Отправка сообщений")
PARTS.append("- [ ] Кнопки, меню")
PARTS.append("")
PARTS.append("### Шаг 4: Адаптировать кабинет")
PARTS.append("- [ ] Flask → FastAPI")
PARTS.append("- [ ] Заменить кнопки VK на МАКС")
PARTS.append("- [ ] Добавить мультитенантность")
PARTS.append("")
PARTS.append("### Шаг 5: Тестирование")
PARTS.append("- [ ] Локальный тест (CloudPub)")
PARTS.append("- [ ] Тест Webhook от МАКСа")
PARTS.append("- [ ] Тест AI-консультаций")
PARTS.append("- [ ] Тест записи")
PARTS.append("")

PARTS.append("---")
PARTS.append("")

PARTS.append("## 📌 Как использовать в новом чате")
PARTS.append("")
PARTS.append("1. **Откройте новый чат** по MAX-продукту.")
PARTS.append("2. **Скиньте два файла:**")
PARTS.append("   - `MAX_PRODUCT_SPEC.md` — общая спецификация")
PARTS.append("   - `REUSABLE_MODULES.md` — этот файл")
PARTS.append("3. Напишите: **«Начинаем MAX-продукт. Вот что можно переиспользовать.»**")
PARTS.append("4. Ассистент **сразу поймёт**, что:")
PARTS.append("   - Уже готово (логика слотов, AI, даты, транслит)")
PARTS.append("   - Что адаптировать (SQLite → PostgreSQL)")
PARTS.append("   - Что писать заново (MAX-адаптер, FastAPI)")
PARTS.append("")

CONTENT = "\n".join(PARTS)


def main():
    if DOC.exists():
        backup = DOC.with_suffix(".md.bak")
        backup.write_text(DOC.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"📦 Бэкап: {backup.name}")

    DOC.write_text(CONTENT, encoding='utf-8')

    print(f"✅ REUSABLE_MODULES.md создан")
    print(f"   Размер: {len(CONTENT)} символов")
    print(f"   Строк: {CONTENT.count(chr(10))}")


if __name__ == '__main__':
    main()
"""
Заменяет хардкод-строки на {{ t('key', admin_lang) }} в шаблонах кабинета.
Запуск: python translate_templates.py
Существующие строки НЕ трогает, только заменяет известные.
"""
import re
from pathlib import Path
from datetime import datetime
import shutil

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"

# Пары: (что искать в HTML, на что заменить)
# Заменяем точные вхождения
REPLACEMENTS = {
    'admin.html': [
        ('<h2>Добро пожаловать!</h2>', '<h2>{{ t("admin_welcome_title", admin_lang) }}</h2>'),
        ('<p>Вы вошли как <b>{{ email }}</b></p>', '<p>{{ t("admin_welcome_text", admin_lang, email=email) }}</p>'),
        ('<h2>📋 Записи клиентов</h2>', '<h2>{{ t("admin_card_bookings_title", admin_lang) }}</h2>'),
        ('<p>Список всех записей, подтверждение и отмена.</p>', '<p>{{ t("admin_card_bookings_text", admin_lang) }}</p>'),
        ('<a href="/admin/bookings" class="action-btn">Открыть записи →</a>', '<a href="/admin/bookings" class="action-btn">{{ t("admin_card_bookings_btn", admin_lang) }}</a>'),
        ('<h2>📅 Расписание</h2>', '<h2>{{ t("admin_card_schedule_title", admin_lang) }}</h2>'),
        ('<p>Настройте свои рабочие часы по дням недели, добавьте выходные.</p>', '<p>{{ t("admin_card_schedule_text", admin_lang) }}</p>'),
        ('<a href="/admin/schedule" class="action-btn">Настроить расписание →</a>', '<a href="/admin/schedule" class="action-btn">{{ t("admin_card_schedule_btn", admin_lang) }}</a>'),
        ('<h2>🔐 Настройки</h2>', '<h2>{{ t("admin_card_settings_title", admin_lang) }}</h2>'),
        ('<p>Смена пароля, данные аккаунта.</p>', '<p>{{ t("admin_card_settings_text", admin_lang) }}</p>'),
        ('<a href="/admin/settings" class="action-btn">Открыть настройки →</a>', '<a href="/admin/settings" class="action-btn">{{ t("admin_card_settings_btn", admin_lang) }}</a>'),
        ('<h2>🚧 В разработке</h2>', '<h2>{{ t("admin_card_dev_title", admin_lang) }}</h2>'),
        ('<p>Скоро добавим:</p>', '<p>{{ t("admin_card_dev_text", admin_lang) }}</p>'),
        ('<li>📊 Статистика и выручка</li>', '<li>{{ t("admin_card_dev_stat", admin_lang) }}</li>'),
        ('<li>🗓 Календарь с записями</li>', '<li>{{ t("admin_card_dev_cal", admin_lang) }}</li>'),
        ('<li>💬 Интеграция с WhatsApp и Instagram</li>', '<li>{{ t("admin_card_dev_wa", admin_lang) }}</li>'),
    ],
    'schedule.html': [
        ('<h2>📅 Рабочие часы</h2>', '<h2>{{ t("schedule_title", admin_lang) }}</h2>'),
        ('<p class="subtitle">Укажите, в какие дни вы работаете и во сколько начинаете и заканчиваете.</p>', '<p class="subtitle">{{ t("schedule_subtitle", admin_lang) }}</p>'),
        ('<div class="alert alert-success">✅ Расписание сохранено</div>', '<div class="alert alert-success">{{ t("schedule_saved", admin_lang) }}</div>'),
        ('<label for="working_{{ day.weekday }}">Работаю</label>', '<label for="working_{{ day.weekday }}">{{ t("schedule_working", admin_lang) }}</label>'),
        ('<button type="submit" class="btn btn-primary">💾 Сохранить</button>', '<button type="submit" class="btn btn-primary">{{ t("schedule_save", admin_lang) }}</button>'),
        ('<a href="/admin" class="btn-secondary">← Назад</a>', '<a href="/admin" class="btn-secondary">{{ t("schedule_back", admin_lang) }}</a>'),
    ],
    'bookings.html': [
        ('<h2>📋 Записи клиентов</h2>', '<h2>{{ t("bookings_title", admin_lang) }}</h2>'),
        ('<p class="subtitle">Всего: {{ bookings|length }}</p>', '<p class="subtitle">{{ t("bookings_total", admin_lang, count=bookings|length) }}</p>'),
        ('class="{% if filter_type == \'all\' %}active{% endif %}">Все</a>', 'class="{% if filter_type == \'all\' %}active{% endif %}">{{ t("bookings_filter_all", admin_lang) }}</a>'),
        ('class="{% if filter_type == \'upcoming\' %}active{% endif %}">Предстоящие</a>', 'class="{% if filter_type == \'upcoming\' %}active{% endif %}">{{ t("bookings_filter_upcoming", admin_lang) }}</a>'),
        ('class="{% if filter_type == \'pending\' %}active{% endif %}">Ожидают</a>', 'class="{% if filter_type == \'pending\' %}active{% endif %}">{{ t("bookings_filter_pending", admin_lang) }}</a>'),
        ('class="{% if filter_type == \'past\' %}active{% endif %}">Прошедшие</a>', 'class="{% if filter_type == \'past\' %}active{% endif %}">{{ t("bookings_filter_past", admin_lang) }}</a>'),
        ('<th>Дата</th>', '<th>{{ t("bookings_th_date", admin_lang) }}</th>'),
        ('<th>Время</th>', '<th>{{ t("bookings_th_time", admin_lang) }}</th>'),
        ('<th>Клиент</th>', '<th>{{ t("bookings_th_client", admin_lang) }}</th>'),
        ('<th>Телефон</th>', '<th>{{ t("bookings_th_phone", admin_lang) }}</th>'),
        ('<th>Размер</th>', '<th>{{ t("bookings_th_size", admin_lang) }}</th>'),
        ('<th>Статус</th>', '<th>{{ t("bookings_th_status", admin_lang) }}</th>'),
        ('<th>Действия</th>', '<th>{{ t("bookings_th_actions", admin_lang) }}</th>'),
        ('<span class="status status-pending">Ожидает</span>', '<span class="status status-pending">{{ t("bookings_status_pending", admin_lang) }}</span>'),
        ('<span class="status status-confirmed">Подтверждено</span>', '<span class="status status-confirmed">{{ t("bookings_status_confirmed", admin_lang) }}</span>'),
        ('<span class="status status-cancelled">Отменено</span>', '<span class="status status-cancelled">{{ t("bookings_status_cancelled", admin_lang) }}</span>'),
        ('class="btn-action btn-confirm">✓ Подтвердить</a>', 'class="btn-action btn-confirm">{{ t("bookings_btn_confirm", admin_lang) }}</a>'),
        ('class="btn-action btn-cancel">✕ Отменить</a>', 'class="btn-action btn-cancel">{{ t("bookings_btn_cancel", admin_lang) }}</a>'),
        ('<p>Записей пока нет</p>', '<p>{{ t("bookings_empty", admin_lang) }}</p>'),
    ],
    'calendar.html': [
        ('<h2>{{ week_label }}</h2>', '<h2>{{ week_label }}</h2>'),
    ],
    'settings.html': [
        ('<h2>🔐 Смена пароля</h2>', '<h2>{{ t("settings_title", admin_lang) }}</h2>'),
        ('<p class="subtitle">Вы вошли как {{ email }}</p>', '<p class="subtitle">{{ t("settings_subtitle", admin_lang, email=email) }}</p>'),
        ('<label>Старый пароль</label>', '<label>{{ t("settings_old_password", admin_lang) }}</label>'),
        ('<label>Новый пароль (минимум 8 символов)</label>', '<label>{{ t("settings_new_password", admin_lang) }}</label>'),
        ('<label>Повторите новый пароль</label>', '<label>{{ t("settings_new_password2", admin_lang) }}</label>'),
        ('<button type="submit">💾 Сохранить</button>', '<button type="submit">{{ t("settings_save", admin_lang) }}</button>'),
        ('<a href="/admin" class="btn-secondary">← Назад</a>', '<a href="/admin" class="btn-secondary">{{ t("settings_back", admin_lang) }}</a>'),
    ],
}


def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_translate_{timestamp}"
    shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    print(f"📦 Бэкап: {backup_dir.name}")


def update_template(name: str, replacements: list) -> int:
    path = TEMPLATES / name
    if not path.exists():
        print(f"⏭️  Нет файла: {name}")
        return 0

    content = path.read_text(encoding='utf-8')
    count = 0

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
        else:
            print(f"   ⚠️  Не найдено в {name}: {old[:60]}")

    if count > 0:
        path.write_text(content, encoding='utf-8')
        print(f"✅ {name}: {count} замен")

    return count


def main():
    print("=" * 60)
    print("🚀 Перевод шаблонов на i18n")
    print("=" * 60)
    print()

    backup()
    print()

    total = 0
    for name, replacements in REPLACEMENTS.items():
        total += update_template(name, replacements)

    print()
    print("=" * 60)
    print(f"✅ Всего замен: {total}")
    print("=" * 60)


if __name__ == '__main__':
    main()
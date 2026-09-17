"""
Добавляет ключи статистики в JSON-файлы переводов.
Запуск: python add_stats_i18n.py
"""
import json
from pathlib import Path

BASE = Path(__file__).parent
I18N_DIR = BASE / "core" / "i18n"

NEW_RU = {
    "stats_title": "📊 Статистика",
    "stats_period_today": "Сегодня",
    "stats_period_week": "Эта неделя",
    "stats_period_month": "Этот месяц",
    "stats_period_all": "Всё время",
    "stats_total": "Всего записей",
    "stats_confirmed": "Подтверждено",
    "stats_pending": "Ожидает",
    "stats_cancelled": "Отменено",
    "stats_revenue": "Выручка",
    "stats_hours": "Загрузка",
    "stats_recent": "Последние записи",
}

NEW_EN = {
    "stats_title": "📊 Statistics",
    "stats_period_today": "Today",
    "stats_period_week": "This week",
    "stats_period_month": "This month",
    "stats_period_all": "All time",
    "stats_total": "Total bookings",
    "stats_confirmed": "Confirmed",
    "stats_pending": "Pending",
    "stats_cancelled": "Cancelled",
    "stats_revenue": "Revenue",
    "stats_hours": "Workload",
    "stats_recent": "Recent bookings",
}

NEW_HE = {
    "stats_title": "📊 סטטיסטיקה",
    "stats_period_today": "היום",
    "stats_period_week": "השבוע",
    "stats_period_month": "החודש",
    "stats_period_all": "כל הזמן",
    "stats_total": "סה\"כ הזמנות",
    "stats_confirmed": "מאושר",
    "stats_pending": "ממתין",
    "stats_cancelled": "מבוטל",
    "stats_revenue": "הכנסות",
    "stats_hours": "עומס",
    "stats_recent": "הזמנות אחרונות",
}


def update_json(lang: str, new_keys: dict):
    path = I18N_DIR / f"{lang}.json"

    if path.exists():
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    before = len(data)
    data.update(new_keys)
    after = len(data)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ {lang}.json: {before} → {after} ключей")


def main():
    print("=" * 60)
    print("🚀 Добавление ключей статистики")
    print("=" * 60)
    print()

    update_json('ru', NEW_RU)
    update_json('en', NEW_EN)
    update_json('he', NEW_HE)

    print()
    print("=" * 60)
    print("✅ Готово!")
    print("=" * 60)


if __name__ == '__main__':
    main()
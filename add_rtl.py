"""
Добавляет RTL для иврита во все шаблоны кабинета.
Заменяет <html lang="ru"> на динамический тег с dir="rtl" для he.
Запуск: python add_rtl.py
"""
from pathlib import Path
from datetime import datetime
import shutil

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"

TEMPLATES_TO_UPDATE = [
    'admin.html', 'schedule.html', 'bookings.html',
    'calendar.html', 'settings.html',
]

OLD_HTML_TAG = '<html lang="ru">'
NEW_HTML_TAG = '<html lang="{{ admin_lang }}" {% if admin_lang == \'he\' %}dir="rtl"{% endif %}>'


def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_rtl_{timestamp}"
    shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    print(f"📦 Бэкап: {backup_dir.name}")


def update_template(name: str) -> bool:
    path = TEMPLATES / name
    if not path.exists():
        print(f"⏭️  Нет файла: {name}")
        return False

    content = path.read_text(encoding='utf-8')

    if 'dir="rtl"' in content:
        print(f"⏭️  Уже обновлён: {name}")
        return False

    if OLD_HTML_TAG not in content:
        print(f"⚠️  Не найден <html lang=\"ru\"> в: {name}")
        return False

    content = content.replace(OLD_HTML_TAG, NEW_HTML_TAG, 1)
    path.write_text(content, encoding='utf-8')
    print(f"✅ Обновлён: {name}")
    return True


def main():
    print("=" * 60)
    print("🚀 Добавление RTL для иврита")
    print("=" * 60)
    print()

    backup()
    print()

    updated = 0
    for name in TEMPLATES_TO_UPDATE:
        if update_template(name):
            updated += 1

    print()
    print("=" * 60)
    print(f"✅ Готово! Обновлено: {updated}")
    print("=" * 60)


if __name__ == '__main__':
    main()
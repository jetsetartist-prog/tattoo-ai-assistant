"""
Исправляет ссылки на записи в календаре и списке записей.
- Календарь: клик по записи → /admin/bookings/<id>
- Список: клик по строке → /admin/bookings/<id>
Запуск: python fix_booking_links.py
"""
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"


def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_links_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    print(f"📦 Бэкап: {backup_dir.name}")


def fix_calendar():
    """Заменяет ссылку в календаре с /admin/bookings на /admin/bookings/<id>."""
    path = TEMPLATES / "calendar.html"
    if not path.exists():
        print("⚠️  Нет calendar.html")
        return

    content = path.read_text(encoding='utf-8')

    old = '<a href="/admin/bookings" style="text-decoration: none;">'
    new = '<a href="/admin/bookings/{{ b.id }}" style="text-decoration: none;">'

    if old in content:
        content = content.replace(old, new)
        path.write_text(content, encoding='utf-8')
        print("✅ calendar.html: ссылки исправлены")
    elif new in content:
        print("⏭️  calendar.html: уже исправлено")
    else:
        print("⚠️  calendar.html: не найден блок ссылки")


def fix_bookings():
    """Добавляет кликабельность строк в списке записей."""
    path = TEMPLATES / "bookings.html"
    if not path.exists():
        print("⚠️  Нет bookings.html")
        return

    content = path.read_text(encoding='utf-8')

    # Если уже есть onclick — пропускаем
    if 'onclick="window.location=' in content:
        print("⏭️  bookings.html: уже исправлено")
        return

    # Добавляем onclick на строку таблицы
    old_row = """                    <tr>
                        <td><b>{{ b.date_human }}</b></td>"""

    new_row = """                    <tr style="cursor: pointer;" onclick="window.location='/admin/bookings/{{ b.id }}'">
                        <td><b>{{ b.date_human }}</b></td>"""

    if old_row in content:
        content = content.replace(old_row, new_row)
        path.write_text(content, encoding='utf-8')
        print("✅ bookings.html: строки стали кликабельными")
    else:
        print("⚠️  bookings.html: не найден блок строки таблицы")


def main():
    print("=" * 60)
    print("🔗 Исправление ссылок на записи")
    print("=" * 60)
    print()

    backup()
    print()

    fix_calendar()
    fix_bookings()

    print()
    print("=" * 60)
    print("✅ Готово!")
    print("=" * 60)
    print()
    print("Что делать:")
    print("1. Перезапустите web_demo.py")
    print("2. Клик по записи в календаре → детали")
    print("3. Клик по строке в списке → детали")
    print()


if __name__ == '__main__':
    main()
"""
Упрощает клик по розовому слоту — без fetch, прямой переход на форму.
Запуск: python fix_simple_click.py
"""
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
CALENDAR = BASE / "templates" / "calendar.html"

# Старая JS-функция с fetch
OLD_FUNC = """        function confirmOpenSlot() {
            if (!pendingSlot) return;

            fetch('/admin/api/slots/open', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(pendingSlot)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const slot = pendingSlot;
                    closeOffSlotModal();
                    window.location.href = '/admin/bookings/new?date=' + slot.date + '&time=' + slot.time;
                } else {
                    alert('Ошибка: ' + (data.error || 'не удалось'));
                }
            })
            .catch(() => alert('Ошибка соединения'));

            pendingSlot = null;
        }"""

# Новая — просто переход
NEW_FUNC = """        function confirmOpenSlot() {
            if (!pendingSlot) return;
            const slot = pendingSlot;
            closeOffSlotModal();
            window.location.href = '/admin/bookings/new?date=' + slot.date + '&time=' + slot.time;
            pendingSlot = null;
        }"""


def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_simple_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if CALENDAR.exists():
        shutil.copy(CALENDAR, backup_dir / "calendar.html")
    print(f"📦 Бэкап: {backup_dir.name}")


def fix():
    content = CALENDAR.read_text(encoding='utf-8')

    if 'fetch(\'/admin/api/slots/open\'' not in content:
        print("⏭️  Уже упрощено")
        return

    if OLD_FUNC in content:
        content = content.replace(OLD_FUNC, NEW_FUNC)
        CALENDAR.write_text(content, encoding='utf-8')
        print("✅ confirmOpenSlot упрощена")
    else:
        print("⚠️  Точное совпадение не найдено — ищу fetch вручную")

        # Ищем блок fetch и заменяем его
        import re
        pattern = r"function confirmOpenSlot\(\) \{.*?\n        \}"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content.replace(match.group(0), NEW_FUNC)
            CALENDAR.write_text(content, encoding='utf-8')
            print("✅ confirmOpenSlot заменена (regex)")
        else:
            print("❌ Не удалось найти функцию")


def main():
    print("=" * 60)
    print("🔧 Упрощение клика по нерабочему слоту")
    print("=" * 60)
    print()

    backup()
    print()
    fix()

    print()
    print("=" * 60)
    print("✅ ГОТОВО")
    print("=" * 60)
    print()
    print("Теперь клик по розовому слоту:")
    print("  → сразу открывает форму новой записи")
    print("  → слот создастся при сохранении")
    print()


if __name__ == '__main__':
    main()
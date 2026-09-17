"""
ЭТАП 1f: Разделение слотов для бота и кабинета.

- Бот видит ТОЛЬКО рабочие слоты
- Кабинет видит рабочие + custom_slots (открытые мастером)
- Клиент НЕ МОЖЕТ записаться на custom_slots через бота

Запуск: python install_stage1f_separate_slots.py
"""
import json
import shutil
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).parent
CORE = BASE / "core" / "storage"
I18N = BASE / "core" / "i18n"
SCHEDULE = CORE / "schedule.py"
BOOKING = BASE / "core" / "handlers" / "booking.py"


# ============================================
# 1. schedule.py — добавляем get_free_slots_bot и get_free_slots_admin
# ============================================

CUSTOM_SLOTS_FUNCS = '''"""
Функции для работы с кастомными слотами.
get_free_slots_bot — только рабочие слоты (для бота)
get_free_slots_admin — рабочие + кастомные (для кабинета)
"""


def get_free_slots_bot(
    master_id: int,
    date_str: str,
    service_duration: int = 60,
    step_minutes: int = 30,
) -> list:
    """Свободные слоты для БОТА — только рабочие часы, без custom_slots."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    weekday = dt.weekday()

    # Выходной — нет слотов
    if is_day_off(master_id, date_str):
        return []

    wh = get_work_hours(master_id, weekday)
    if not wh or not wh.get("is_working"):
        return []

    work_start = _time_to_minutes(wh["start_time"])
    work_end = _time_to_minutes(wh["end_time"])

    busy = get_busy_slots(master_id, date_str)

    free = []
    current = work_start
    while current + service_duration <= work_end:
        slot_end = current + service_duration
        overlap = False
        for b_start, b_end in busy:
            if not (slot_end <= b_start or current >= b_end):
                overlap = True
                break
        if not overlap:
            free.append(_minutes_to_time(current))
        current += step_minutes

    return free


def get_free_slots_admin(
    master_id: int,
    date_str: str,
    service_duration: int = 60,
    step_minutes: int = 30,
) -> list:
    """Свободные слоты для КАБИНЕТА — рабочие + custom_slots."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    weekday = dt.weekday()

    busy = get_busy_slots(master_id, date_str)
    custom = set(get_custom_slots(master_id, date_str))

    # Выходной — только custom_slots
    if is_day_off(master_id, date_str):
        free = []
        for time_str in sorted(custom):
            current = _time_to_minutes(time_str)
            slot_end = current + service_duration
            overlap = False
            for b_start, b_end in busy:
                if not (slot_end <= b_start or current >= b_end):
                    overlap = True
                    break
            if not overlap:
                free.append(time_str)
        return free

    wh = get_work_hours(master_id, weekday)

    # День нерабочий по графику — только custom
    if not wh or not wh.get("is_working"):
        free = []
        for time_str in sorted(custom):
            current = _time_to_minutes(time_str)
            slot_end = current + service_duration
            overlap = False
            for b_start, b_end in busy:
                if not (slot_end <= b_start or current >= b_end):
                    overlap = True
                    break
            if not overlap:
                free.append(time_str)
        return free

    work_start = _time_to_minutes(wh["start_time"])
    work_end = _time_to_minutes(wh["end_time"])

    # Рабочие + кастомные
    candidates = set()
    current = work_start
    while current + service_duration <= work_end:
        candidates.add(current)
        current += step_minutes

    for time_str in custom:
        candidates.add(_time_to_minutes(time_str))

    free = []
    for start_min in sorted(candidates):
        slot_end = start_min + service_duration
        overlap = False
        for b_start, b_end in busy:
            if not (slot_end <= b_start or start_min >= b_end):
                overlap = True
                break
        if not overlap:
            free.append(_minutes_to_time(start_min))

    return free
'''


def update_schedule():
    """Добавляем функции get_free_slots_bot и get_free_slots_admin."""
    if not SCHEDULE.exists():
        print("  ⚠️  Нет schedule.py")
        return

    content = SCHEDULE.read_text(encoding='utf-8')

    if 'def get_free_slots_bot' in content:
        print("  ⏭️  schedule.py: функции уже есть")
        return

    # Вставляем перед def get_free_slots(
    marker = "def get_free_slots("
    if marker in content:
        content = content.replace(marker, CUSTOM_SLOTS_FUNCS + "\n\n" + marker, 1)
        SCHEDULE.write_text(content, encoding='utf-8')
        print("  ✅ schedule.py: get_free_slots_bot + get_free_slots_admin")
    else:
        print("  ⚠️  schedule.py: не найден блок get_free_slots")


# ============================================
# 2. booking.py — использовать get_free_slots_bot
# ============================================

def update_booking():
    """Бот должен использовать get_free_slots_bot."""
    if not BOOKING.exists():
        print("  ⚠️  Нет booking.py")
        return

    content = BOOKING.read_text(encoding='utf-8')

    # Импорт
    if 'get_free_slots_bot' not in content:
        old_import = "from core.storage.schedule import (\n    get_default_master,\n    get_all_services,\n    get_free_dates,\n    get_free_slots,\n    book_slot,\n)"
        new_import = "from core.storage.schedule import (\n    get_default_master,\n    get_all_services,\n    get_free_dates,\n    get_free_slots_bot,\n    book_slot,\n)"
        if old_import in content:
            content = content.replace(old_import, new_import)
            print("  ✅ booking.py: импорт get_free_slots_bot")
        else:
            # Пробуем другой вариант импорта
            if 'get_free_slots,' in content:
                content = content.replace('get_free_slots,', 'get_free_slots_bot,')
                print("  ✅ booking.py: импорт обновлён")

    # Заменяем вызовы get_free_slots на get_free_slots_bot
    if 'get_free_slots(' in content and 'get_free_slots_bot(' not in content:
        content = content.replace('get_free_slots(', 'get_free_slots_bot(')
        print("  ✅ booking.py: вызовы обновлены")

    BOOKING.write_text(content, encoding='utf-8')


# ============================================
# 3. web_demo.py — использовать get_free_slots_admin
# ============================================

WEB_DEMO = BASE / "web_demo.py"


def update_web_demo():
    """Кабинет должен использовать get_free_slots_admin."""
    if not WEB_DEMO.exists():
        print("  ⚠️  Нет web_demo.py")
        return

    content = WEB_DEMO.read_text(encoding='utf-8')

    # Импорт
    if 'get_free_slots_admin' not in content:
        if 'get_free_slots' in content:
            content = content.replace('get_free_slots,', 'get_free_slots_admin,')
            content = content.replace('get_free_slots)', 'get_free_slots_admin)')
            print("  ✅ web_demo.py: импорт get_free_slots_admin")

    # Заменяем вызовы (в admin_new_booking)
    if 'get_free_slots(' in content:
        content = content.replace('get_free_slots(', 'get_free_slots_admin(')
        print("  ✅ web_demo.py: вызовы обновлены")

    # Добавляем импорт если его нет
    if 'from core.storage.schedule import' in content and 'get_free_slots_admin' not in content:
        # Добавляем в существующий импорт
        old = 'from core.storage.schedule import ('
        if old in content:
            content = content.replace(
                old,
                old + '\n    get_free_slots_admin,',
                1
            )
            print("  ✅ web_demo.py: get_free_slots_admin в импорт")

    WEB_DEMO.write_text(content, encoding='utf-8')


# ============================================
# 4. Проверка
# ============================================

def check():
    print()
    print("🔍 Проверка:")
    try:
        from core.storage.schedule import get_free_slots_bot, get_free_slots_admin
        print("  ✅ get_free_slots_bot — импорт OK")
        print("  ✅ get_free_slots_admin — импорт OK")
    except Exception as e:
        print(f"  ❌ Ошибка импорта: {e}")


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_stage1f_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if SCHEDULE.exists():
        shutil.copy(SCHEDULE, backup_dir / "schedule.py")
    if BOOKING.exists():
        shutil.copy(BOOKING, backup_dir / "booking.py")
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    print(f"📦 Бэкап: {backup_dir.name}")
    print()


def main():
    print("=" * 60)
    print("🚀 ЭТАП 1f: Разделение слотов бот/кабинет")
    print("=" * 60)
    print()

    backup()

    print("🐍 schedule.py:")
    update_schedule()
    print()

    print("🐍 booking.py:")
    update_booking()
    print()

    print("🐍 web_demo.py:")
    update_web_demo()
    print()

    check()

    print()
    print("=" * 60)
    print("✅ ЭТАП 1f ГОТОВ")
    print("=" * 60)
    print()
    print("Логика:")
    print("  - Бот: get_free_slots_bot — только рабочие слоты")
    print("  - Кабинет: get_free_slots_admin — рабочие + custom_slots")
    print("  - Клиент НЕ МОЖЕТ записаться на custom_slots через бота")
    print("  - Мастер открывает конкретные слоты вручную")
    print()


if __name__ == '__main__':
    main()
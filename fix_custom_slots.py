"""
Fix: добавляет функции custom_slots в schedule.py + таблицу custom_slots в БД.

Запуск: python fix_custom_slots.py
"""
import sqlite3
import shutil
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).parent
SCHEDULE = BASE / "core" / "storage" / "schedule.py"
SQLITE_PATH = os.getenv("SQLITE_PATH", "data/leads.db")


# ============================================
# 1. Таблица custom_slots в БД
# ============================================

def update_db():
    print("📊 БД:")
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(master_id, date, time)
        )
    """)
    print("  ✅ Таблица custom_slots")

    conn.commit()
    conn.close()
    print()


# ============================================
# 2. Функции custom_slots
# ============================================

CUSTOM_FUNCS = '''

# ============================================
# КАСТОМНЫЕ СЛОТЫ (открытые вручную)
# ============================================

def add_custom_slot(master_id: int, date_str: str, time_str: str):
    """Открывает один нерабочий слот для записи."""
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO custom_slots (master_id, date, time)
        VALUES (?, ?, ?)
    """, (master_id, date_str, time_str))
    conn.commit()
    conn.close()
    logger.info(f"[Schedule] Открыт кастомный слот: {date_str} {time_str}")


def get_custom_slots(master_id: int, date_str: str) -> list:
    """Возвращает список кастомных слотов на дату."""
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT time FROM custom_slots
        WHERE master_id = ? AND date = ?
    """, (master_id, date_str))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def remove_custom_slot(master_id: int, date_str: str, time_str: str):
    """Закрывает кастомный слот."""
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM custom_slots
        WHERE master_id = ? AND date = ? AND time = ?
    """, (master_id, date_str, time_str))
    conn.commit()
    conn.close()
    logger.info(f"[Schedule] Закрыт кастомный слот: {date_str} {time_str}")
'''


def update_schedule():
    print("🐍 schedule.py:")
    if not SCHEDULE.exists():
        print("  ⚠️  Нет файла")
        return

    content = SCHEDULE.read_text(encoding='utf-8')

    if 'def add_custom_slot' in content:
        print("  ⏭️  Функции custom_slots уже есть")
        return

    # Вставляем перед первой функцией get_free_slots_*
    # Ищем marker
    markers = ['def get_free_slots_bot(', 'def get_free_slots_admin(', 'def get_free_slots(']
    inserted = False

    for marker in markers:
        if marker in content:
            content = content.replace(marker, CUSTOM_FUNCS + "\n\n" + marker, 1)
            inserted = True
            print(f"  ✅ Функции добавлены (перед {marker.strip()})")
            break

    if not inserted:
        # Если ни один не найден — добавляем в конец
        content += CUSTOM_FUNCS
        print("  ✅ Функции добавлены в конец файла")

    SCHEDULE.write_text(content, encoding='utf-8')


# ============================================
# 3. Также обновляем create_manual_booking
# ============================================

def fix_create_manual():
    """Обновляет create_manual_booking чтобы мог открывать кастомные слоты."""
    content = SCHEDULE.read_text(encoding='utf-8')

    # Проверяем, есть ли уже автоматическое открытие
    if 'add_custom_slot(master_id, date_str, time_str)' in content:
        print("  ⏭️  create_manual_booking уже обновлён")
        return

    # Ищем блок проверки в create_manual_booking
    old = '''    free = get_free_slots(master_id, date_str, duration)
    if time_str not in free:
        logger.warning(f"[Schedule] Слот {date_str} {time_str} уже занят")
        return None

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads (platform, user_id, name, phone, style, size, date_preference)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (source, "auto", name, phone, "", "", f"{date_str} {time_str}"))'''

    new = '''    free = get_free_slots(master_id, date_str, duration)
    if time_str not in free:
        # Проверяем, свободен ли слот фактически
        busy = get_busy_slots(master_id, date_str)
        start = _time_to_minutes(time_str)
        slot_end = start + duration
        overlap = False
        for b_start, b_end in busy:
            if not (slot_end <= b_start or start >= b_end):
                overlap = True
                break
        if overlap:
            logger.warning(f"[Schedule] Слот {date_str} {time_str} занят")
            return None
        # Открываем кастомно
        add_custom_slot(master_id, date_str, time_str)

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads (platform, user_id, name, phone, style, size, date_preference)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (source, "auto", name, phone, "", "", f"{date_str} {time_str}"))'''

    if old in content:
        content = content.replace(old, new)
        SCHEDULE.write_text(content, encoding='utf-8')
        print("  ✅ create_manual_booking обновлён")
    else:
        print("  ⚠️  create_manual_booking: блок не найден (возможно, уже обновлён)")


# ============================================
# MAIN
# ============================================

def main():
    print("=" * 60)
    print("🔧 Fix: custom_slots")
    print("=" * 60)
    print()

    # Бэкап
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_fix_slots_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if SCHEDULE.exists():
        shutil.copy(SCHEDULE, backup_dir / "schedule.py")
    print(f"📦 Бэкап: {backup_dir.name}")
    print()

    update_db()
    update_schedule()
    fix_create_manual()

    print()
    print("=" * 60)
    print("✅ ГОТОВО")
    print("=" * 60)
    print()
    print("Проверьте:")
    print('  python -c "from core.storage.schedule import get_free_slots_bot, get_free_slots_admin, add_custom_slot, get_custom_slots; print(\'OK\')"')
    print()


if __name__ == '__main__':
    main()
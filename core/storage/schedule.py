"""
Работа с расписанием: мастера, рабочие часы, выходные, услуги, записи.
Логика свободных слотов + пароли мастеров.
"""
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from loguru import logger

SQLITE_PATH = os.getenv("SQLITE_PATH", "data/leads.db")


# ============================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================

def init_schedule_db() -> None:
    """Создаёт таблицы для расписания, если их нет."""
    Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    # Мастера
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS masters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            telegram_id TEXT,
            vk_id TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Рабочие часы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER NOT NULL,
            weekday INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            is_working INTEGER DEFAULT 1,
            FOREIGN KEY (master_id) REFERENCES masters(id),
            UNIQUE(master_id, weekday)
        )
    """)

    # Выходные
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS days_off (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            reason TEXT,
            FOREIGN KEY (master_id) REFERENCES masters(id),
            UNIQUE(master_id, date)
        )
    """)

    # Услуги
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            price_from INTEGER,
            is_active INTEGER DEFAULT 1
        )
    """)

    # Записи
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER NOT NULL,
            lead_id INTEGER,
            service_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (master_id) REFERENCES masters(id),
            FOREIGN KEY (lead_id) REFERENCES leads(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    """)

    # Пароль мастера
    try:
        cursor.execute("ALTER TABLE masters ADD COLUMN password_hash TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE masters ADD COLUMN password_set_at TIMESTAMP")
    except sqlite3.OperationalError:
        pass

    # Поля для записей: notes, reference_image
    try:
        cursor.execute("ALTER TABLE bookings ADD COLUMN notes TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE bookings ADD COLUMN reference_image TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    logger.info("[Schedule] Таблицы расписания инициализированы")


def seed_default_data() -> None:
    """Создаёт мастера по умолчанию, график и услуги."""
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM masters")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO masters (name, email) VALUES (?, ?)",
            ("Мастер", "staffpm@yandex.ru"),
        )
        master_id = cursor.lastrowid
        logger.info(f"[Schedule] Создан мастер по умолчанию, id={master_id}")

        default_hours = [
            (master_id, 0, "10:00", "20:00", 1),
            (master_id, 1, "10:00", "20:00", 1),
            (master_id, 2, "10:00", "20:00", 1),
            (master_id, 3, "10:00", "20:00", 1),
            (master_id, 4, "10:00", "20:00", 1),
            (master_id, 5, "12:00", "18:00", 1),
            (master_id, 6, "00:00", "00:00", 0),
        ]
        cursor.executemany(
            "INSERT INTO work_hours (master_id, weekday, start_time, end_time, is_working) "
            "VALUES (?, ?, ?, ?, ?)",
            default_hours,
        )
        logger.info("[Schedule] Создан график по умолчанию")

    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        default_services = [
            ("Маленькая (до 10 см)", 60, 5000),
            ("Средняя (10-20 см)", 120, 10000),
            ("Большая (20+ см)", 180, 20000),
        ]
        cursor.executemany(
            "INSERT INTO services (name, duration_minutes, price_from) VALUES (?, ?, ?)",
            default_services,
        )
        logger.info("[Schedule] Созданы услуги по умолчанию")

    conn.commit()
    conn.close()


# ============================================
# МАСТЕРА
# ============================================

def get_default_master() -> Optional[dict]:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM masters WHERE is_active = 1 ORDER BY id LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_master(master_id: int) -> Optional[dict]:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM masters WHERE id = ?", (master_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_master_by_email(email: str) -> Optional[dict]:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM masters WHERE LOWER(email) = ?", (email.lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def set_master_password(master_id: int, password_hash: str) -> None:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE masters SET password_hash = ?, password_set_at = CURRENT_TIMESTAMP WHERE id = ?",
        (password_hash, master_id),
    )
    conn.commit()
    conn.close()
    logger.info(f"[Schedule] Пароль мастера id={master_id} обновлён")


def has_password(master_id: int) -> bool:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM masters WHERE id = ?", (master_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row and row[0])


# ============================================
# РАБОЧИЕ ЧАСЫ
# ============================================

def get_work_hours(master_id: int, weekday: int) -> Optional[dict]:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM work_hours WHERE master_id = ? AND weekday = ?",
        (master_id, weekday),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_work_hours(master_id: int) -> list:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM work_hours WHERE master_id = ? ORDER BY weekday",
        (master_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_work_hours(master_id: int, weekday: int, start: str, end: str, is_working: bool) -> None:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO work_hours (master_id, weekday, start_time, end_time, is_working)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(master_id, weekday) DO UPDATE SET
            start_time = excluded.start_time,
            end_time = excluded.end_time,
            is_working = excluded.is_working
    """, (master_id, weekday, start, end, 1 if is_working else 0))
    conn.commit()
    conn.close()


# ============================================
# ВЫХОДНЫЕ
# ============================================

def get_days_off(master_id: int, from_date: str = None, to_date: str = None) -> list:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if from_date and to_date:
        cursor.execute(
            "SELECT * FROM days_off WHERE master_id = ? AND date BETWEEN ? AND ? ORDER BY date",
            (master_id, from_date, to_date),
        )
    else:
        cursor.execute(
            "SELECT * FROM days_off WHERE master_id = ? ORDER BY date",
            (master_id,),
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_day_off(master_id: int, date_str: str) -> bool:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM days_off WHERE master_id = ? AND date = ?",
        (master_id, date_str),
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def add_day_off(master_id: int, date_str: str, reason: str = "") -> None:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO days_off (master_id, date, reason) VALUES (?, ?, ?)",
        (master_id, date_str, reason),
    )
    conn.commit()
    conn.close()


def remove_day_off(master_id: int, date_str: str) -> None:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM days_off WHERE master_id = ? AND date = ?",
        (master_id, date_str),
    )
    conn.commit()
    conn.close()


# ============================================
# УСЛУГИ
# ============================================

def get_all_services() -> list:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE is_active = 1 ORDER BY duration_minutes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_service(service_id: int) -> Optional[dict]:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============================================
# СЛОТЫ
# ============================================

def _time_to_minutes(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _minutes_to_time(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def get_busy_slots(master_id: int, date_str: str) -> list:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT time, duration FROM bookings "
        "WHERE master_id = ? AND date = ? AND status IN ('pending', 'confirmed')",
        (master_id, date_str),
    )
    rows = cursor.fetchall()
    conn.close()

    busy = []
    for time_str, duration in rows:
        start = _time_to_minutes(time_str)
        busy.append((start, start + duration))
    return busy


"""
Функции для работы с кастомными слотами.
get_free_slots_bot — только рабочие слоты (для бота)
get_free_slots_admin — рабочие + кастомные (для кабинета)
"""




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


def get_free_slots(
    master_id: int,
    date_str: str,
    service_duration: int = 60,
    step_minutes: int = 30,
) -> list:
    if is_day_off(master_id, date_str):
        return []

    dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    weekday = dt.weekday()

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


def get_free_dates(
    master_id: int,
    service_duration: int = 60,
    days_ahead: int = 14,
    from_date: str = None,
) -> list:
    if from_date:
        start = datetime.strptime(from_date, "%Y-%m-%d").date()
    else:
        start = datetime.now().date()

    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    result = []

    for i in range(days_ahead):
        d = start + timedelta(days=i)
        date_str = d.isoformat()

        slots = get_free_slots(master_id, date_str, service_duration)
        if slots:
            result.append({
                "date": date_str,
                "human": f"{d.strftime('%d.%m.%Y')} ({weekdays_ru[d.weekday()]})",
                "slots_count": len(slots),
                "first_slot": slots[0] if slots else None,
            })

    return result


# ============================================
# БРОНИРОВАНИЕ
# ============================================

def book_slot(
    master_id: int,
    date_str: str,
    time_str: str,
    duration: int,
    lead_id: int = None,
    service_id: int = None,
) -> Optional[int]:
    """Бронирует слот (из бота). Возвращает ID или None, если занят."""
    free = get_free_slots(master_id, date_str, duration)
    if time_str not in free:
        logger.warning(f"[Schedule] Слот {date_str} {time_str} уже занят")
        return None

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (master_id, lead_id, service_id, date, time, duration, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (master_id, lead_id, service_id, date_str, time_str, duration))
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"[Schedule] Забронирован слот: {date_str} {time_str} (id={booking_id})")
    return booking_id


def create_manual_booking(
    master_id: int,
    date_str: str,
    time_str: str,
    duration: int,
    name: str,
    phone: str,
    service_id: int = None,
    notes: str = "",
    reference_image: str = "",
    client_id: int = None,
    price: int = 0,
    deposit: int = 0,
    source: str = "manual",
) -> Optional[int]:
    """
    Создаёт запись вручную (от мастера или из бота).
    Возвращает ID записи или None, если слот занят.
    """
    free = get_free_slots(master_id, date_str, duration)
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
    """, (source, "auto", name, phone, "", "", f"{date_str} {time_str}"))
    lead_id = cursor.lastrowid

    status = 'confirmed' if source == 'manual' else 'pending'

    cursor.execute("""
        INSERT INTO bookings
            (master_id, lead_id, service_id, date, time, duration, status, notes, reference_image, client_id, price, deposit, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (master_id, lead_id, service_id, date_str, time_str, duration, status, notes, reference_image, client_id, price, deposit, source))
    booking_id = cursor.lastrowid

    conn.commit()
    conn.close()

    logger.info(f"[Schedule] Создана запись ({source}): {date_str} {time_str} (id={booking_id})")
    return booking_id


def get_booking(booking_id: int) -> Optional[dict]:
    """Возвращает запись со всеми деталями."""
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            b.*,
            l.name AS lead_name,
            l.phone AS lead_phone,
            s.name AS service_name,
            s.price_from AS price_from
        FROM bookings b
        LEFT JOIN leads l ON b.lead_id = l.id
        LEFT JOIN services s ON b.service_id = s.id
        WHERE b.id = ?
    """, (booking_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_booking(
    booking_id: int,
    notes: str = None,
    reference_image: str = None,
    status: str = None,
) -> None:
    """Обновляет запись."""
    updates = []
    params = []

    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)
    if reference_image is not None:
        updates.append("reference_image = ?")
        params.append(reference_image)
    if status is not None:
        updates.append("status = ?")
        params.append(status)

    if not updates:
        return

    params.append(booking_id)

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE bookings SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    logger.info(f"[Schedule] Обновлена запись id={booking_id}")


def get_bookings(master_id: int, date_str: str = None, from_date: str = None) -> list:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if date_str:
        cursor.execute(
            "SELECT * FROM bookings WHERE master_id = ? AND date = ? ORDER BY time",
            (master_id, date_str),
        )
    elif from_date:
        cursor.execute(
            "SELECT * FROM bookings WHERE master_id = ? AND date >= ? ORDER BY date, time",
            (master_id, from_date),
        )
    else:
        cursor.execute(
            "SELECT * FROM bookings WHERE master_id = ? ORDER BY date DESC, time DESC",
            (master_id,),
        )

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cancel_booking(booking_id: int) -> None:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bookings SET status = 'cancelled' WHERE id = ?",
        (booking_id,),
    )
    conn.commit()
    conn.close()
    logger.info(f"[Schedule] Отменена запись id={booking_id}")


def confirm_booking(booking_id: int) -> None:
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bookings SET status = 'confirmed' WHERE id = ?",
        (booking_id,),
    )
    conn.commit()
    conn.close()

def delete_booking(booking_id: int) -> bool:
    """Полностью удаляет запись из БД. Возвращает True, если удалено."""
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    if deleted:
        logger.info(f"[Schedule] Удалена запись id={booking_id}")
    return deleted


def update_booking_price(booking_id: int, price: int = None, deposit: int = None):
    """Обновляет стоимость и предоплату записи."""
    updates = []
    params = []

    if price is not None:
        updates.append("price = ?")
        params.append(price)
    if deposit is not None:
        updates.append("deposit = ?")
        params.append(deposit)

    if not updates:
        return

    params.append(booking_id)
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE bookings SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    logger.info(f"[Schedule] Обновлена цена записи id={booking_id}: price={price}, deposit={deposit}")

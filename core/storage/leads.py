"""
Работа с базой данных лидов (SQLite).
Платформо-независимо: работает с любым адаптером.
Также инициализирует таблицы расписания (masters, work_hours, days_off, services, bookings).
"""
import os
import sqlite3
import csv
from pathlib import Path
from loguru import logger

SQLITE_PATH = os.getenv("SQLITE_PATH", "data/leads.db")


def init_db() -> None:
    """Создаёт таблицу лидов и таблицы расписания."""
    Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    # Таблица лидов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            style TEXT,
            size TEXT,
            date_preference TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logger.info(f"[Storage] БД инициализирована: {SQLITE_PATH}")

    # Инициализируем таблицы расписания
    try:
        from core.storage.schedule import init_schedule_db, seed_default_data
        init_schedule_db()
        seed_default_data()
    except Exception as e:
        logger.error(f"[Storage] Ошибка инициализации расписания: {e}")


def save_lead(
    platform: str,
    user_id: str,
    name: str,
    phone: str,
    style: str = "",
    size: str = "",
    date_preference: str = "",
) -> int:
    """
    Сохраняет лид в SQLite и CSV.
    Возвращает ID созданного лида.
    """
    # SQLite
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (platform, user_id, name, phone, style, size, date_preference)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (platform, user_id, name, phone, style, size, date_preference))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # CSV (для быстрого экспорта)
    csv_path = "data/leads.csv"
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["platform", "user_id", "name", "phone", "style", "size", "date_preference"])
        writer.writerow([platform, user_id, name, phone, style, size, date_preference])

    logger.info(f"[Storage] Лид сохранён: platform={platform}, user={user_id}, name={name}, id={lead_id}")
    return lead_id


def get_all_leads() -> list:
    """Возвращает все лиды (для админ-панели)."""
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
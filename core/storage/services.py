"""
Управление услугами: CRUD.
"""
import os
import sqlite3
from typing import Optional
from loguru import logger

SQLITE_PATH = os.getenv("SQLITE_PATH", "data/leads.db")


def _connect():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_services(include_inactive: bool = False) -> list:
    conn = _connect()
    cur = conn.cursor()
    if include_inactive:
        cur.execute("SELECT * FROM services ORDER BY duration_minutes")
    else:
        cur.execute("SELECT * FROM services WHERE is_active = 1 ORDER BY duration_minutes")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_service(service_id: int) -> Optional[dict]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def create_service(name: str, duration_minutes: int, price_from: int = 0,
                   buffer_minutes: int = 30) -> int:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO services (name, duration_minutes, price_from, buffer_minutes)
        VALUES (?, ?, ?, ?)
    """, (name, duration_minutes, price_from, buffer_minutes))
    service_id = cur.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"[Services] Создана услуга id={service_id}: {name}")
    return service_id


def update_service(service_id: int, name: str = None, duration_minutes: int = None,
                   price_from: int = None, buffer_minutes: int = None,
                   is_active: bool = None):
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if duration_minutes is not None:
        updates.append("duration_minutes = ?")
        params.append(duration_minutes)
    if price_from is not None:
        updates.append("price_from = ?")
        params.append(price_from)
    if buffer_minutes is not None:
        updates.append("buffer_minutes = ?")
        params.append(buffer_minutes)
    if is_active is not None:
        updates.append("is_active = ?")
        params.append(1 if is_active else 0)

    if not updates:
        return

    params.append(service_id)
    conn = _connect()
    cur = conn.cursor()
    cur.execute(f"UPDATE services SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    logger.info(f"[Services] Обновлена услуга id={service_id}")


def delete_service(service_id: int):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("UPDATE services SET is_active = 0 WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()
    logger.info(f"[Services] Деактивирована услуга id={service_id}")


def hard_delete_service(service_id: int) -> bool:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bookings WHERE service_id = ?", (service_id,))
    if cur.fetchone()[0] > 0:
        conn.close()
        return False
    cur.execute("DELETE FROM services WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()
    return True

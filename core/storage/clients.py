"""
Работа с клиентами. Связка: имя + телефон.
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


def get_or_create_client(name: str, phone: str) -> int:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM clients
        WHERE LOWER(name) = LOWER(?) AND phone = ?
        LIMIT 1
    """, (name, phone))
    row = cur.fetchone()
    if row:
        conn.close()
        return row['id']

    cur.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
    client_id = cur.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"[Clients] Создан клиент id={client_id}: {name} ({phone})")
    return client_id


def get_client(client_id: int) -> Optional[dict]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_clients(search: str = "") -> list:
    conn = _connect()
    cur = conn.cursor()
    if search:
        cur.execute("""
            SELECT * FROM clients
            WHERE LOWER(name) LIKE LOWER(?) OR phone LIKE ?
            ORDER BY name
        """, (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT * FROM clients ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_client_stats(client_id: int) -> dict:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
               SUM(COALESCE(price, 0)) as total_revenue,
               SUM(COALESCE(deposit, 0)) as total_deposit
        FROM bookings
        WHERE client_id = ? AND status != 'cancelled'
    """, (client_id,))
    row = cur.fetchone()
    conn.close()

    total = row['total'] or 0
    revenue = row['total_revenue'] or 0
    deposit = row['total_deposit'] or 0

    return {
        'total_bookings': total,
        'confirmed_bookings': row['confirmed'] or 0,
        'total_revenue': revenue,
        'total_deposit': deposit,
        'average_check': revenue // total if total > 0 else 0,
    }


def get_client_bookings(client_id: int) -> list:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.*, s.name as service_name
        FROM bookings b
        LEFT JOIN services s ON b.service_id = s.id
        WHERE b.client_id = ?
        ORDER BY b.date DESC, b.time DESC
    """, (client_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_client(client_id: int, name: str = None, phone: str = None,
                  email: str = None, notes: str = None):
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if phone is not None:
        updates.append("phone = ?")
        params.append(phone)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)

    if not updates:
        return

    params.append(client_id)
    conn = _connect()
    cur = conn.cursor()
    cur.execute(f"UPDATE clients SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    logger.info(f"[Clients] Обновлён клиент id={client_id}")

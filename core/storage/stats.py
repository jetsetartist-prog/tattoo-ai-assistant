"""
Подсчёт статистики для кабинета мастера.
- Всего/подтверждено/ожидает/отменено
- Выручка
- Загрузка (часы)
"""
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

SQLITE_PATH = os.getenv("SQLITE_PATH", "data/leads.db")


def _connect():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_period_stats(master_id: int, period: str = "month") -> dict:
    """
    Возвращает статистику за период.

    period: 'today', 'week', 'month', 'all'
    """
    conn = _connect()
    cur = conn.cursor()

    today = datetime.now().date()

    if period == 'today':
        date_from = today.isoformat()
        date_to = today.isoformat()
        label = "Сегодня"
    elif period == 'week':
        date_from = (today - timedelta(days=today.weekday())).isoformat()
        date_to = (today + timedelta(days=6)).isoformat()
        label = "Эта неделя"
    elif period == 'month':
        date_from = today.replace(day=1).isoformat()
        # Последний день месяца
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        date_to = (next_month - timedelta(days=1)).isoformat()
        label = "Этот месяц"
    else:  # 'all'
        date_from = "2000-01-01"
        date_to = "2100-12-31"
        label = "Всё время"

    # Все записи за период (не отменённые)
    cur.execute("""
        SELECT
            b.id,
            b.date,
            b.time,
            b.duration,
            b.status,
            b.service_id,
            s.price_from
        FROM bookings b
        LEFT JOIN services s ON b.service_id = s.id
        WHERE b.master_id = ?
          AND b.date BETWEEN ? AND ?
    """, (master_id, date_from, date_to))

    rows = cur.fetchall()
    conn.close()

    total = len(rows)
    confirmed = sum(1 for r in rows if r['status'] == 'confirmed')
    pending = sum(1 for r in rows if r['status'] == 'pending')
    cancelled = sum(1 for r in rows if r['status'] == 'cancelled')

    # Выручка — только подтверждённые
    revenue = sum(
        (r['price_from'] or 0)
        for r in rows
        if r['status'] == 'confirmed'
    )

    # Загрузка — только подтверждённые + ожидающие
    total_minutes = sum(
        (r['duration'] or 0)
        for r in rows
        if r['status'] in ('confirmed', 'pending')
    )
    total_hours = total_minutes // 60

    return {
        'period': period,
        'label': label,
        'date_from': date_from,
        'date_to': date_to,
        'total': total,
        'confirmed': confirmed,
        'pending': pending,
        'cancelled': cancelled,
        'revenue': revenue,
        'total_hours': total_hours,
    }


def get_upcoming_count(master_id: int) -> int:
    """Сколько записей на будущие даты (не отменённых)."""
    conn = _connect()
    cur = conn.cursor()
    today = datetime.now().date().isoformat()
    cur.execute("""
        SELECT COUNT(*) as c
        FROM bookings
        WHERE master_id = ?
          AND date >= ?
          AND status != 'cancelled'
    """, (master_id, today))
    count = cur.fetchone()['c']
    conn.close()
    return count


def get_recent_bookings(master_id: int, limit: int = 5) -> list:
    """Последние N записей для превью."""
    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            b.id, b.date, b.time, b.status, b.duration,
            l.name, l.phone,
            s.name as service_name
        FROM bookings b
        LEFT JOIN leads l ON b.lead_id = l.id
        LEFT JOIN services s ON b.service_id = s.id
        WHERE b.master_id = ?
        ORDER BY b.date DESC, b.time DESC
        LIMIT ?
    """, (master_id, limit))

    rows = cur.fetchall()
    conn.close()

    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    result = []
    for r in rows:
        try:
            dt = datetime.strptime(r['date'], "%Y-%m-%d").date()
            date_human = f"{dt.strftime('%d.%m.%Y')} ({weekdays_ru[dt.weekday()]})"
        except Exception:
            date_human = r['date']

        result.append({
            'id': r['id'],
            'date': r['date'],
            'date_human': date_human,
            'time': r['time'],
            'status': r['status'],
            'duration': r['duration'],
            'name': r['name'] or '—',
            'phone': r['phone'] or '—',
            'service_name': r['service_name'] or '—',
        })

    return result
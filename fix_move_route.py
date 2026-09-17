"""Fix: добавляет маршрут /admin/api/bookings/move для drag&drop."""
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
WEB_DEMO = BASE / "web_demo.py"


ROUTE = '''# ============================================
# API: ПЕРЕМЕЩЕНИЕ ЗАПИСИ (drag & drop)
# ============================================

@app.route('/admin/api/bookings/move', methods=['POST'])
def admin_api_booking_move():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return jsonify({'success': False, 'error': 'Not authorized'}), 401

    data = request.json
    booking_id = data.get('booking_id')
    new_date = data.get('date')
    new_time = data.get('time')

    if not booking_id or not new_date or not new_time:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    booking = get_booking(booking_id)
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'}), 404

    master = get_default_master()
    duration = booking['duration']

    # Проверяем, свободен ли новый слот
    from core.storage.schedule import get_free_slots_admin
    free = get_free_slots_admin(master['id'], new_date, duration)

    # Если тот же слот — ок
    if not (new_date == booking['date'] and new_time == booking['time']):
        if new_time not in free:
            return jsonify({'success': False, 'error': 'Slot is busy'}), 400

    # Обновляем
    import sqlite3 as _sqlite3
    conn = _sqlite3.connect(os.getenv("SQLITE_PATH", "data/leads.db"))
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET date = ?, time = ? WHERE id = ?",
                (new_date, new_time, booking_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


'''


def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_fix_move_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    print(f"📦 Бэкап: {backup_dir.name}")


def fix():
    content = WEB_DEMO.read_text(encoding='utf-8')

    if '/admin/api/bookings/move' in content:
        print("⏭️  Маршрут уже есть")
        return

    marker = "if __name__ == '__main__':"
    if marker in content:
        content = content.replace(marker, ROUTE + marker, 1)
        WEB_DEMO.write_text(content, encoding='utf-8')
        print("✅ Маршрут /admin/api/bookings/move добавлен")
    else:
        print("❌ Не найден if __name__")


def main():
    print("=" * 60)
    print("🔧 Fix: маршрут drag & drop")
    print("=" * 60)
    print()
    backup()
    print()
    fix()
    print()
    print("=" * 60)
    print("✅ ГОТОВО")
    print("=" * 60)


if __name__ == '__main__':
    main()
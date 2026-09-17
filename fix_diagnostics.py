"""
Fix по результатам диагностики:
1. Добавляет маршрут /admin/api/bookings/move (drag&drop)
2. Добавляет ключ currency в JSON (ru/en/he)
3. Проверяет результат

Запуск: python fix_diagnostics.py
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
WEB_DEMO = BASE / "web_demo.py"
I18N = BASE / "core" / "i18n"


# ============================================
# 1. МАРШРУТ /admin/api/bookings/move
# ============================================

ROUTE_MOVE = '''# ============================================
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

    from core.storage.schedule import get_free_slots_admin
    free = get_free_slots_admin(master['id'], new_date, duration)

    if not (new_date == booking['date'] and new_time == booking['time']):
        if new_time not in free:
            return jsonify({'success': False, 'error': 'Slot is busy'}), 400

    import sqlite3 as _sqlite3
    conn = _sqlite3.connect(os.getenv("SQLITE_PATH", "data/leads.db"))
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET date = ?, time = ? WHERE id = ?",
                (new_date, new_time, booking_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


'''


# ============================================
# 2. ПЕРЕВОДЫ currency
# ============================================

I18N_CURRENCY = {
    "ru": {"currency": "Валюта"},
    "en": {"currency": "Currency"},
    "he": {"currency": "מטבע"},
}


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_fix_diag_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    if I18N.exists():
        shutil.copytree(I18N, backup_dir / "i18n", dirs_exist_ok=True)
    print(f"📦 Бэкап: {backup_dir.name}")


def fix_move_route():
    print("🔧 Маршрут /admin/api/bookings/move:")
    if not WEB_DEMO.exists():
        print("  ❌ Нет web_demo.py")
        return

    content = WEB_DEMO.read_text(encoding='utf-8')

    if '/admin/api/bookings/move' in content:
        print("  ⏭️  Уже есть")
        return

    marker = "if __name__ == '__main__':"
    if marker in content:
        content = content.replace(marker, ROUTE_MOVE + marker, 1)
        WEB_DEMO.write_text(content, encoding='utf-8')
        print("  ✅ Добавлен")
    else:
        print("  ❌ Не найден if __name__")


def fix_currency():
    print("🔧 Ключ currency в JSON:")
    for lang, data in I18N_CURRENCY.items():
        path = I18N / f"{lang}.json"
        if not path.exists():
            print(f"  ⚠️  Нет {lang}.json")
            continue
        with open(path, encoding='utf-8') as f:
            existing = json.load(f)
        if 'currency' in existing:
            print(f"  ⏭️  {lang}.json — уже есть")
            continue
        before = len(existing)
        existing.update(data)
        after = len(existing)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {lang}.json: {before} → {after}")


def main():
    print("=" * 60)
    print("🔧 Fix по диагностике")
    print("=" * 60)
    print()

    backup()
    print()

    fix_move_route()
    print()

    fix_currency()
    print()

    print("=" * 60)
    print("✅ ГОТОВО")
    print("=" * 60)
    print()
    print("Проверка:")
    print('  findstr /C:"admin_api_booking_move" web_demo.py')
    print('  python -c "import json; print(\'currency ru:\', json.load(open(\'core/i18n/ru.json\', encoding=\'utf-8\')).get(\'currency\'))"')
    print()


if __name__ == '__main__':
    main()
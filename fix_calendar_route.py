"""
Fix: заменяет функцию admin_calendar в web_demo.py целиком.
Запуск: python fix_calendar_route.py
"""
import re
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
WEB_DEMO = BASE / "web_demo.py"


NEW_FUNCTION = '''@app.route('/admin/calendar')
def admin_calendar():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    master = get_default_master()
    if not master:
        return "Мастер не найден", 500

    week_offset = int(request.args.get('week_offset', 0))

    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    sunday = monday + timedelta(days=6)

    all_bookings = get_bookings(master['id'])

    conn = sqlite3.connect(os.getenv("SQLITE_PATH", "data/leads.db"))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    from core.storage.schedule import get_all_work_hours, is_day_off, _time_to_minutes
    work_hours_list = get_all_work_hours(master['id'])
    work_hours_by_weekday = {wh['weekday']: wh for wh in work_hours_list}

    all_hours = set()
    for wh in work_hours_list:
        if wh.get('is_working'):
            start_h = _time_to_minutes(wh['start_time']) // 60
            end_h = _time_to_minutes(wh['end_time']) // 60
            for h in range(start_h, end_h):
                all_hours.add(h)

    if all_hours:
        hours = list(range(min(all_hours), max(all_hours) + 1))
    else:
        hours = list(range(10, 21))

    days = []
    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    for i in range(7):
        day_date = monday + timedelta(days=i)
        date_str = day_date.isoformat()
        weekday = day_date.weekday()

        wh = work_hours_by_weekday.get(weekday, {})
        is_working_day = bool(wh.get('is_working'))

        work_start_h = None
        work_end_h = None
        if is_working_day:
            work_start_h = _time_to_minutes(wh['start_time']) // 60
            work_end_h = _time_to_minutes(wh['end_time']) // 60

        is_off_day = (not is_working_day) or is_day_off(master['id'], date_str)

        working_hours = set()
        if not is_off_day:
            for h in range(work_start_h, work_end_h):
                working_hours.add(h)

        bookings_by_hour = {}

        for b in all_bookings:
            if b['date'] != date_str:
                continue
            if b['status'] == 'cancelled':
                continue

            try:
                hour = int(b['time'].split(':')[0])
            except Exception:
                continue

            cur.execute("SELECT * FROM leads WHERE id = ?", (b['lead_id'],))
            lead = cur.fetchone()

            if hour not in bookings_by_hour:
                bookings_by_hour[hour] = []

            bookings_by_hour[hour].append({
                'id': b['id'],
                'time': b['time'],
                'duration': b['duration'],
                'status': b['status'],
                'name': lead['name'] if lead else '—',
                'has_notes': bool(b.get('notes')),
                'has_image': bool(b.get('reference_image')),
            })

        days.append({
            'name': weekdays_ru[i],
            'day_num': day_date.strftime('%d.%m'),
            'date': date_str,
            'is_today': day_date == today,
            'is_off_day': is_off_day,
            'working_hours': working_hours,
            'bookings_by_hour': bookings_by_hour,
        })

    conn.close()

    week_label = f"{monday.strftime('%d.%m.%Y')} — {sunday.strftime('%d.%m.%Y')}"

    return _render_template_file(
        'calendar.html',
        days=days,
        hours=hours,
        week_label=week_label,
        week_offset=week_offset,
        active='calendar',
    )
'''


def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_fix_route_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    print(f"📦 Бэкап: {backup_dir.name}")


def fix_route():
    if not WEB_DEMO.exists():
        print("❌ Нет web_demo.py")
        return False

    content = WEB_DEMO.read_text(encoding='utf-8')

    # Проверяем, есть ли уже новая версия
    if 'work_hours_by_weekday' in content and 'is_off_day' in content:
        print("⏭️  Уже обновлено")
        return True

    # Ищем начало функции
    start_marker = "@app.route('/admin/calendar')"
    start_idx = content.find(start_marker)

    if start_idx == -1:
        print("❌ Не найден @app.route('/admin/calendar')")
        return False

    print(f"✅ Найдено начало на позиции {start_idx}")

    # Ищем КОНЕЦ функции: следующий '@app.route' или '# ====' после начала
    search_start = start_idx + len(start_marker)
    
    # Ищем следующий @app.route
    next_route = content.find("@app.route", search_start)
    
    # Ищем следующий разделитель # ====
    next_section = content.find("# ============================================", search_start)
    
    # Берём минимальный из них
    candidates = [x for x in [next_route, next_section] if x != -1]
    
    if not candidates:
        print("❌ Не найден конец функции")
        return False
    
    end_idx = min(candidates)
    
    print(f"✅ Найден конец на позиции {end_idx}")

    # Заменяем
    new_content = content[:start_idx] + NEW_FUNCTION.strip() + "\n\n\n" + content[end_idx:]
    WEB_DEMO.write_text(new_content, encoding='utf-8')
    print("✅ Функция admin_calendar заменена")
    return True


def main():
    print("=" * 60)
    print("🔧 Fix: замена admin_calendar")
    print("=" * 60)
    print()

    backup()
    print()

    success = fix_route()

    print()
    print("=" * 60)
    if success:
        print("✅ ГОТОВО")
    else:
        print("❌ ОШИБКА")
    print("=" * 60)
    print()

    if success:
        print("Проверьте:")
        print('  python -c "c = open(\'web_demo.py\', encoding=\'utf-8\').read(); print(\'is_off_day:\', \'is_off_day\' in c); print(\'work_hours_by_weekday:\', \'work_hours_by_weekday\' in c)"')
        print()


if __name__ == '__main__':
    main()
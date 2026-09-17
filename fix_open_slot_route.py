"""Fix: добавляет маршрут /admin/api/slots/open в web_demo.py."""
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
WEB_DEMO = BASE / "web_demo.py"


ROUTE = '''# ============================================
# API: ОТКРЫТИЕ НЕРАБОЧЕГО СЛОТА
# ============================================

@app.route('/admin/api/slots/open', methods=['POST'])
def admin_api_open_slot():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return jsonify({'success': False, 'error': 'Not authorized'}), 401

    data = request.json
    date_str = data.get('date')
    time_str = data.get('time')

    if not date_str or not time_str:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    master = get_default_master()
    if not master:
        return jsonify({'success': False, 'error': 'Master not found'}), 500

    from core.storage.schedule import add_custom_slot
    add_custom_slot(master['id'], date_str, time_str)

    return jsonify({'success': True})


'''


def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_fix_open_slot_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    print(f"📦 Бэкап: {backup_dir.name}")


def fix():
    if not WEB_DEMO.exists():
        print("❌ Нет web_demo.py")
        return

    content = WEB_DEMO.read_text(encoding='utf-8')

    if '/admin/api/slots/open' in content:
        print("⏭️  Маршрут уже есть")
        return

    marker = "if __name__ == '__main__':"
    if marker in content:
        content = content.replace(marker, ROUTE + marker, 1)
        WEB_DEMO.write_text(content, encoding='utf-8')
        print("✅ Маршрут /admin/api/slots/open добавлен")
    else:
        print("❌ Не найден if __name__")


def main():
    print("=" * 60)
    print("🔧 Fix: маршрут открытия слота")
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
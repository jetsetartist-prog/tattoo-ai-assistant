"""
Добавляет удаление записи:
- Функция delete_booking в schedule.py
- Кнопка «Удалить» в booking_detail.html
- Маршрут /admin/bookings/delete/<id> в web_demo.py
- Переводы
Запуск: python install_delete_booking.py
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"
I18N = BASE / "core" / "i18n"
WEB_DEMO = BASE / "web_demo.py"
SCHEDULE = BASE / "core" / "storage" / "schedule.py"


# ============================================
# 1. ФУНКЦИЯ delete_booking
# ============================================

DELETE_FUNCTION = '''

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
'''


# ============================================
# 2. ОБНОВЛЁННЫЙ booking_detail.html
# ============================================

BOOKING_DETAIL_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('booking_detail_title', admin_lang) }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: #075e54; color: white; }
        .header-top { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px 10px 40px; }
        .header-top h1 { font-size: 20px; }
        .header-nav { display: flex; gap: 20px; padding: 0 40px 14px 40px; }
        .header-nav a { color: white; text-decoration: none; font-size: 14px; opacity: 0.8; }
        .header-nav a:hover { opacity: 1; }
        .header-nav a.active { opacity: 1; font-weight: 600; border-bottom: 2px solid #25d366; padding-bottom: 2px; }
        .lang-switch { display: flex; gap: 5px; }
        .lang-btn { padding: 3px 8px; background: rgba(255,255,255,0.15); color: white; text-decoration: none; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .lang-btn.active { background: #25d366; }

        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .card h2 { color: #075e54; font-size: 20px; margin-bottom: 20px; }
        .info-grid { display: grid; grid-template-columns: 200px 1fr; gap: 16px; font-size: 15px; }
        .info-grid .label { color: #666; font-weight: 500; }
        .info-grid .value { color: #333; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600; }
        .status-pending { background: #fff3e0; color: #e65100; }
        .status-confirmed { background: #e8f5e9; color: #2e7d32; }
        .status-cancelled { background: #ffebee; color: #c62828; }
        .notes-box { background: #f9f9f9; border-left: 4px solid #25d366; padding: 16px 20px; border-radius: 8px; margin-top: 8px; color: #333; font-size: 15px; line-height: 1.6; white-space: pre-wrap; }
        .image-box { margin-top: 12px; }
        .image-box img { max-width: 100%; max-height: 500px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .actions { display: flex; gap: 12px; margin-top: 20px; flex-wrap: wrap; }
        .btn { padding: 12px 24px; border-radius: 8px; font-size: 15px; font-weight: 600; text-decoration: none; display: inline-block; border: none; cursor: pointer; transition: background 0.2s; }
        .btn-primary { background: #25d366; color: white; }
        .btn-primary:hover { background: #1ebe5d; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        .btn-danger { background: #ffebee; color: #c62828; }
        .btn-danger:hover { background: #ffcdd2; }
        .btn-delete { background: #c62828; color: white; }
        .btn-delete:hover { background: #b71c1c; }
        .divider { height: 1px; background: #eee; margin: 24px 0; }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="card">
            <h2>📋 {{ t('booking_detail_title', admin_lang) }} #{{ booking.id }}</h2>

            <div class="info-grid">
                <div class="label">{{ t('bookings_th_date', admin_lang) }}:</div>
                <div class="value"><b>{{ booking.date_human }}</b></div>

                <div class="label">{{ t('bookings_th_time', admin_lang) }}:</div>
                <div class="value">{{ booking.time }} · {{ booking.duration // 60 }}{{ t('booking_hours_short', admin_lang) }}</div>

                <div class="label">{{ t('bookings_th_client', admin_lang) }}:</div>
                <div class="value">{{ booking.lead_name }}</div>

                <div class="label">{{ t('bookings_th_phone', admin_lang) }}:</div>
                <div class="value">{{ booking.lead_phone }}</div>

                <div class="label">{{ t('bookings_th_size', admin_lang) }}:</div>
                <div class="value">{{ booking.service_name }}</div>

                <div class="label">{{ t('bookings_th_status', admin_lang) }}:</div>
                <div class="value">
                    {% if booking.status == 'pending' %}
                    <span class="status status-pending">{{ t('bookings_status_pending', admin_lang) }}</span>
                    {% elif booking.status == 'confirmed' %}
                    <span class="status status-confirmed">{{ t('bookings_status_confirmed', admin_lang) }}</span>
                    {% elif booking.status == 'cancelled' %}
                    <span class="status status-cancelled">{{ t('bookings_status_cancelled', admin_lang) }}</span>
                    {% endif %}
                </div>
            </div>

            {% if booking.notes %}
            <div style="margin-top: 24px;">
                <div class="label" style="color: #666; font-weight: 500; margin-bottom: 8px;">💬 {{ t('new_booking_notes', admin_lang) }}:</div>
                <div class="notes-box">{{ booking.notes }}</div>
            </div>
            {% endif %}

            {% if booking.reference_image %}
            <div style="margin-top: 24px;">
                <div class="label" style="color: #666; font-weight: 500; margin-bottom: 8px;">📎 {{ t('new_booking_image', admin_lang) }}:</div>
                <div class="image-box">
                    <a href="/admin/uploads/{{ booking.reference_image }}" target="_blank">
                        <img src="/admin/uploads/{{ booking.reference_image }}" alt="Sketch">
                    </a>
                </div>
            </div>
            {% endif %}

            <div class="divider"></div>

            <div class="actions">
                <a href="/admin/bookings" class="btn btn-secondary">← {{ t('bookings_back', admin_lang) }}</a>

                {% if booking.status == 'pending' %}
                <a href="/admin/bookings/confirm/{{ booking.id }}" class="btn btn-primary">✓ {{ t('bookings_btn_confirm', admin_lang) }}</a>
                {% endif %}

                {% if booking.status != 'cancelled' %}
                <a href="/admin/bookings/cancel/{{ booking.id }}" class="btn btn-danger">✕ {{ t('bookings_btn_cancel', admin_lang) }}</a>
                {% endif %}

                <a href="/admin/bookings/delete/{{ booking.id }}"
                   class="btn btn-delete"
                   onclick="return confirm('{{ t('booking_delete_confirm', admin_lang) }}')">
                    🗑 {{ t('booking_delete', admin_lang) }}
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""


# ============================================
# 3. ПЕРЕВОДЫ
# ============================================

I18N_NEW = {
    "ru": {
        "booking_delete": "Удалить запись",
        "booking_delete_confirm": "Точно удалить запись? Это действие нельзя отменить.",
    },
    "en": {
        "booking_delete": "Delete booking",
        "booking_delete_confirm": "Delete this booking? This action cannot be undone.",
    },
    "he": {
        "booking_delete": "מחק הזמנה",
        "booking_delete_confirm": "למחוק את ההזמנה? לא ניתן לבטל פעולה זו.",
    },
}


# ============================================
# 4. МАРШРУТ DELETE
# ============================================

ROUTE_DELETE = '''

@app.route('/admin/bookings/delete/<int:booking_id>')
def admin_booking_delete(booking_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    delete_booking(booking_id)
    return redirect('/admin/bookings')
'''


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_delete_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    if I18N.exists():
        shutil.copytree(I18N, backup_dir / "i18n", dirs_exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    if SCHEDULE.exists():
        shutil.copy(SCHEDULE, backup_dir / "schedule.py")
    print(f"📦 Бэкап: {backup_dir.name}")


def update_schedule():
    if not SCHEDULE.exists():
        print("⚠️  Нет schedule.py")
        return

    content = SCHEDULE.read_text(encoding='utf-8')

    if 'def delete_booking(' in content:
        print("⏭️  schedule.py: delete_booking уже есть")
        return

    content += DELETE_FUNCTION
    SCHEDULE.write_text(content, encoding='utf-8')
    print("✅ schedule.py: добавлена функция delete_booking")


def update_template():
    path = TEMPLATES / "booking_detail.html"
    path.write_text(BOOKING_DETAIL_HTML, encoding='utf-8')
    print("✅ Обновлён: templates/booking_detail.html")


def update_i18n():
    for lang, data in I18N_NEW.items():
        path = I18N / f"{lang}.json"
        if not path.exists():
            continue
        with open(path, encoding='utf-8') as f:
            existing = json.load(f)
        before = len(existing)
        existing.update(data)
        after = len(existing)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print(f"✅ {lang}.json: {before} → {after} ключей")


def update_web_demo():
    if not WEB_DEMO.exists():
        return

    content = WEB_DEMO.read_text(encoding='utf-8')

    # Импорт delete_booking
    if 'delete_booking' not in content:
        old = "    get_master, get_bookings, cancel_booking, confirm_booking,"
        new = "    get_master, get_bookings, cancel_booking, confirm_booking, delete_booking,"
        if old in content:
            content = content.replace(old, new)
            print("✅ web_demo.py: импорт delete_booking добавлен")
        else:
            # Пробуем другой вариант
            old2 = "get_master, get_bookings, cancel_booking, confirm_booking,\n    get_booking,"
            new2 = "get_master, get_bookings, cancel_booking, confirm_booking,\n    get_booking, delete_booking,"
            if old2 in content:
                content = content.replace(old2, new2)
                print("✅ web_demo.py: импорт delete_booking добавлен (вариант 2)")
            else:
                print("⚠️  web_demo.py: не найден блок импорта schedule")

    # Маршрут
    if '/admin/bookings/delete/' not in content:
        marker = "if __name__ == '__main__':"
        if marker in content:
            content = content.replace(marker, ROUTE_DELETE + "\n\n" + marker, 1)
            print("✅ web_demo.py: маршрут delete добавлен")

    WEB_DEMO.write_text(content, encoding='utf-8')


def main():
    print("=" * 60)
    print("🚀 Установка фичи: удаление записи")
    print("=" * 60)
    print()

    backup()
    print()

    print("🐍 schedule.py:")
    update_schedule()
    print()

    print("📄 Шаблон:")
    update_template()
    print()

    print("🌍 Переводы:")
    update_i18n()
    print()

    print("🐍 web_demo.py:")
    update_web_demo()
    print()

    print("=" * 60)
    print("✅ Готово!")
    print("=" * 60)
    print()
    print("Что делать:")
    print("1. Перезапустите web_demo.py")
    print("2. Откройте любую запись — увидите кнопку «🗑 Удалить»")
    print("3. При клике спросит подтверждение")
    print()


if __name__ == '__main__':
    main()
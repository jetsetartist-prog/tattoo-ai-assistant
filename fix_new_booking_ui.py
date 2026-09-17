"""
Исправления для формы new_booking и добавление страницы деталей записи.
Запуск: python fix_new_booking_ui.py
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"
I18N = BASE / "core" / "i18n"
WEB_DEMO = BASE / "web_demo.py"


# ============================================
# 1. ОБНОВЛЁННЫЙ new_booking.html
# ============================================

NEW_BOOKING_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('new_booking_title', admin_lang) }}</title>
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
        .lang-btn:hover { background: rgba(255,255,255,0.3); }
        .lang-btn.active { background: #25d366; }

        .container { max-width: 700px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card h2 { color: #075e54; font-size: 20px; margin-bottom: 8px; }
        .subtitle { color: #666; font-size: 14px; margin-bottom: 24px; }
        label { display: block; color: #333; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
        .required { color: #c00; }
        input[type="text"], input[type="tel"], input[type="date"], input[type="time"], select, textarea {
            width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 15px; outline: none; margin-bottom: 8px; font-family: inherit;
        }
        input:focus, select:focus, textarea:focus { border-color: #25d366; }
        textarea { resize: vertical; min-height: 80px; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .field { margin-bottom: 16px; }
        .field input, .field select, .field textarea { margin-bottom: 0; }
        .actions { margin-top: 24px; display: flex; gap: 12px; }
        .btn { padding: 14px 28px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-primary { background: #25d366; color: white; }
        .btn-primary:hover { background: #1ebe5d; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        .alert-error { background: #ffe5e5; color: #c00; padding: 14px 18px; border-radius: 8px; font-size: 14px; margin-bottom: 20px; border-left: 4px solid #c00; }
        .hint { display: block; font-size: 12px; color: #999; margin-top: 6px; margin-bottom: 16px; }
        .file-input-wrap {
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: border-color 0.2s;
            margin-bottom: 16px;
        }
        .file-input-wrap:hover { border-color: #25d366; }
        .file-input-wrap input[type="file"] { display: none; }
        .file-input-label {
            color: #666;
            font-size: 14px;
            cursor: pointer;
        }
        .file-preview {
            margin-top: 12px;
            display: none;
        }
        .file-preview img {
            max-width: 200px;
            max-height: 200px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
        }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="card">
            <h2>{{ t('new_booking_title', admin_lang) }}</h2>
            <p class="subtitle">{{ t('new_booking_subtitle', admin_lang) }}</p>

            {% if error %}
            <div class="alert-error">{{ error }}</div>
            {% endif %}

            <form method="POST" action="/admin/bookings/new" enctype="multipart/form-data">
                <div class="field">
                    <label>{{ t('new_booking_name', admin_lang) }} <span class="required">*</span></label>
                    <input type="text" name="name" value="{{ prefill_name or '' }}" required autofocus>
                </div>

                <div class="field">
                    <label>{{ t('new_booking_phone', admin_lang) }} <span class="required">*</span></label>
                    <input type="tel" name="phone" value="{{ prefill_phone or '' }}" required>
                </div>

                <div class="field">
                    <label>{{ t('new_booking_service', admin_lang) }} <span class="required">*</span></label>
                    <select name="service_id" required>
                        <option value="">{{ t('new_booking_select_service', admin_lang) }}</option>
                        {% for s in services %}
                        <option value="{{ s.id }}" {% if prefill_service_id == s.id %}selected{% endif %}>
                            {{ s.name }} — {{ s.duration_minutes // 60 }}ч — от {{ s.price_from }}₽
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <div class="row">
                    <div class="field">
                        <label>{{ t('new_booking_date', admin_lang) }} <span class="required">*</span></label>
                        <input type="date" name="date" value="{{ prefill_date or '' }}" required min="{{ today }}">
                    </div>
                    <div class="field">
                        <label>{{ t('new_booking_time', admin_lang) }} <span class="required">*</span></label>
                        <input type="time" name="time" value="{{ prefill_time or '' }}" required step="1800">
                        <span class="hint">{{ t('new_booking_time_hint', admin_lang) }}</span>
                    </div>
                </div>

                <div class="field">
                    <label>{{ t('new_booking_notes', admin_lang) }}</label>
                    <textarea name="notes" placeholder="{{ t('new_booking_notes_ph', admin_lang) }}">{{ prefill_notes or '' }}</textarea>
                </div>

                <div class="field">
                    <label>{{ t('new_booking_image', admin_lang) }}</label>
                    <label class="file-input-wrap" for="file_input">
                        <div class="file-input-label" id="file_label">📎 {{ t('new_booking_image_hint', admin_lang) }}</div>
                        <input type="file" id="file_input" name="reference_image" accept="image/*" onchange="previewFile(this)">
                    </label>
                    <div class="file-preview" id="file_preview">
                        <img id="preview_img" src="" alt="Preview">
                    </div>
                </div>

                <div class="actions">
                    <button type="submit" class="btn btn-primary">{{ t('new_booking_save', admin_lang) }}</button>
                    <a href="/admin/calendar" class="btn btn-secondary">{{ t('new_booking_cancel', admin_lang) }}</a>
                </div>
            </form>
        </div>
    </div>

    <script>
        function previewFile(input) {
            const preview = document.getElementById('file_preview');
            const img = document.getElementById('preview_img');
            const label = document.getElementById('file_label');

            if (input.files && input.files[0]) {
                const file = input.files[0];
                label.textContent = '📎 ' + file.name;

                const reader = new FileReader();
                reader.onload = function(e) {
                    img.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                label.textContent = '📎 {{ t("new_booking_image_hint", admin_lang) }}';
                preview.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""


# ============================================
# 2. booking_detail.html — страница деталей записи
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
        .info-grid {
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 16px;
            font-size: 15px;
        }
        .info-grid .label { color: #666; font-weight: 500; }
        .info-grid .value { color: #333; }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
        }
        .status-pending { background: #fff3e0; color: #e65100; }
        .status-confirmed { background: #e8f5e9; color: #2e7d32; }
        .status-cancelled { background: #ffebee; color: #c62828; }

        .notes-box {
            background: #f9f9f9;
            border-left: 4px solid #25d366;
            padding: 16px 20px;
            border-radius: 8px;
            margin-top: 8px;
            color: #333;
            font-size: 15px;
            line-height: 1.6;
            white-space: pre-wrap;
        }

        .image-box {
            margin-top: 12px;
        }
        .image-box img {
            max-width: 100%;
            max-height: 500px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .actions { display: flex; gap: 12px; margin-top: 20px; }
        .btn { padding: 12px 24px; border-radius: 8px; font-size: 15px; font-weight: 600; text-decoration: none; display: inline-block; border: none; cursor: pointer; }
        .btn-primary { background: #25d366; color: white; }
        .btn-primary:hover { background: #1ebe5d; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        .btn-danger { background: #ffebee; color: #c62828; }
        .btn-danger:hover { background: #ffcdd2; }
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

            <div class="actions">
                <a href="/admin/bookings" class="btn btn-secondary">← {{ t('bookings_back', admin_lang) }}</a>
                {% if booking.status == 'pending' %}
                <a href="/admin/bookings/confirm/{{ booking.id }}" class="btn btn-primary">✓ {{ t('bookings_btn_confirm', admin_lang) }}</a>
                {% endif %}
                {% if booking.status != 'cancelled' %}
                <a href="/admin/bookings/cancel/{{ booking.id }}" class="btn btn-danger">✕ {{ t('bookings_btn_cancel', admin_lang) }}</a>
                {% endif %}
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
        "booking_detail_title": "Запись",
        "booking_hours_short": "ч",
        "bookings_back": "Назад к записям",
        "bookings_click_hint": "Клик по записи — детали",
    },
    "en": {
        "booking_detail_title": "Booking",
        "booking_hours_short": "h",
        "bookings_back": "Back to bookings",
        "bookings_click_hint": "Click a booking for details",
    },
    "he": {
        "booking_detail_title": "הזמנה",
        "booking_hours_short": " ש'",
        "bookings_back": "חזרה להזמנות",
        "bookings_click_hint": "לחץ על הזמנה לפרטים",
    },
}


# ============================================
# 4. МАРШРУТ ДЕТАЛЕЙ ЗАПИСИ
# ============================================

ROUTE_DETAIL = '''

# ============================================
# ДЕТАЛИ ЗАПИСИ
# ============================================

@app.route('/admin/bookings/<int:booking_id>')
def admin_booking_detail(booking_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    booking = get_booking(booking_id)
    if not booking:
        return "Запись не найдена", 404

    # Обогащаем датой human
    try:
        dt = datetime.strptime(booking['date'], "%Y-%m-%d").date()
        weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        booking['date_human'] = f"{dt.strftime('%d.%m.%Y')} ({weekdays_ru[dt.weekday()]})"
    except Exception:
        booking['date_human'] = booking['date']

    return _render_template_file(
        'booking_detail.html',
        booking=booking,
        active='bookings',
    )
'''


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_fix_ui_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    if I18N.exists():
        shutil.copytree(I18N, backup_dir / "i18n", dirs_exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    print(f"📦 Бэкап: {backup_dir.name}")


def update_templates():
    (TEMPLATES / "new_booking.html").write_text(NEW_BOOKING_HTML, encoding='utf-8')
    print("✅ Обновлён: templates/new_booking.html")

    (TEMPLATES / "booking_detail.html").write_text(BOOKING_DETAIL_HTML, encoding='utf-8')
    print("✅ Создан: templates/booking_detail.html")


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

    # Импорт get_booking (если нет)
    if 'get_booking' not in content:
        old = "    get_master, get_bookings, cancel_booking, confirm_booking,"
        new = "    get_master, get_bookings, cancel_booking, confirm_booking,\n    get_booking,"
        if old in content:
            content = content.replace(old, new)
            print("✅ web_demo.py: импорт get_booking добавлен")

    # Маршрут деталей
    if '/admin/bookings/<int:booking_id>' not in content:
        marker = "if __name__ == '__main__':"
        if marker in content:
            content = content.replace(marker, ROUTE_DETAIL + "\n\n" + marker, 1)
            print("✅ web_demo.py: маршрут деталей добавлен")

    WEB_DEMO.write_text(content, encoding='utf-8')


def main():
    print("=" * 60)
    print("🚀 Исправление UI формы + детали записи")
    print("=" * 60)
    print()

    backup()
    print()

    print("📄 Шаблоны:")
    update_templates()
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
    print("2. Откройте /admin/bookings/new — проверьте форму")
    print("3. Откройте любую запись — увидите детали с фото")
    print()


if __name__ == '__main__':
    main()
"""
Установщик фичи "Новая запись" (new_booking).

Что делает:
1. Создаёт templates/new_booking.html
2. Добавляет 18 ключей в ru.json, en.json, he.json
3. Проверяет, что в schedule.py есть create_manual_booking, get_booking, update_booking
4. Добавляет маршруты /admin/bookings/new и /admin/uploads/<file> в web_demo.py
5. Добавляет импорты в web_demo.py

Запуск: python install_new_booking.py
Идемпотентный — можно запускать несколько раз.
"""
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"
I18N = BASE / "core" / "i18n"
WEB_DEMO = BASE / "web_demo.py"
SCHEDULE = BASE / "core" / "storage" / "schedule.py"


# ============================================
# 1. ШАБЛОН new_booking.html
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
            font-size: 15px; outline: none; margin-bottom: 16px; font-family: inherit;
        }
        input:focus, select:focus, textarea:focus { border-color: #25d366; }
        textarea { resize: vertical; min-height: 80px; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .actions { margin-top: 24px; display: flex; gap: 12px; }
        .btn { padding: 14px 28px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-primary { background: #25d366; color: white; }
        .btn-primary:hover { background: #1ebe5d; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        .alert-error { background: #ffe5e5; color: #c00; padding: 14px 18px; border-radius: 8px; font-size: 14px; margin-bottom: 20px; border-left: 4px solid #c00; }
        .hint { font-size: 12px; color: #999; margin-top: -12px; margin-bottom: 16px; }
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
                <label>{{ t('new_booking_name', admin_lang) }} <span class="required">*</span></label>
                <input type="text" name="name" value="{{ prefill_name or '' }}" required autofocus>

                <label>{{ t('new_booking_phone', admin_lang) }} <span class="required">*</span></label>
                <input type="tel" name="phone" value="{{ prefill_phone or '' }}" required>

                <label>{{ t('new_booking_service', admin_lang) }} <span class="required">*</span></label>
                <select name="service_id" required>
                    <option value="">{{ t('new_booking_select_service', admin_lang) }}</option>
                    {% for s in services %}
                    <option value="{{ s.id }}" {% if prefill_service_id == s.id %}selected{% endif %}>
                        {{ s.name }} — {{ s.duration_minutes // 60 }}ч — от {{ s.price_from }}₽
                    </option>
                    {% endfor %}
                </select>

                <div class="row">
                    <div>
                        <label>{{ t('new_booking_date', admin_lang) }} <span class="required">*</span></label>
                        <input type="date" name="date" value="{{ prefill_date or '' }}" required min="{{ today }}">
                    </div>
                    <div>
                        <label>{{ t('new_booking_time', admin_lang) }} <span class="required">*</span></label>
                        <input type="time" name="time" value="{{ prefill_time or '' }}" required step="1800">
                        <div class="hint">{{ t('new_booking_time_hint', admin_lang) }}</div>
                    </div>
                </div>

                <label>{{ t('new_booking_notes', admin_lang) }}</label>
                <textarea name="notes" placeholder="{{ t('new_booking_notes_ph', admin_lang) }}">{{ prefill_notes or '' }}</textarea>

                <label>{{ t('new_booking_image', admin_lang) }}</label>
                <input type="file" name="reference_image" accept="image/*">
                <div class="hint">{{ t('new_booking_image_hint', admin_lang) }}</div>

                <div class="actions">
                    <button type="submit" class="btn btn-primary">{{ t('new_booking_save', admin_lang) }}</button>
                    <a href="/admin/calendar" class="btn btn-secondary">{{ t('new_booking_cancel', admin_lang) }}</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""


# ============================================
# 2. ПЕРЕВОДЫ
# ============================================

I18N_RU = {
    "new_booking_title": "➕ Новая запись",
    "new_booking_subtitle": "Заполните данные клиента",
    "new_booking_name": "Имя клиента",
    "new_booking_phone": "Телефон",
    "new_booking_service": "Услуга",
    "new_booking_select_service": "— Выберите услугу —",
    "new_booking_date": "Дата",
    "new_booking_time": "Время",
    "new_booking_time_hint": "Шаг 30 минут",
    "new_booking_notes": "Комментарий",
    "new_booking_notes_ph": "Например: реализм, чб, на плече",
    "new_booking_image": "Эскиз / референс",
    "new_booking_image_hint": "JPG, PNG, до 5 МБ",
    "new_booking_save": "💾 Сохранить запись",
    "new_booking_cancel": "← Отмена",
    "new_booking_btn": "➕ Новая запись",
    "new_booking_success": "✅ Запись создана",
    "new_booking_error_slot": "Этот слот занят. Выберите другое время.",
    "new_booking_error_required": "Заполните обязательные поля",
}

I18N_EN = {
    "new_booking_title": "➕ New booking",
    "new_booking_subtitle": "Fill in client details",
    "new_booking_name": "Client name",
    "new_booking_phone": "Phone",
    "new_booking_service": "Service",
    "new_booking_select_service": "— Choose service —",
    "new_booking_date": "Date",
    "new_booking_time": "Time",
    "new_booking_time_hint": "30-minute step",
    "new_booking_notes": "Notes",
    "new_booking_notes_ph": "E.g.: realism, b&w, on shoulder",
    "new_booking_image": "Sketch / reference",
    "new_booking_image_hint": "JPG, PNG, up to 5 MB",
    "new_booking_save": "💾 Save booking",
    "new_booking_cancel": "← Cancel",
    "new_booking_btn": "➕ New booking",
    "new_booking_success": "✅ Booking created",
    "new_booking_error_slot": "This slot is busy. Choose another time.",
    "new_booking_error_required": "Fill in required fields",
}

I18N_HE = {
    "new_booking_title": "➕ הזמנה חדשה",
    "new_booking_subtitle": "מלא את פרטי הלקוח",
    "new_booking_name": "שם הלקוח",
    "new_booking_phone": "טלפון",
    "new_booking_service": "שירות",
    "new_booking_select_service": "— בחר שירות —",
    "new_booking_date": "תאריך",
    "new_booking_time": "שעה",
    "new_booking_time_hint": "בצעדים של 30 דקות",
    "new_booking_notes": "הערות",
    "new_booking_notes_ph": "לדוגמה: ריאליזם, שחור-לבן",
    "new_booking_image": "סקיצה / רפרנס",
    "new_booking_image_hint": "JPG, PNG, עד 5 MB",
    "new_booking_save": "💾 שמור הזמנה",
    "new_booking_cancel": "← ביטול",
    "new_booking_btn": "➕ הזמנה חדשה",
    "new_booking_success": "✅ ההזמנה נוצרה",
    "new_booking_error_slot": "המשבצת תפוסה. בחר שעה אחרת.",
    "new_booking_error_required": "מלא שדות חובה",
}


# ============================================
# 3. МАРШРУТЫ
# ============================================

ROUTE_NEW_BOOKING = '''

# ============================================
# НОВАЯ ЗАПИСЬ (вручную)
# ============================================

import uuid
from werkzeug.utils import secure_filename
from flask import send_from_directory

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin/uploads/<filename>')
def admin_upload(filename):
    """Отдаёт загруженный файл."""
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/admin/bookings/new', methods=['GET', 'POST'])
def admin_new_booking():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    master = get_default_master()
    if not master:
        return "Мастер не найден", 500

    services = get_all_services()

    # Prefill из query
    prefill_date = request.args.get('date', '')
    prefill_time = request.args.get('time', '')

    if request.method == 'GET':
        return _render_template_file(
            'new_booking.html',
            services=services,
            error=None,
            prefill_date=prefill_date,
            prefill_time=prefill_time,
            prefill_name='',
            prefill_phone='',
            prefill_service_id=None,
            prefill_notes='',
            today=datetime.now().date().isoformat(),
            active='calendar',
        )

    # POST
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    service_id = request.form.get('service_id', '').strip()
    date_str = request.form.get('date', '').strip()
    time_str = request.form.get('time', '').strip()
    notes = request.form.get('notes', '').strip()

    error = None

    if not name or not phone or not service_id or not date_str or not time_str:
        error = 'Заполните обязательные поля'

    service = get_service(int(service_id)) if service_id else None
    if not service:
        error = 'Услуга не найдена'

    if not error:
        duration = service['duration_minutes']

        # Проверяем, что слот свободен
        free = get_free_slots(master['id'], date_str, duration)
        if time_str not in free:
            error = 'Этот слот занят. Выберите другое время.'

    if error:
        return _render_template_file(
            'new_booking.html',
            services=services,
            error=error,
            prefill_date=date_str,
            prefill_time=time_str,
            prefill_name=name,
            prefill_phone=phone,
            prefill_service_id=int(service_id) if service_id else None,
            prefill_notes=notes,
            today=datetime.now().date().isoformat(),
            active='calendar',
        ), 400

    # Загрузка файла
    reference_image = ''
    if 'reference_image' in request.files:
        file = request.files['reference_image']
        if file and file.filename and allowed_file(file.filename):
            # Проверяем размер
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)

            if size <= MAX_FILE_SIZE:
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"booking_{uuid.uuid4().hex[:12]}.{ext}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                reference_image = filename

    # Создаём запись
    booking_id = create_manual_booking(
        master_id=master['id'],
        date_str=date_str,
        time_str=time_str,
        duration=service['duration_minutes'],
        name=name,
        phone=phone,
        service_id=service['id'],
        notes=notes,
        reference_image=reference_image,
    )

    if not booking_id:
        return _render_template_file(
            'new_booking.html',
            services=services,
            error='Не удалось создать запись',
            prefill_date=date_str,
            prefill_time=time_str,
            prefill_name=name,
            prefill_phone=phone,
            prefill_service_id=int(service_id) if service_id else None,
            prefill_notes=notes,
            today=datetime.now().date().isoformat(),
            active='calendar',
        ), 500

    return redirect('/admin/bookings')
'''


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_install_nb_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    if I18N.exists():
        shutil.copytree(I18N, backup_dir / "i18n", dirs_exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")

    print(f"📦 Бэкап: {backup_dir.name}")
    return backup_dir


def create_template():
    path = TEMPLATES / "new_booking.html"
    if path.exists():
        print(f"⏭️  Уже существует: {path.name}")
        return
    path.write_text(NEW_BOOKING_HTML, encoding='utf-8')
    print(f"✅ Создан: templates/new_booking.html")


def update_i18n():
    for lang, data in [('ru', I18N_RU), ('en', I18N_EN), ('he', I18N_HE)]:
        path = I18N / f"{lang}.json"
        if not path.exists():
            print(f"⚠️  Нет файла: {lang}.json")
            continue

        with open(path, encoding='utf-8') as f:
            existing = json.load(f)

        before = len(existing)
        existing.update(data)
        after = len(existing)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        print(f"✅ {lang}.json: {before} → {after} ключей")


def check_schedule():
    """Проверяет, что в schedule.py есть нужные функции."""
    if not SCHEDULE.exists():
        print(f"❌ Нет файла: schedule.py")
        return False

    content = SCHEDULE.read_text(encoding='utf-8')
    required = ['create_manual_booking', 'get_booking', 'update_booking']

    for fn in required:
        if f"def {fn}(" not in content:
            print(f"⚠️  В schedule.py нет функции: {fn}")
            return False

    print(f"✅ schedule.py: все функции на месте")
    return True


def update_web_demo():
    """Добавляет импорты и маршруты в web_demo.py."""
    if not WEB_DEMO.exists():
        print(f"❌ Нет файла: web_demo.py")
        return

    content = WEB_DEMO.read_text(encoding='utf-8')

    # 1. Импорты
    if 'create_manual_booking' not in content:
        old_import = """from core.storage.schedule import (
    get_default_master, get_all_work_hours, set_work_hours,
    get_master_by_email, set_master_password, has_password,
    get_master, get_bookings, cancel_booking, confirm_booking,
)"""
        new_import = """from core.storage.schedule import (
    get_default_master, get_all_work_hours, set_work_hours,
    get_master_by_email, set_master_password, has_password,
    get_master, get_bookings, cancel_booking, confirm_booking,
    create_manual_booking, get_booking, update_booking,
    get_free_slots, get_all_services, get_service,
)"""

        if old_import in content:
            content = content.replace(old_import, new_import)
            print("✅ web_demo.py: импорты обновлены")
        else:
            print("⚠️  web_demo.py: не найден блок импортов schedule")
    else:
        print("⏭️  web_demo.py: импорты уже есть")

    # 2. Маршруты
    if '/admin/bookings/new' not in content:
        marker = "if __name__ == '__main__':"
        if marker in content:
            content = content.replace(marker, ROUTE_NEW_BOOKING + "\n\n" + marker, 1)
            print("✅ web_demo.py: маршруты добавлены")
        else:
            print("⚠️  web_demo.py: не найден if __name__")
    else:
        print("⏭️  web_demo.py: маршруты уже есть")

    WEB_DEMO.write_text(content, encoding='utf-8')


def main():
    print("=" * 60)
    print("🚀 Установка фичи: Новая запись (new_booking)")
    print("=" * 60)
    print()

    backup()
    print()

    print("📄 Шаблон:")
    create_template()
    print()

    print("🌍 Переводы:")
    update_i18n()
    print()

    print("🔍 Проверка schedule.py:")
    check_schedule()
    print()

    print("🐍 Обновление web_demo.py:")
    update_web_demo()
    print()

    print("=" * 60)
    print("✅ Готово!")
    print("=" * 60)
    print()
    print("Что делать:")
    print("1. Перезапустите web_demo.py: python web_demo.py")
    print("2. Откройте: http://localhost:5000/admin/bookings/new")
    print("3. Или: в календаре кликните по свободному слоту")
    print()


if __name__ == '__main__':
    main()
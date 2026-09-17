"""
ЭТАП 1: Связка формы записи с клиентами + поля цены + источник.

Что делает:
1. БД: поле source в bookings
2. schedule.py: create_manual_booking принимает client_id, price, deposit, source
3. new_booking.html: поля «Стоимость» и «Предоплата»
4. web_demo.py: создание клиента + маршрут редактирования цены
5. booking_detail.html: форма редактирования цены + источник
6. bookings.html: колонка «Источник»
7. Переводы

Запуск: python install_stage1_client_link.py
"""
import json
import shutil
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"
I18N = BASE / "core" / "i18n"
WEB_DEMO = BASE / "web_demo.py"
SCHEDULE = BASE / "core" / "storage" / "schedule.py"
SQLITE_PATH = os.getenv("SQLITE_PATH", "data/leads.db")


# ============================================
# 1. БД
# ============================================

def update_db():
    print("📊 БД:")
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE bookings ADD COLUMN source TEXT DEFAULT 'manual'")
        print("  ✅ bookings.source")
    except sqlite3.OperationalError:
        print("  ⏭️  bookings.source уже есть")

    conn.commit()
    conn.close()
    print()


# ============================================
# 2. schedule.py — create_manual_booking
# ============================================

OLD_FUNC = '''def create_manual_booking(
    master_id: int,
    date_str: str,
    time_str: str,
    duration: int,
    name: str,
    phone: str,
    service_id: int = None,
    notes: str = "",
    reference_image: str = "",
) -> Optional[int]:
    """
    Создаёт запись вручную (от мастера).
    Возвращает ID записи или None, если слот занят.
    """
    free = get_free_slots(master_id, date_str, duration)
    if time_str not in free:
        logger.warning(f"[Schedule] Слот {date_str} {time_str} уже занят")
        return None

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads (platform, user_id, name, phone, style, size, date_preference)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("manual", "master", name, phone, "", "", f"{date_str} {time_str}"))
    lead_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO bookings
            (master_id, lead_id, service_id, date, time, duration, status, notes, reference_image)
        VALUES (?, ?, ?, ?, ?, ?, 'confirmed', ?, ?)
    """, (master_id, lead_id, service_id, date_str, time_str, duration, notes, reference_image))
    booking_id = cursor.lastrowid

    conn.commit()
    conn.close()

    logger.info(f"[Schedule] Создана ручная запись: {date_str} {time_str} (id={booking_id})")
    return booking_id'''

NEW_FUNC = '''def create_manual_booking(
    master_id: int,
    date_str: str,
    time_str: str,
    duration: int,
    name: str,
    phone: str,
    service_id: int = None,
    notes: str = "",
    reference_image: str = "",
    client_id: int = None,
    price: int = 0,
    deposit: int = 0,
    source: str = "manual",
) -> Optional[int]:
    """
    Создаёт запись вручную (от мастера или из бота).
    Возвращает ID записи или None, если слот занят.
    """
    free = get_free_slots(master_id, date_str, duration)
    if time_str not in free:
        logger.warning(f"[Schedule] Слот {date_str} {time_str} уже занят")
        return None

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads (platform, user_id, name, phone, style, size, date_preference)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (source, "auto", name, phone, "", "", f"{date_str} {time_str}"))
    lead_id = cursor.lastrowid

    status = 'confirmed' if source == 'manual' else 'pending'

    cursor.execute("""
        INSERT INTO bookings
            (master_id, lead_id, service_id, date, time, duration, status, notes, reference_image, client_id, price, deposit, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (master_id, lead_id, service_id, date_str, time_str, duration, status, notes, reference_image, client_id, price, deposit, source))
    booking_id = cursor.lastrowid

    conn.commit()
    conn.close()

    logger.info(f"[Schedule] Создана запись ({source}): {date_str} {time_str} (id={booking_id})")
    return booking_id'''

# Также добавим update_booking для обновления цены
UPDATE_FUNC = '''

def update_booking_price(booking_id: int, price: int = None, deposit: int = None):
    """Обновляет стоимость и предоплату записи."""
    updates = []
    params = []

    if price is not None:
        updates.append("price = ?")
        params.append(price)
    if deposit is not None:
        updates.append("deposit = ?")
        params.append(deposit)

    if not updates:
        return

    params.append(booking_id)
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE bookings SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    logger.info(f"[Schedule] Обновлена цена записи id={booking_id}: price={price}, deposit={deposit}")
'''


# ============================================
# 3. new_booking.html — поля цены
# ============================================

OLD_HTML_PART = '''                <div class="field">
                    <label>{{ t('new_booking_image', admin_lang) }}</label>
                    <label class="file-input-wrap" for="file_input">
                        <div class="file-input-label" id="file_label">📎 {{ t('new_booking_image_hint', admin_lang) }}</div>
                        <input type="file" id="file_input" name="reference_image" accept="image/*" onchange="previewFile(this)">
                    </label>
                    <div class="file-preview" id="file_preview">
                        <img id="preview_img" src="" alt="Preview">
                    </div>
                </div>'''

NEW_HTML_PART = '''                <div class="field">
                    <label>{{ t('new_booking_image', admin_lang) }}</label>
                    <label class="file-input-wrap" for="file_input">
                        <div class="file-input-label" id="file_label">📎 {{ t('new_booking_image_hint', admin_lang) }}</div>
                        <input type="file" id="file_input" name="reference_image" accept="image/*" onchange="previewFile(this)">
                    </label>
                    <div class="file-preview" id="file_preview">
                        <img id="preview_img" src="" alt="Preview">
                    </div>
                </div>

                <div class="row">
                    <div class="field">
                        <label>{{ t('new_booking_price', admin_lang) }} ({{ currency_symbol }})</label>
                        <input type="number" name="price" min="0" value="{{ prefill_price or 0 }}">
                    </div>
                    <div class="field">
                        <label>{{ t('new_booking_deposit', admin_lang) }} ({{ currency_symbol }})</label>
                        <input type="number" name="deposit" min="0" value="{{ prefill_deposit or 0 }}">
                    </div>
                </div>'''


# ============================================
# 4. web_demo.py — создание клиента + маршрут
# ============================================

OLD_READ = '''    notes = request.form.get('notes', '').strip()

    error = None'''

NEW_READ = '''    notes = request.form.get('notes', '').strip()
    price = int(request.form.get('price', 0) or 0)
    deposit = int(request.form.get('deposit', 0) or 0)

    error = None'''

OLD_CREATE = '''    # Создаём запись
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
    )'''

NEW_CREATE = '''    # Получаем или создаём клиента
    from core.storage.clients import get_or_create_client
    client_id = get_or_create_client(name, phone)

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
        client_id=client_id,
        price=price,
        deposit=deposit,
        source='manual',
    )'''

ROUTE_PRICE = '''

@app.route('/admin/bookings/edit/<int:booking_id>', methods=['POST'])
def admin_booking_edit_price(booking_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    price = int(request.form.get('price', 0) or 0)
    deposit = int(request.form.get('deposit', 0) or 0)

    update_booking_price(booking_id, price=price, deposit=deposit)
    return redirect(f'/admin/bookings/{booking_id}')
'''


# ============================================
# 5. booking_detail.html — форма цены + источник
# ============================================

# Заменим блок после статуса — добавим источник
OLD_DETAIL_STATUS = '''                <div class="label">{{ t('bookings_th_status', admin_lang) }}:</div>
                <div class="value">
                    {% if booking.status == 'pending' %}
                    <span class="status status-pending">{{ t('bookings_status_pending', admin_lang) }}</span>
                    {% elif booking.status == 'confirmed' %}
                    <span class="status status-confirmed">{{ t('bookings_status_confirmed', admin_lang) }}</span>
                    {% elif booking.status == 'cancelled' %}
                    <span class="status status-cancelled">{{ t('bookings_status_cancelled', admin_lang) }}</span>
                    {% endif %}
                </div>
            </div>'''

NEW_DETAIL_STATUS = '''                <div class="label">{{ t('bookings_th_status', admin_lang) }}:</div>
                <div class="value">
                    {% if booking.status == 'pending' %}
                    <span class="status status-pending">{{ t('bookings_status_pending', admin_lang) }}</span>
                    {% elif booking.status == 'confirmed' %}
                    <span class="status status-confirmed">{{ t('bookings_status_confirmed', admin_lang) }}</span>
                    {% elif booking.status == 'cancelled' %}
                    <span class="status status-cancelled">{{ t('bookings_status_cancelled', admin_lang) }}</span>
                    {% endif %}
                </div>

                <div class="label">{{ t('booking_source', admin_lang) }}:</div>
                <div class="value">
                    {% if booking.source == 'online' %}
                    <span class="status status-pending">🌐 {{ t('booking_source_online', admin_lang) }}</span>
                    {% else %}
                    <span class="status status-confirmed">✋ {{ t('booking_source_manual', admin_lang) }}</span>
                    {% endif %}
                </div>
            </div>'''

# Добавим блок оплаты перед divider
OLD_DIVIDER = '''            <div class="divider"></div>

            <div class="actions">'''

NEW_PAYMENT_BLOCK = '''            <div class="divider"></div>

            <div style="margin-bottom: 24px;">
                <h3 style="color: #075e54; font-size: 16px; margin-bottom: 16px;">💰 {{ t('booking_payment', admin_lang) }}</h3>

                <form method="POST" action="/admin/bookings/edit/{{ booking.id }}">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label style="display: block; color: #666; font-size: 13px; margin-bottom: 6px;">{{ t('booking_price', admin_lang) }} ({{ currency_symbol }})</label>
                            <input type="number" name="price" min="0" value="{{ booking.price or 0 }}" style="width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px;">
                        </div>
                        <div>
                            <label style="display: block; color: #666; font-size: 13px; margin-bottom: 6px;">{{ t('booking_deposit', admin_lang) }} ({{ currency_symbol }})</label>
                            <input type="number" name="deposit" min="0" value="{{ booking.deposit or 0 }}" style="width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px;">
                        </div>
                    </div>

                    {% if booking.price %}
                    <div style="margin-top: 16px; padding: 12px 16px; background: #f9f9f9; border-radius: 8px; font-size: 14px;">
                        <b>{{ t('booking_remaining', admin_lang) }}:</b> {{ (booking.price or 0) - (booking.deposit or 0) }} {{ currency_symbol }}
                    </div>
                    {% endif %}

                    <button type="submit" style="margin-top: 16px; padding: 10px 20px; background: #25d366; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;">💾 {{ t('booking_save_payment', admin_lang) }}</button>
                </form>
            </div>

            <div class="divider"></div>

            <div class="actions">'''


# ============================================
# 6. bookings.html — колонка источник
# ============================================

OLD_BOOKINGS_HEADER = '''                        <th>{{ t('bookings_th_status', admin_lang) }}</th>
                        <th>{{ t('bookings_th_actions', admin_lang) }}</th>'''

NEW_BOOKINGS_HEADER = '''                        <th>{{ t('bookings_th_status', admin_lang) }}</th>
                        <th>{{ t('booking_source', admin_lang) }}</th>
                        <th>{{ t('bookings_th_actions', admin_lang) }}</th>'''


# ============================================
# 7. ПЕРЕВОДЫ
# ============================================

I18N_RU = {
    "new_booking_price": "Стоимость",
    "new_booking_deposit": "Предоплата",
    "booking_payment": "Оплата",
    "booking_price": "Стоимость",
    "booking_deposit": "Предоплата",
    "booking_remaining": "Остаток",
    "booking_save_payment": "Сохранить оплату",
    "booking_source": "Источник",
    "booking_source_online": "Онлайн",
    "booking_source_manual": "Вручную",
}

I18N_EN = {
    "new_booking_price": "Price",
    "new_booking_deposit": "Deposit",
    "booking_payment": "Payment",
    "booking_price": "Price",
    "booking_deposit": "Deposit",
    "booking_remaining": "Remaining",
    "booking_save_payment": "Save payment",
    "booking_source": "Source",
    "booking_source_online": "Online",
    "booking_source_manual": "Manual",
}

I18N_HE = {
    "new_booking_price": "מחיר",
    "new_booking_deposit": "מקדמה",
    "booking_payment": "תשלום",
    "booking_price": "מחיר",
    "booking_deposit": "מקדמה",
    "booking_remaining": "יתרה",
    "booking_save_payment": "שמור תשלום",
    "booking_source": "מקור",
    "booking_source_online": "אונליין",
    "booking_source_manual": "ידני",
}


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_stage1_{timestamp}"
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
    print()


def update_schedule():
    if not SCHEDULE.exists():
        return
    content = SCHEDULE.read_text(encoding='utf-8')

    if OLD_FUNC in content:
        content = content.replace(OLD_FUNC, NEW_FUNC)
        print("  ✅ schedule.py: create_manual_booking обновлена")
    else:
        print("  ⏭️  schedule.py: старая create_manual_booking не найдена")

    if 'def update_booking_price' not in content:
        content += UPDATE_FUNC
        print("  ✅ schedule.py: update_booking_price добавлена")

    SCHEDULE.write_text(content, encoding='utf-8')


def update_new_booking():
    path = TEMPLATES / "new_booking.html"
    if not path.exists():
        return
    content = path.read_text(encoding='utf-8')
    if OLD_HTML_PART in content:
        content = content.replace(OLD_HTML_PART, NEW_HTML_PART)
        path.write_text(content, encoding='utf-8')
        print("  ✅ new_booking.html: поля цены добавлены")
    else:
        print("  ⏭️  new_booking.html: блок не найден")


def update_detail():
    path = TEMPLATES / "booking_detail.html"
    if not path.exists():
        return
    content = path.read_text(encoding='utf-8')

    if OLD_DETAIL_STATUS in content:
        content = content.replace(OLD_DETAIL_STATUS, NEW_DETAIL_STATUS)
        print("  ✅ booking_detail.html: источник добавлен")

    if OLD_DIVIDER in content and 'booking_payment' not in content:
        content = content.replace(OLD_DIVIDER, NEW_PAYMENT_BLOCK)
        print("  ✅ booking_detail.html: форма оплаты добавлена")

    path.write_text(content, encoding='utf-8')


def update_bookings():
    path = TEMPLATES / "bookings.html"
    if not path.exists():
        return
    content = path.read_text(encoding='utf-8')
    if OLD_BOOKINGS_HEADER in content and 'booking_source' not in content:
        content = content.replace(OLD_BOOKINGS_HEADER, NEW_BOOKINGS_HEADER)
        path.write_text(content, encoding='utf-8')
        print("  ✅ bookings.html: колонка источника добавлена")


def update_web_demo():
    if not WEB_DEMO.exists():
        return
    content = WEB_DEMO.read_text(encoding='utf-8')

    if OLD_READ in content:
        content = content.replace(OLD_READ, NEW_READ)
        print("  ✅ web_demo.py: чтение price/deposit")

    if OLD_CREATE in content:
        content = content.replace(OLD_CREATE, NEW_CREATE)
        print("  ✅ web_demo.py: создание клиента")

    # Импорт update_booking_price
    if 'update_booking_price' not in content:
        old_import = "    get_master, get_bookings, cancel_booking, confirm_booking,"
        new_import = "    get_master, get_bookings, cancel_booking, confirm_booking, update_booking_price,"
        if old_import in content:
            content = content.replace(old_import, new_import)
            print("  ✅ web_demo.py: импорт update_booking_price")

    # Маршрут
    if '/admin/bookings/edit/' not in content:
        marker = "if __name__ == '__main__':"
        if marker in content:
            content = content.replace(marker, ROUTE_PRICE + "\n\n" + marker, 1)
            print("  ✅ web_demo.py: маршрут редактирования цены")

    WEB_DEMO.write_text(content, encoding='utf-8')


def update_i18n():
    for lang, data in [('ru', I18N_RU), ('en', I18N_EN), ('he', I18N_HE)]:
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
        print(f"  ✅ {lang}.json: {before} → {after}")


def main():
    print("=" * 60)
    print("🚀 ЭТАП 1: Связка клиента + оплата + источник")
    print("=" * 60)
    print()

    backup()
    update_db()

    print("🐍 schedule.py:")
    update_schedule()
    print()

    print("📄 new_booking.html:")
    update_new_booking()
    print()

    print("📄 booking_detail.html:")
    update_detail()
    print()

    print("📄 bookings.html:")
    update_bookings()
    print()

    print("🐍 web_demo.py:")
    update_web_demo()
    print()

    print("🌍 Переводы:")
    update_i18n()
    print()

    print("=" * 60)
    print("✅ ЭТАП 1 ГОТОВ")
    print("=" * 60)
    print()
    print("Перезапустите web_demo.py и проверьте:")
    print("  1. /admin/bookings/new — поля «Стоимость» и «Предоплата»")
    print("  2. Создайте запись → клиент появится в /admin/clients")
    print("  3. Откройте детали записи → форма оплаты")
    print()


if __name__ == '__main__':
    main()
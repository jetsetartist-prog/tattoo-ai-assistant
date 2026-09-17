"""
Часть 3: Маршруты + переводы + меню.
- Маршруты /admin/clients, /admin/clients/<id>, /admin/clients/edit/<id>
- Маршруты /admin/services, /admin/services/new, /admin/services/edit/<id>, /admin/services/delete/<id>
- Переводы (~50 ключей)
- Обновление _nav.html (добавить «Клиенты» и «Услуги»)
- Обновление _render_template_file — передача currency

Запуск: python install_crm_part3.py
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
# 1. МАРШРУТЫ
# ============================================

ROUTES = '''

# ============================================
# КЛИЕНТЫ
# ============================================

@app.route('/admin/clients')
def admin_clients():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    search = request.args.get('q', '').strip()
    clients = get_all_clients(search=search)

    return _render_template_file(
        'clients.html',
        clients=clients,
        search=search,
        active='clients',
    )


@app.route('/admin/clients/<int:client_id>')
def admin_client_detail(client_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    client = get_client(client_id)
    if not client:
        return "Клиент не найден", 404

    stats = get_client_stats(client_id)
    bookings = get_client_bookings(client_id)

    return _render_template_file(
        'client_detail.html',
        client=client,
        stats=stats,
        bookings=bookings,
        active='clients',
    )


@app.route('/admin/clients/edit/<int:client_id>', methods=['GET', 'POST'])
def admin_client_edit(client_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    client = get_client(client_id)
    if not client:
        return "Клиент не найден", 404

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        notes = request.form.get('notes', '').strip()

        update_client(
            client_id,
            name=name if name else None,
            phone=phone if phone else None,
            email=email if email else None,
            notes=notes if notes else None,
        )
        return redirect(f'/admin/clients/{client_id}')

    return _render_template_file(
        'client_edit.html',
        client=client,
        active='clients',
    )


# ============================================
# УСЛУГИ
# ============================================

@app.route('/admin/services')
def admin_services():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    services = get_all_services()

    return _render_template_file(
        'services.html',
        services=services,
        active='services',
    )


@app.route('/admin/services/new', methods=['GET', 'POST'])
def admin_service_new():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    error = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        hours = int(request.form.get('hours', 0) or 0)
        minutes = int(request.form.get('minutes', 0) or 0)
        price_from = int(request.form.get('price_from', 0) or 0)
        buffer_minutes = int(request.form.get('buffer_minutes', 30) or 30)

        duration_minutes = hours * 60 + minutes

        if not name:
            error = 'Введите название услуги'
        elif duration_minutes <= 0:
            error = 'Длительность должна быть больше 0'
        else:
            create_service(name, duration_minutes, price_from, buffer_minutes)
            return redirect('/admin/services')

    return _render_template_file(
        'service_edit.html',
        service=None,
        error=error,
        active='services',
    )


@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
def admin_service_edit(service_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    service = get_service(service_id)
    if not service:
        return "Услуга не найдена", 404

    error = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        hours = int(request.form.get('hours', 0) or 0)
        minutes = int(request.form.get('minutes', 0) or 0)
        price_from = int(request.form.get('price_from', 0) or 0)
        buffer_minutes = int(request.form.get('buffer_minutes', 30) or 30)

        duration_minutes = hours * 60 + minutes

        if not name:
            error = 'Введите название услуги'
        elif duration_minutes <= 0:
            error = 'Длительность должна быть больше 0'
        else:
            update_service(
                service_id,
                name=name,
                duration_minutes=duration_minutes,
                price_from=price_from,
                buffer_minutes=buffer_minutes,
            )
            return redirect('/admin/services')

    return _render_template_file(
        'service_edit.html',
        service=service,
        error=error,
        active='services',
    )


@app.route('/admin/services/delete/<int:service_id>')
def admin_service_delete(service_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    delete_service(service_id)
    return redirect('/admin/services')
'''


# ============================================
# 2. ПЕРЕВОДЫ
# ============================================

I18N_RU = {
    "nav_clients": "Клиенты",
    "nav_services": "Услуги",

    "clients_title": "Клиенты",
    "clients_search": "Поиск по имени или телефону...",
    "clients_empty": "Клиентов пока нет",
    "clients_th_name": "Имя",
    "clients_th_phone": "Телефон",
    "clients_th_email": "Email",
    "clients_th_created": "Создан",
    "clients_notes": "Заметки",
    "clients_back": "Назад к клиентам",
    "clients_edit": "Редактировать",
    "client_edit_title": "Редактирование клиента",
    "client_notes_ph": "Аллергии, предпочтения, особенности",
    "client_save": "Сохранить",
    "client_cancel": "Отмена",
    "client_bookings_history": "История визитов",
    "client_bookings_empty": "Визитов пока нет",
    "client_stat_total": "Всего записей",
    "client_stat_confirmed": "Подтверждено",
    "client_stat_revenue": "Сумма",
    "client_stat_avg": "Средний чек",

    "services_title": "Услуги",
    "services_new": "Новая услуга",
    "services_empty": "Услуг пока нет",
    "services_th_name": "Название",
    "services_th_duration": "Длительность",
    "services_th_price": "Стоимость от",
    "services_th_buffer": "Перерыв",
    "services_delete_confirm": "Удалить услугу?",
    "service_edit_title": "Услуга",
    "service_hours": "Часов",
    "service_minutes": "Минут",
    "service_duration_hint": "Например: 1 час 30 минут",
    "service_buffer_hint": "Время между сеансами (на уборку, отдых)",
    "service_save": "Сохранить",
    "service_cancel": "Отмена",
}

I18N_EN = {
    "nav_clients": "Clients",
    "nav_services": "Services",

    "clients_title": "Clients",
    "clients_search": "Search by name or phone...",
    "clients_empty": "No clients yet",
    "clients_th_name": "Name",
    "clients_th_phone": "Phone",
    "clients_th_email": "Email",
    "clients_th_created": "Created",
    "clients_notes": "Notes",
    "clients_back": "Back to clients",
    "clients_edit": "Edit",
    "client_edit_title": "Edit client",
    "client_notes_ph": "Allergies, preferences, features",
    "client_save": "Save",
    "client_cancel": "Cancel",
    "client_bookings_history": "Visit history",
    "client_bookings_empty": "No visits yet",
    "client_stat_total": "Total bookings",
    "client_stat_confirmed": "Confirmed",
    "client_stat_revenue": "Revenue",
    "client_stat_avg": "Average check",

    "services_title": "Services",
    "services_new": "New service",
    "services_empty": "No services yet",
    "services_th_name": "Name",
    "services_th_duration": "Duration",
    "services_th_price": "Price from",
    "services_th_buffer": "Buffer",
    "services_delete_confirm": "Delete service?",
    "service_edit_title": "Service",
    "service_hours": "Hours",
    "service_minutes": "Minutes",
    "service_duration_hint": "E.g.: 1 hour 30 minutes",
    "service_buffer_hint": "Time between sessions (cleaning, rest)",
    "service_save": "Save",
    "service_cancel": "Cancel",
}

I18N_HE = {
    "nav_clients": "לקוחות",
    "nav_services": "שירותים",

    "clients_title": "לקוחות",
    "clients_search": "חפש לפי שם או טלפון...",
    "clients_empty": "אין לקוחות עדיין",
    "clients_th_name": "שם",
    "clients_th_phone": "טלפון",
    "clients_th_email": "אימייל",
    "clients_th_created": "נוצר",
    "clients_notes": "הערות",
    "clients_back": "חזרה ללקוחות",
    "clients_edit": "עריכה",
    "client_edit_title": "עריכת לקוח",
    "client_notes_ph": "אלרגיות, העדפות, מאפיינים",
    "client_save": "שמור",
    "client_cancel": "ביטול",
    "client_bookings_history": "היסטוריית ביקורים",
    "client_bookings_empty": "אין ביקורים עדיין",
    "client_stat_total": "סה\"כ הזמנות",
    "client_stat_confirmed": "מאושר",
    "client_stat_revenue": "הכנסות",
    "client_stat_avg": "צ'ק ממוצע",

    "services_title": "שירותים",
    "services_new": "שירות חדש",
    "services_empty": "אין שירותים עדיין",
    "services_th_name": "שם",
    "services_th_duration": "משך",
    "services_th_price": "מחיר מ-",
    "services_th_buffer": "הפסקה",
    "services_delete_confirm": "למחוק שירות?",
    "service_edit_title": "שירות",
    "service_hours": "שעות",
    "service_minutes": "דקות",
    "service_duration_hint": "לדוגמה: שעה ו-30 דקות",
    "service_buffer_hint": "זמן בין מפגשים (ניקיון, מנוחה)",
    "service_save": "שמור",
    "service_cancel": "ביטול",
}


# ============================================
# 3. ОБНОВЛЕНИЕ _nav.html
# ============================================

NAV_HTML = """<div class="header">
    <div class="header-top">
        <h1>💉 {% if admin_lang == 'en' %}Master's Cabinet{% elif admin_lang == 'he' %}הקבינט של המאסטר{% else %}Кабинет мастера{% endif %}</h1>
        <div class="lang-switch">
            <a href="?lang=ru" class="lang-btn {% if admin_lang == 'ru' %}active{% endif %}" title="Русский">RU</a>
            <a href="?lang=en" class="lang-btn {% if admin_lang == 'en' %}active{% endif %}" title="English">EN</a>
            <a href="?lang=he" class="lang-btn {% if admin_lang == 'he' %}active{% endif %}" title="עברית">HE</a>
        </div>
    </div>
    <div class="header-nav">
        <a href="/admin" {% if active == 'home' %}class="active"{% endif %}>{{ t('admin_nav_home', admin_lang) }}</a>
        <a href="/admin/schedule" {% if active == 'schedule' %}class="active"{% endif %}>{{ t('admin_nav_schedule', admin_lang) }}</a>
        <a href="/admin/bookings" {% if active == 'bookings' %}class="active"{% endif %}>{{ t('admin_nav_bookings', admin_lang) }}</a>
        <a href="/admin/calendar" {% if active == 'calendar' %}class="active"{% endif %}>{{ t('admin_nav_calendar', admin_lang) }}</a>
        <a href="/admin/clients" {% if active == 'clients' %}class="active"{% endif %}>{{ t('nav_clients', admin_lang) }}</a>
        <a href="/admin/services" {% if active == 'services' %}class="active"{% endif %}>{{ t('nav_services', admin_lang) }}</a>
        <a href="/admin/stats" {% if active == 'stats' %}class="active"{% endif %}>{{ t('stats_title', admin_lang) }}</a>
        <a href="/admin/settings" {% if active == 'settings' %}class="active"{% endif %}>{{ t('admin_nav_settings', admin_lang) }}</a>
        <a href="/admin/logout">{{ t('admin_nav_logout', admin_lang) }}</a>
    </div>
</div>
"""


# ============================================
# 4. ОБНОВЛЕНИЕ _render_template_file
# ============================================

NEW_RENDER_FUNC = '''def _render_template_file(filename: str, **kwargs):
    if 'admin_lang' not in kwargs:
        kwargs['admin_lang'] = get_admin_lang()

    # Синхронизация валюты с языком
    try:
        sync_currency_with_lang(kwargs['admin_lang'])
    except Exception:
        pass

    if 't' not in kwargs:
        kwargs['t'] = t

    # Добавляем валюту во все шаблоны
    if 'currency' not in kwargs:
        try:
            kwargs['currency'] = get_currency()
            kwargs['currency_symbol'] = get_currency_symbol()
        except Exception:
            kwargs['currency'] = 'RUB'
            kwargs['currency_symbol'] = '₽'

    path = os.path.join(os.path.dirname(__file__), 'templates', filename)
    with open(path, encoding='utf-8') as f:
        return render_template_string(f.read(), **kwargs)
'''


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_part3_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    if I18N.exists():
        shutil.copytree(I18N, backup_dir / "i18n", dirs_exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    print(f"📦 Бэкап: {backup_dir.name}")
    print()


def update_nav():
    path = TEMPLATES / "_nav.html"
    path.write_text(NAV_HTML, encoding='utf-8')
    print("  ✅ _nav.html обновлён")


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
        print(f"  ✅ {lang}.json: {before} → {after} ключей")


def update_web_demo():
    if not WEB_DEMO.exists():
        return

    content = WEB_DEMO.read_text(encoding='utf-8')

    # 1. Импорты
    if 'from core.storage.clients import' not in content:
        marker = "from core.i18n.translator import t"
        imports = """from core.i18n.translator import t
from core.storage.clients import (
    get_or_create_client, get_client, get_all_clients,
    get_client_stats, get_client_bookings, update_client,
)
from core.storage.services import (
    get_all_services as get_services_list, get_service as get_service_by_id,
    create_service, update_service, delete_service,
)
from core.storage.settings import (
    get_currency, set_currency, get_currency_symbol,
    get_currency_for_lang, sync_currency_with_lang, is_currency_manual,
    get_all_currencies,
)"""
        if marker in content:
            content = content.replace(marker, imports, 1)
            print("  ✅ web_demo.py: импорты добавлены")

    # 2. Обновление _render_template_file
    old_render = '''def _render_template_file(filename: str, **kwargs):
    if 'admin_lang' not in kwargs:
        kwargs['admin_lang'] = get_admin_lang()
    if 't' not in kwargs:
        kwargs['t'] = t

    path = os.path.join(os.path.dirname(__file__), 'templates', filename)
    with open(path, encoding='utf-8') as f:
        return render_template_string(f.read(), **kwargs)'''

    if old_render in content:
        content = content.replace(old_render, NEW_RENDER_FUNC)
        print("  ✅ web_demo.py: _render_template_file обновлён")
    else:
        print("  ⏭️  web_demo.py: _render_template_file уже обновлён или не найден")

    # 3. Маршруты
    if '/admin/clients' not in content:
        marker = "if __name__ == '__main__':"
        if marker in content:
            content = content.replace(marker, ROUTES + "\n\n" + marker, 1)
            print("  ✅ web_demo.py: маршруты добавлены")
    else:
        print("  ⏭️  web_demo.py: маршруты уже есть")

    WEB_DEMO.write_text(content, encoding='utf-8')


def main():
    print("=" * 60)
    print("🚀 Часть 3: Маршруты + переводы + меню")
    print("=" * 60)
    print()

    backup()

    print("📄 Меню:")
    update_nav()
    print()

    print("🌍 Переводы:")
    update_i18n()
    print()

    print("🐍 web_demo.py:")
    update_web_demo()
    print()

    print("=" * 60)
    print("✅ ЧАСТЬ 3 ГОТОВА")
    print("=" * 60)
    print()
    print("Перезапустите web_demo.py:")
    print("  python web_demo.py")
    print()
    print("Проверьте:")
    print("  /admin/clients — список клиентов")
    print("  /admin/services — список услуг")
    print()


if __name__ == '__main__':
    main()
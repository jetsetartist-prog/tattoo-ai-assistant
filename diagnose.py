"""
Диагностика проекта: проверяет всё на ошибки.
Запуск: python diagnose.py
"""
import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
os.chdir(BASE)

# Цвета для вывода
OK = "✅"
FAIL = "❌"
WARN = "⚠️"
INFO = "ℹ️"


class Diagnostics:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = 0

    def check(self, name, condition, error_msg=""):
        if condition:
            print(f"  {OK} {name}")
            self.passed += 1
        else:
            print(f"  {FAIL} {name} {error_msg}")
            self.errors.append(f"{name}: {error_msg}")

    def warn(self, name, error_msg=""):
        print(f"  {WARN} {name} {error_msg}")
        self.warnings.append(f"{name}: {error_msg}")


d = Diagnostics()


# ============================================
# 1. ПРОВЕРКА СТРУКТУРЫ
# ============================================
print("=" * 60)
print("1. СТРУКТУРА ПРОЕКТА")
print("=" * 60)

d.check("Папка core/", (BASE / "core").exists())
d.check("Папка templates/", (BASE / "templates").exists())
d.check("Папка data/", (BASE / "data").exists())
d.check("Папка data/uploads/", (BASE / "data" / "uploads").exists())
d.check("Файл web_demo.py", (BASE / "web_demo.py").exists())
d.check("Файл .env", (BASE / ".env").exists())
d.check("БД data/leads.db", (BASE / "data" / "leads.db").exists())

print()


# ============================================
# 2. ПРОВЕРКА PYTHON-МОДУЛЕЙ
# ============================================
print("=" * 60)
print("2. PYTHON-МОДУЛИ (импорты)")
print("=" * 60)

modules = [
    ("core.messaging.base", ["MessageAdapter", "IncomingMessage", "Button"]),
    ("core.handlers.message_handler", ["handle_incoming"]),
    ("core.handlers.booking", ["start_booking", "handle_booking_input", "is_in_booking"]),
    ("core.ai.provider", ["get_ai_response"]),
    ("core.storage.leads", ["init_db", "save_lead", "get_all_leads"]),
    ("core.storage.schedule", [
        "init_schedule_db", "seed_default_data", "get_default_master",
        "get_all_work_hours", "set_work_hours", "get_master_by_email",
        "get_master", "get_bookings", "cancel_booking", "confirm_booking",
        "delete_booking", "create_manual_booking", "get_booking", "update_booking",
        "get_free_slots_bot", "get_free_slots_admin", "get_all_services",
        "get_service", "book_slot", "add_custom_slot", "get_custom_slots",
    ]),
    ("core.storage.clients", [
        "get_or_create_client", "get_client", "get_all_clients",
        "get_client_stats", "get_client_bookings", "update_client",
    ]),
    ("core.storage.services", [
        "get_all_services", "get_service", "create_service",
        "update_service", "delete_service",
    ]),
    ("core.storage.settings", [
        "get_currency", "set_currency", "get_currency_symbol",
        "get_currency_for_lang", "sync_currency_with_lang",
    ]),
    ("core.storage.stats", [
        "get_period_stats", "get_upcoming_count", "get_recent_bookings",
    ]),
    ("core.auth.mailer", ["init_mail", "send_master_password"]),
    ("core.auth.storage", [
        "generate_password", "create_session", "get_session", "destroy_session",
    ]),
    ("core.i18n.detector", ["detect_language"]),
    ("core.i18n.translator", ["t"]),
]

for module_name, names in modules:
    try:
        module = __import__(module_name, fromlist=names)
        missing = [n for n in names if not hasattr(module, n)]
        if missing:
            print(f"  {FAIL} {module_name}: нет {missing}")
            d.errors.append(f"{module_name}: нет {missing}")
        else:
            print(f"  {OK} {module_name} ({len(names)} функций)")
            d.passed += 1
    except Exception as e:
        print(f"  {FAIL} {module_name}: {e}")
        d.errors.append(f"{module_name}: {e}")

print()


# ============================================
# 3. ПРОВЕРКА ШАБЛОНОВ
# ============================================
print("=" * 60)
print("3. HTML-ШАБЛОНЫ")
print("=" * 60)

templates = [
    "_nav.html", "_lang_switch.html",
    "login.html", "forgot_password.html",
    "admin.html", "schedule.html", "bookings.html",
    "calendar.html", "stats.html", "settings.html",
    "new_booking.html", "booking_detail.html",
    "clients.html", "client_detail.html", "client_edit.html",
    "services.html", "service_edit.html",
]

for t in templates:
    path = BASE / "templates" / t
    if path.exists():
        size = path.stat().st_size
        print(f"  {OK} {t} ({size} байт)")
        d.passed += 1
    else:
        print(f"  {FAIL} {t} — НЕТ")
        d.errors.append(f"Шаблон {t} отсутствует")

print()


# ============================================
# 4. ПРОВЕРКА МАРШРУТОВ В WEB_DEMO.PY
# ============================================
print("=" * 60)
print("4. МАРШРУТЫ В WEB_DEMO.PY")
print("=" * 60)

web = (BASE / "web_demo.py").read_text(encoding='utf-8')

routes = [
    "/admin/login", "/admin/forgot-password", "/admin/logout",
    "/admin", "/admin/schedule", "/admin/bookings",
    "/admin/bookings/confirm", "/admin/bookings/cancel",
    "/admin/bookings/edit", "/admin/bookings/delete",
    "/admin/bookings/new", "/admin/uploads",
    "/admin/calendar", "/admin/stats", "/admin/settings",
    "/admin/clients", "/admin/clients/edit",
    "/admin/services", "/admin/services/new", "/admin/services/edit",
    "/admin/services/delete",
    "/admin/api/clients/search", "/admin/api/bookings/move",
    "/admin/api/slots/open",
]

for r in routes:
    if r in web:
        print(f"  {OK} {r}")
        d.passed += 1
    else:
        print(f"  {FAIL} {r} — НЕТ")
        d.errors.append(f"Маршрут {r} отсутствует")

print()


# ============================================
# 5. ПРОВЕРКА ИМПОРТОВ В WEB_DEMO
# ============================================
print("=" * 60)
print("5. ИМПОРТЫ В WEB_DEMO.PY")
print("=" * 60)

imports_to_check = [
    "get_default_master", "get_bookings", "create_manual_booking",
    "get_booking", "get_free_slots_admin", "update_booking_price",
    "delete_booking", "get_all_clients", "get_or_create_client",
    "create_service", "update_service", "delete_service",
    "get_currency", "get_currency_symbol",
]

for imp in imports_to_check:
    if imp in web:
        print(f"  {OK} {imp}")
        d.passed += 1
    else:
        print(f"  {FAIL} {imp} — нет в web_demo.py")
        d.errors.append(f"Импорт {imp} отсутствует")

print()


# ============================================
# 6. ПРОВЕРКА JSON-ПЕРЕВОДОВ
# ============================================
print("=" * 60)
print("6. JSON-ПЕРЕВОДЫ")
print("=" * 60)

required_keys = [
    "welcome", "menu_booking", "menu_price",
    "admin_nav_home", "admin_nav_schedule", "admin_nav_bookings",
    "admin_nav_calendar", "admin_nav_settings", "admin_nav_logout",
    "calendar_title", "calendar_day_off",
    "off_slot_title", "off_slot_question", "off_slot_yes", "off_slot_no",
    "new_booking_title", "new_booking_save",
    "booking_source", "booking_source_online", "booking_source_manual",
    "clients_title", "services_title", "nav_clients", "nav_services",
    "stats_title", "currency",
]

for lang in ["ru", "en", "he"]:
    path = BASE / "core" / "i18n" / f"{lang}.json"
    if not path.exists():
        print(f"  {FAIL} {lang}.json — НЕТ")
        d.errors.append(f"{lang}.json отсутствует")
        continue

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"  {WARN} {lang}.json — нет {len(missing)} ключей: {missing[:5]}...")
        d.warnings.append(f"{lang}.json: нет {missing}")
    else:
        print(f"  {OK} {lang}.json — все {len(required_keys)} ключей есть")
        d.passed += 1

print()


# ============================================
# 7. ПРОВЕРКА БД
# ============================================
print("=" * 60)
print("7. БАЗА ДАННЫХ")
print("=" * 60)

try:
    conn = sqlite3.connect(BASE / "data" / "leads.db")
    cur = conn.cursor()

    # Таблицы
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]

    for table in ["leads", "masters", "work_hours", "services", "bookings", "clients", "settings", "custom_slots"]:
        if table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  {OK} {table} ({count} записей)")
            d.passed += 1
        else:
            print(f"  {FAIL} Таблица {table} — НЕТ")
            d.errors.append(f"Таблица {table} отсутствует")

    # Колонки bookings
    print()
    print("  Колонки в bookings:")
    cur.execute("PRAGMA table_info(bookings)")
    cols = [r[1] for r in cur.fetchall()]
    for col in ["id", "master_id", "date", "time", "duration", "status",
                "notes", "reference_image", "client_id", "price", "deposit", "source"]:
        if col in cols:
            print(f"    {OK} {col}")
            d.passed += 1
        else:
            print(f"    {FAIL} {col} — НЕТ")
            d.errors.append(f"Колонка bookings.{col} отсутствует")

    conn.close()
except Exception as e:
    print(f"  {FAIL} Ошибка БД: {e}")
    d.errors.append(f"БД: {e}")

print()


# ============================================
# ИТОГ
# ============================================
print("=" * 60)
print("ИТОГ")
print("=" * 60)
print()
print(f"  {OK} Проверок пройдено: {d.passed}")
print(f"  {FAIL} Ошибок: {len(d.errors)}")
print(f"  {WARN} Предупреждений: {len(d.warnings)}")
print()

if d.errors:
    print(f"{FAIL} ОШИБКИ:")
    for e in d.errors:
        print(f"  - {e}")
    print()

if d.warnings:
    print(f"{WARN} ПРЕДУПРЕЖДЕНИЯ:")
    for w in d.warnings[:10]:
        print(f"  - {w}")
    print()

if not d.errors:
    print(f"{OK} ВСЁ РАБОТАЕТ! Ошибок нет.")
else:
    print(f"{FAIL} ЕСТЬ ОШИБКИ. Смотрите список выше.")
print()
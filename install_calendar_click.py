"""
Установщик фичи: клик по слоту в календаре.
- Клик по пустому слоту → форма новой записи с предзаполненной датой/временем
- Клик по записи → детали записи (комментарий, фото)
Запуск: python install_calendar_click.py
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
# 1. ОБНОВЛЁННЫЙ calendar.html
# ============================================

CALENDAR_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('calendar_title', admin_lang) }}</title>
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

        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }

        .nav-week {
            display: flex; justify-content: space-between; align-items: center;
            background: white; padding: 16px 24px; border-radius: 12px;
            margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .nav-week h2 { color: #075e54; font-size: 18px; }
        .nav-week .links a {
            display: inline-block; padding: 8px 16px; background: #f0f0f0; color: #333;
            text-decoration: none; border-radius: 8px; font-size: 14px; margin-left: 8px;
        }
        .nav-week .links a:hover { background: #e0e0e0; }
        .nav-week .links a.today { background: #25d366; color: white; }
        .nav-week .links a.new-booking { background: #075e54; color: white; }

        .calendar {
            background: white; border-radius: 12px; overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .cal-header {
            display: grid; grid-template-columns: 80px repeat(7, 1fr);
            background: #f9f9f9; border-bottom: 2px solid #eee;
        }
        .cal-header > div {
            padding: 14px 8px; text-align: center; font-size: 13px;
            font-weight: 600; color: #666; border-right: 1px solid #eee;
        }
        .cal-header > div:last-child { border-right: none; }
        .cal-header .today { background: #e8f5e9; color: #075e54; }

        .cal-body {
            display: grid; grid-template-columns: 80px repeat(7, 1fr);
        }
        .time-slot {
            padding: 8px; font-size: 11px; color: #999; text-align: right;
            border-right: 1px solid #eee; border-bottom: 1px solid #f5f5f5; height: 60px;
        }
        .day-slot {
            border-right: 1px solid #eee; border-bottom: 1px solid #f5f5f5;
            height: 60px; position: relative; padding: 2px;
            cursor: pointer; transition: background 0.15s;
        }
        .day-slot:hover { background: #f0f8f5; }
        .day-slot:last-child { border-right: none; }

        .booking {
            background: linear-gradient(135deg, #25d366 0%, #1ebe5d 100%);
            color: white; padding: 4px 6px; border-radius: 6px;
            font-size: 11px; line-height: 1.3; cursor: pointer;
            overflow: hidden; height: 100%;
            display: flex; flex-direction: column; justify-content: center;
            position: relative;
        }
        .booking:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(37, 211, 102, 0.4); }
        .booking.pending { background: linear-gradient(135deg, #ffb74d 0%, #ff9800 100%); }
        .booking.cancelled { background: #ccc; text-decoration: line-through; opacity: 0.6; }
        .booking .b-name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .booking .b-time { font-size: 10px; opacity: 0.9; }
        .booking .b-icons { font-size: 10px; position: absolute; top: 3px; right: 4px; }

        .legend { display: flex; gap: 20px; margin-top: 16px; font-size: 13px; color: #666; }
        .legend-item { display: flex; align-items: center; gap: 6px; }
        .legend-color { width: 16px; height: 16px; border-radius: 4px; }

        .hint {
            background: #e8f5e9; color: #2e7d32; padding: 12px 16px;
            border-radius: 8px; font-size: 13px; margin-top: 16px;
        }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="nav-week">
            <h2>{{ week_label }}</h2>
            <div class="links">
                <a href="/admin/calendar?week_offset={{ week_offset - 1 }}">← {{ t('calendar_prev', admin_lang) }}</a>
                <a href="/admin/calendar?week_offset=0" class="today">{{ t('calendar_today', admin_lang) }}</a>
                <a href="/admin/calendar?week_offset={{ week_offset + 1 }}">{{ t('calendar_next', admin_lang) }} →</a>
                <a href="/admin/bookings/new" class="new-booking">➕ {{ t('new_booking_btn', admin_lang) }}</a>
            </div>
        </div>

        <div class="calendar">
            <div class="cal-header">
                <div></div>
                {% for day in days %}
                <div class="{% if day.is_today %}today{% endif %}">
                    {{ day.name }}<br>
                    <small>{{ day.day_num }}</small>
                </div>
                {% endfor %}
            </div>

            <div class="cal-body">
                {% for hour in hours %}
                <div class="time-slot">{{ hour }}:00</div>
                    {% for day in days %}
                    {% set slot_bookings = day.bookings_by_hour.get(hour, []) %}
                    {% if slot_bookings %}
                    <div class="day-slot">
                        {% for b in slot_bookings %}
                        <a href="/admin/bookings" style="text-decoration: none;">
                            <div class="booking {% if b.status == 'pending' %}pending{% elif b.status == 'cancelled' %}cancelled{% endif %}">
                                <div class="b-name">{{ b.name }}</div>
                                <div class="b-time">{{ b.time }} · {{ b.duration // 60 }}ч</div>
                                {% if b.has_notes or b.has_image %}
                                <div class="b-icons">
                                    {% if b.has_notes %}💬{% endif %}
                                    {% if b.has_image %}📎{% endif %}
                                </div>
                                {% endif %}
                            </div>
                        </a>
                        {% endfor %}
                    </div>
                    {% else %}
                    <a href="/admin/bookings/new?date={{ day.date }}&time={{ '%02d' % hour }}:00" style="text-decoration: none; color: inherit;">
                        <div class="day-slot"></div>
                    </a>
                    {% endif %}
                    {% endfor %}
                {% endfor %}
            </div>
        </div>

        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background: #25d366;"></div><span>{{ t('calendar_legend_confirmed', admin_lang) }}</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #ff9800;"></div><span>{{ t('calendar_legend_pending', admin_lang) }}</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #ccc;"></div><span>{{ t('calendar_legend_cancelled', admin_lang) }}</span></div>
            <div class="legend-item"><span>💬 {{ t('calendar_has_notes', admin_lang) }}</span></div>
            <div class="legend-item"><span>📎 {{ t('calendar_has_image', admin_lang) }}</span></div>
        </div>

        <div class="hint">
            💡 {{ t('calendar_click_hint', admin_lang) }}
        </div>
    </div>
</body>
</html>
"""


# ============================================
# 2. ПЕРЕВОДЫ
# ============================================

I18N_NEW = {
    "ru": {
        "calendar_has_notes": "есть комментарий",
        "calendar_has_image": "есть эскиз",
        "calendar_click_hint": "Кликните по свободному слоту, чтобы создать запись",
    },
    "en": {
        "calendar_has_notes": "has notes",
        "calendar_has_image": "has sketch",
        "calendar_click_hint": "Click on a free slot to create a booking",
    },
    "he": {
        "calendar_has_notes": "יש הערה",
        "calendar_has_image": "יש סקיצה",
        "calendar_click_hint": "לחץ על משבצת פנויה כדי ליצור הזמנה",
    },
}


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_cal_click_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    if I18N.exists():
        shutil.copytree(I18N, backup_dir / "i18n", dirs_exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    print(f"📦 Бэкап: {backup_dir.name}")


def update_calendar_html():
    path = TEMPLATES / "calendar.html"
    path.write_text(CALENDAR_HTML, encoding='utf-8')
    print("✅ Обновлён: templates/calendar.html")


def update_i18n():
    for lang, data in I18N_NEW.items():
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


def update_calendar_route():
    """Обновляет маршрут admin_calendar в web_demo.py — добавляет has_notes, has_image."""
    if not WEB_DEMO.exists():
        print("❌ Нет web_demo.py")
        return

    content = WEB_DEMO.read_text(encoding='utf-8')

    old_block = """            bookings_by_hour[hour].append({
                'id': b['id'],
                'time': b['time'],
                'duration': b['duration'],
                'status': b['status'],
                'name': lead['name'] if lead else '—',
            })"""

    new_block = """            bookings_by_hour[hour].append({
                'id': b['id'],
                'time': b['time'],
                'duration': b['duration'],
                'status': b['status'],
                'name': lead['name'] if lead else '—',
                'has_notes': bool(b.get('notes')),
                'has_image': bool(b.get('reference_image')),
            })"""

    if old_block in content:
        content = content.replace(old_block, new_block)
        WEB_DEMO.write_text(content, encoding='utf-8')
        print("✅ web_demo.py: маршрут календаря обновлён")
    else:
        print("⏭️  web_demo.py: не найден блок для замены (или уже обновлён)")


def main():
    print("=" * 60)
    print("🚀 Установка фичи: клик по слоту в календаре")
    print("=" * 60)
    print()

    backup()
    print()

    print("📄 Шаблон:")
    update_calendar_html()
    print()

    print("🌍 Переводы:")
    update_i18n()
    print()

    print("🐍 Обновление web_demo.py:")
    update_calendar_route()
    print()

    print("=" * 60)
    print("✅ Готово!")
    print("=" * 60)
    print()
    print("Что делать:")
    print("1. Перезапустите web_demo.py")
    print("2. Откройте /admin/calendar")
    print("3. Кликните по свободному слоту — откроется форма с предзаполненной датой")
    print()


if __name__ == '__main__':
    main()
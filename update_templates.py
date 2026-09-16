"""
Автоматически обновляет шаблоны и web_demo.py:
1. Создаёт templates/_nav.html
2. Заменяет <div class="header">...</div> на {% include '_nav.html' %} во всех шаблонах
3. Добавляет active='...' в вызовы _render_template_file в web_demo.py

Запуск: python update_templates.py
"""
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"
WEB_DEMO = BASE / "web_demo.py"

# ============================================
# 1. _nav.html
# ============================================

NAV_HTML = """<div class="header">
    <h1>💉 Кабинет мастера</h1>
    <div class="nav">
        <a href="/admin" {% if active == 'home' %}class="active"{% endif %}>Главная</a>
        <a href="/admin/schedule" {% if active == 'schedule' %}class="active"{% endif %}>Расписание</a>
        <a href="/admin/bookings" {% if active == 'bookings' %}class="active"{% endif %}>Записи</a>
        <a href="/admin/calendar" {% if active == 'calendar' %}class="active"{% endif %}>Календарь</a>
        <a href="/admin/settings" {% if active == 'settings' %}class="active"{% endif %}>Настройки</a>
        <a href="/admin/logout">Выйти</a>
    </div>
</div>"""

# ============================================
# 2. Замена в шаблонах
# ============================================

# Регулярное выражение: от <div class="header"> до закрывающего </div> перед <div class="container">
NAV_PATTERN = re.compile(
    r'<div class="header">.*?</div>\s*</div>',
    re.DOTALL
)

# ============================================
# 3. Маршруты в web_demo.py → active
# ============================================

# Какие функции → какой active
ROUTE_ACTIVE = {
    'admin_dashboard': 'home',
    'admin_schedule': 'schedule',
    'admin_bookings': 'bookings',
    'admin_calendar': 'calendar',
    'admin_settings': 'settings',
}


def backup():
    """Делает бэкап web_demo.py и templates."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    # web_demo.py
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")

    # templates
    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)

    print(f"📦 Бэкап создан: {backup_dir}")
    return backup_dir


def create_nav():
    """Создаёт _nav.html."""
    nav_file = TEMPLATES / "_nav.html"
    nav_file.write_text(NAV_HTML, encoding='utf-8')
    print(f"✅ Создан: {nav_file}")


def replace_in_templates():
    """Заменяет блок header на {% include '_nav.html' %} во всех шаблонах."""
    templates_to_update = ['admin.html', 'schedule.html', 'bookings.html', 'calendar.html', 'settings.html']

    for name in templates_to_update:
        path = TEMPLATES / name
        if not path.exists():
            print(f"⏭️  Пропущен (нет файла): {name}")
            continue

        content = path.read_text(encoding='utf-8')

        # Ищем <div class="header">...</div> (первое вхождение)
        match = NAV_PATTERN.search(content)
        if not match:
            print(f"⚠️  Не найден header в: {name}")
            continue

        new_content = NAV_PATTERN.sub("{% include '_nav.html' %}", content, count=1)
        path.write_text(new_content, encoding='utf-8')
        print(f"✅ Обновлён: {name}")


def update_web_demo():
    """Добавляет active='...' в вызовы _render_template_file."""
    if not WEB_DEMO.exists():
        print(f"❌ Не найден: {WEB_DEMO}")
        return

    content = WEB_DEMO.read_text(encoding='utf-8')
    original = content

    # Для каждого маршрута добавляем active
    replacements = [
        # admin_dashboard
        (
            "return _render_template_file('admin.html', email=email)",
            "return _render_template_file('admin.html', email=email, active='home')",
        ),
        # admin_schedule
        (
            "return _render_template_file('schedule.html', days=days, saved=saved)",
            "return _render_template_file('schedule.html', days=days, saved=saved, active='schedule')",
        ),
        # admin_bookings
        (
            """    return _render_template_file(
        'bookings.html',
        bookings=enriched,
        filter_type=filter_type,
    )""",
            """    return _render_template_file(
        'bookings.html',
        bookings=enriched,
        filter_type=filter_type,
        active='bookings',
    )""",
        ),
        # admin_calendar
        (
            """    return _render_template_file(
        'calendar.html',
        days=days,
        hours=hours,
        week_label=week_label,
        week_offset=week_offset,
    )""",
            """    return _render_template_file(
        'calendar.html',
        days=days,
        hours=hours,
        week_label=week_label,
        week_offset=week_offset,
        active='calendar',
    )""",
        ),
        # admin_settings
        (
            """    return _render_template_file(
        'settings.html',
        email=email,
        error=error,
        info=info,
    )""",
            """    return _render_template_file(
        'settings.html',
        email=email,
        error=error,
        info=info,
        active='settings',
    )""",
        ),
    ]

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Заменено в web_demo.py: {old[:60]}...")
        else:
            print(f"⚠️  Не найдено в web_demo.py: {old[:60]}...")

    if content != original:
        WEB_DEMO.write_text(content, encoding='utf-8')
        print("✅ web_demo.py обновлён")
    else:
        print("⏭️  web_demo.py без изменений")


def main():
    print("=" * 60)
    print("🚀 Обновление шаблонов и web_demo.py")
    print("=" * 60)
    print()

    # 1. Бэкап
    backup_dir = backup()
    print()

    # 2. _nav.html
    create_nav()
    print()

    # 3. Шаблоны
    print("📄 Обновление шаблонов:")
    replace_in_templates()
    print()

    # 4. web_demo.py
    print("🐍 Обновление web_demo.py:")
    update_web_demo()
    print()

    print("=" * 60)
    print("✅ Готово!")
    print(f"📦 Бэкап: {backup_dir}")
    print("=" * 60)
    print()
    print("Теперь перезапустите web_demo.py:")
    print("  python web_demo.py")
    print()


if __name__ == '__main__':
    main()
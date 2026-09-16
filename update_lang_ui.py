"""
Автоматически обновляет CSS для кнопок языка во всех шаблонах кабинета.
- Заменяет блок .header и .header .nav на новый
- Добавляет стили .header-top, .header-nav, .lang-switch, .lang-btn

Запуск: python update_lang_ui.py
Существующие бэкапы сохраняются в backup_lang_ui_TIMESTAMP/
"""
import re
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"

# Шаблоны для обновления
TEMPLATES_TO_UPDATE = [
    'admin.html',
    'schedule.html',
    'bookings.html',
    'calendar.html',
    'settings.html',
]

# Новый CSS для header
NEW_HEADER_CSS = """        .header {
            background: #075e54;
            color: white;
        }
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 40px 10px 40px;
        }
        .header-top h1 { font-size: 20px; }
        .header-nav {
            display: flex;
            gap: 20px;
            padding: 0 40px 14px 40px;
        }
        .header-nav a {
            color: white;
            text-decoration: none;
            font-size: 14px;
            opacity: 0.8;
            transition: opacity 0.2s;
        }
        .header-nav a:hover { opacity: 1; }
        .header-nav a.active {
            opacity: 1;
            font-weight: 600;
            border-bottom: 2px solid #25d366;
            padding-bottom: 2px;
        }
        .lang-switch {
            display: flex;
            gap: 5px;
        }
        .lang-btn {
            display: inline-block;
            padding: 3px 8px;
            background: rgba(255, 255, 255, 0.15);
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            transition: background 0.2s;
            line-height: 1.4;
        }
        .lang-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        .lang-btn.active {
            background: #25d366;
            color: white;
        }"""

# Регулярка: от .header { до конца .header .nav a.active (старый блок)
OLD_HEADER_PATTERN = re.compile(
    r'\.header\s*\{.*?\.header\s+\.nav\s+a\.active\s*\{[^}]*\}\s*\}',
    re.DOTALL
)


def backup():
    """Делает бэкап папки templates."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_lang_ui_{timestamp}"

    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
        print(f"📦 Бэкап: {backup_dir.name}")
    return backup_dir


def update_template(name: str) -> bool:
    """Обновляет один шаблон. Возвращает True, если обновлён."""
    path = TEMPLATES / name
    if not path.exists():
        print(f"⏭️  Пропущен (нет файла): {name}")
        return False

    content = path.read_text(encoding='utf-8')

    # Проверяем, есть ли уже новый CSS
    if '.header-top' in content and '.lang-switch' in content:
        print(f"⏭️  Уже обновлён: {name}")
        return False

    # Ищем старый блок .header
    if '.header {' not in content:
        print(f"⚠️  Не найден .header в: {name}")
        return False

    # Заменяем старый CSS на новый
    # Сначала попробуем точную замену
    new_content = OLD_HEADER_PATTERN.sub(NEW_HEADER_CSS, content, count=1)

    # Если не сработало — попробуем проще: заменить от ".header {" до "}" перед следующим селектором
    if new_content == content:
        # Ищем первый блок .header { ... }
        pattern2 = re.compile(
            r'\.header\s*\{[^}]*\}',
            re.DOTALL
        )
        new_content = pattern2.sub(NEW_HEADER_CSS, content, count=1)

    # Также удаляем старые стили .header .nav (если остались)
    pattern3 = re.compile(
        r'\.header\s+\.nav\s+a\s*\{[^}]*\}',
        re.DOTALL
    )
    new_content = pattern3.sub('', new_content)

    pattern4 = re.compile(
        r'\.header\s+\.nav\s+a:hover\s*\{[^}]*\}',
        re.DOTALL
    )
    new_content = pattern4.sub('', new_content)

    pattern5 = re.compile(
        r'\.header\s+\.nav\s+a\.active\s*\{[^}]*\}',
        re.DOTALL
    )
    new_content = pattern5.sub('', new_content)

    if new_content == content:
        print(f"⚠️  Не удалось заменить CSS в: {name}")
        return False

    path.write_text(new_content, encoding='utf-8')
    print(f"✅ Обновлён: {name}")
    return True


def main():
    print("=" * 60)
    print("🚀 Обновление CSS для кнопок языка")
    print("=" * 60)
    print()

    # Бэкап
    backup()
    print()

    # Обновление
    updated = 0
    for name in TEMPLATES_TO_UPDATE:
        if update_template(name):
            updated += 1

    print()
    print("=" * 60)
    print(f"✅ Готово! Обновлено: {updated} из {len(TEMPLATES_TO_UPDATE)}")
    print("=" * 60)
    print()
    print("Проверьте страницы кабинета — кнопки языка справа сверху.")
    print()


if __name__ == '__main__':
    main()
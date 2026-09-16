"""
Проверка и создание структуры проекта.
- Существующие файлы НЕ трогает.
- Создаёт только то, чего не хватает.
- Показывает отчёт.

Запуск: python check_structure.py
"""
import os
import sys
from pathlib import Path

# ============================================
# Что должно быть в проекте
# ============================================

# Папки
FOLDERS = [
    "core",
    "core/messaging",
    "core/handlers",
    "core/ai",
    "core/storage",
    "core/auth",
    "adapters",
    "templates",
    "data",
    "logs",
]

# Файлы с содержимым
FILES = {
    # Пакеты
    "core/__init__.py": "",
    "core/messaging/__init__.py": "",
    "core/handlers/__init__.py": "",
    "core/ai/__init__.py": "",
    "core/storage/__init__.py": "",
    "core/auth/__init__.py": "",
    "adapters/__init__.py": "",

    # Заглушки (создаются, если файлов нет)
    "core/messaging/base.py": '"""Базовые интерфейсы адаптеров."""\n',
    "core/handlers/message_handler.py": '"""Ядро: обработка сообщений."""\n',
    "core/handlers/booking.py": '"""Форма записи."""\n',
    "core/ai/provider.py": '"""AI-провайдер."""\n',
    "core/storage/leads.py": '"""Работа с БД лидов."""\n',
    "core/auth/mailer.py": '"""Отправка email с кодами."""\n',
    "core/auth/storage.py": '"""Хранение кодов и сессий."""\n',
    "adapters/vk_adapter.py": '"""VK-адаптер."""\n',
    "adapters/telegram_adapter.py": '"""Telegram-адаптер."""\n',

    # HTML-шаблоны
    "templates/login.html": "<!-- Страница входа -->\n",
    "templates/verify.html": "<!-- Страница ввода кода -->\n",
    "templates/admin.html": "<!-- Кабинет мастера -->\n",
}


def check_and_create():
    """Проверяет структуру и создаёт то, чего не хватает."""
    base = Path(".")

    created_folders = []
    existing_folders = []
    created_files = []
    existing_files = []
    error_files = []

    print("=" * 60)
    print("ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")
    print("=" * 60)
    print()

    # Папки
    print("📁 ПАПКИ:")
    for folder in FOLDERS:
        path = base / folder
        if path.exists():
            existing_folders.append(folder)
            print(f"  ✅ {folder}")
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                created_folders.append(folder)
                print(f"  🆕 {folder} (создана)")
            except Exception as e:
                print(f"  ❌ {folder} — ошибка: {e}")

    print()

    # Файлы
    print("📄 ФАЙЛЫ:")
    for file_path, content in FILES.items():
        path = base / file_path
        if path.exists():
            size = path.stat().st_size
            if size > 0:
                existing_files.append(file_path)
                print(f"  ✅ {file_path} ({size} байт)")
            else:
                # Пустой файл — оставляем как есть
                existing_files.append(file_path)
                print(f"  ⚠️  {file_path} (пустой, оставлен)")
        else:
            try:
                # Создаём родительскую папку, если её нет
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                created_files.append(file_path)
                print(f"  🆕 {file_path} (создан)")
            except Exception as e:
                error_files.append((file_path, str(e)))
                print(f"  ❌ {file_path} — ошибка: {e}")

    print()
    print("=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"Папок создано:      {len(created_folders)}")
    print(f"Папок уже было:     {len(existing_folders)}")
    print(f"Файлов создано:     {len(created_files)}")
    print(f"Файлов уже было:    {len(existing_files)}")
    if error_files:
        print(f"Ошибок:             {len(error_files)}")
        for fp, err in error_files:
            print(f"  ❌ {fp}: {err}")
    print()

    # Проверка важных файлов
    print("=" * 60)
    print("ПРОВЕРКА КЛЮЧЕВЫХ ФАЙЛОВ")
    print("=" * 60)

    important = [
        ".env",
        "web_demo.py",
        "main_multiplatform.py",
        "core/messaging/base.py",
        "core/handlers/message_handler.py",
        "core/auth/mailer.py",
        "core/auth/storage.py",
        "templates/login.html",
        "templates/verify.html",
        "templates/admin.html",
    ]

    for fp in important:
        path = base / fp
        if path.exists():
            size = path.stat().st_size
            if size > 50:
                print(f"  ✅ {fp} ({size} байт)")
            else:
                print(f"  ⚠️  {fp} ({size} байт — возможно, заглушка)")
        else:
            print(f"  ❌ {fp} — ОТСУТСТВУЕТ")

    print()
    print("✅ Проверка завершена.")


if __name__ == "__main__":
    check_and_create()
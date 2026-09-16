"""
Создаёт структуру папок и файлов для мультиплатформенной архитектуры.
Запускать из корня проекта: python setup_structure.py
"""
import os
from pathlib import Path

folders = [
    "core",
    "core/messaging",
    "core/handlers",
    "core/ai",
    "core/storage",
    "adapters",
]

files = {
    "core/__init__.py": "",
    "core/messaging/__init__.py": "",
    "core/handlers/__init__.py": "",
    "core/ai/__init__.py": "",
    "core/storage/__init__.py": "",
    "adapters/__init__.py": "",
    "core/messaging/base.py": '"""Базовые интерфейсы адаптеров."""\n',
    "core/messaging/types.py": '"""Dataclasses для сообщений."""\n',
    "core/handlers/message_handler.py": '"""Ядро: обработка сообщений."""\n',
    "core/ai/provider.py": '"""Абстракция AI-провайдера."""\n',
    "core/storage/leads.py": '"""Работа с БД лидов."""\n',
    "adapters/vk_adapter.py": '"""VK-адаптер."""\n',
    "adapters/telegram_adapter.py": '"""Telegram-адаптер (заглушка)."""\n',
}

base = Path(".")

for folder in folders:
    path = base / folder
    path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Создана папка: {folder}")

for file_path, content in files.items():
    path = base / file_path
    if path.exists():
        print(f"⏭️  Файл уже существует: {file_path}")
        continue
    path.write_text(content, encoding="utf-8")
    print(f"📄 Создан файл: {file_path}")

print("\n✅ Готово. Структура создана.")
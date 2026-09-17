"""
Очистка проекта от мусора.
Показывает что удаляется, что оставляется.
Запуск: python cleanup.py
"""
import shutil
from pathlib import Path

BASE = Path(__file__).parent

# Что удаляем
TO_DELETE_PATTERNS = [
    'backup_*',           # все папки бэкапов
    '*.bak',              # бэкапы файлов
    '*.pyc',              # скомпилированные
]

# Файлы, которые можно удалить (тесты, старые версии)
TO_DELETE_FILES = [
    'test_mail.py',       # тест почты — уже не нужен
    'verify.html',        # старый шаблон
]

# Файлы, которые можно удалить, но с подтверждением
OPTIONAL_DELETE = [
    'install_crm.py',           # заменён на part1/2/3
    'install_crm_full.py',      # заменён на part1/2/3
]


def main():
    print("=" * 60)
    print("🧹 Очистка проекта от мусора")
    print("=" * 60)
    print()

    total_size = 0
    deleted = []

    # Папки-бэкапы
    print("📁 Папки-бэкапы:")
    for path in BASE.glob('backup_*'):
        if path.is_dir():
            size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            total_size += size
            print(f"  🗑 {path.name} ({size / 1024:.1f} КБ)")
            shutil.rmtree(path)
            deleted.append(path.name)

    # .bak файлы
    print()
    print("📄 .bak файлы:")
    for path in BASE.glob('*.bak'):
        size = path.stat().st_size
        total_size += size
        print(f"  🗑 {path.name} ({size / 1024:.1f} КБ)")
        path.unlink()
        deleted.append(path.name)

    # Тестовые файлы
    print()
    print("🧪 Тестовые файлы:")
    for name in TO_DELETE_FILES:
        path = BASE / name
        if not path.exists():
            path = BASE / 'templates' / name
        if path.exists():
            size = path.stat().st_size
            total_size += size
            print(f"  🗑 {path.relative_to(BASE)} ({size / 1024:.1f} КБ)")
            path.unlink()
            deleted.append(str(path.relative_to(BASE)))

    # Опциональные
    print()
    print("⚠️  Опциональные (можно удалить):")
    for name in OPTIONAL_DELETE:
        path = BASE / name
        if path.exists():
            size = path.stat().st_size
            print(f"  ❓ {name} ({size / 1024:.1f} КБ) — удалить вручную, если не нужен")

    print()
    print("=" * 60)
    print(f"✅ Удалено: {len(deleted)} объектов")
    print(f"📊 Освобождено: {total_size / 1024:.1f} КБ")
    print("=" * 60)


if __name__ == '__main__':
    main()
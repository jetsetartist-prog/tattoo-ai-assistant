"""
Создаёт структуру для i18n:
- core/i18n/__init__.py
- core/i18n/detector.py
- core/i18n/translator.py
- core/i18n/ru.json
- core/i18n/en.json
- core/i18n/he.json
- test_lang.py

Запуск: python setup_i18n.py
Существующие файлы НЕ перезаписывает.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent

# ============================================
# Содержимое файлов
# ============================================

INIT_PY = ""

DETECTOR_PY = '''"""
Определение языка текста: ru / he / en.
Без AI — на основе алфавита и статистики.
"""
import re


# Карта раскладки: английские клавиши → русские
LAYOUT_MAP = str.maketrans(
    "qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:\\"ZXCVBNM<>?~",
    "йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё",
)


def _has_hebrew(text: str) -> bool:
    return bool(re.search(r'[\\u0590-\\u05FF]', text))


def _has_cyrillic(text: str) -> bool:
    return bool(re.search(r'[а-яА-ЯёЁ]', text))


def _has_latin(text: str) -> bool:
    return bool(re.search(r'[a-zA-Z]', text))


def _is_translit(text: str) -> bool:
    """Проверяет, является ли латинский текст транслитом русского."""
    if not _has_latin(text):
        return False

    transliterated = text.translate(LAYOUT_MAP)

    if _has_cyrillic(transliterated):
        words = re.findall(r'[а-яё]+', transliterated.lower())
        common_ru = ['привет', 'прайс', 'записаться', 'запись', 'цена', 'контакты', 'меню', 'портфолио']
        for word in words:
            for common in common_ru:
                if word.startswith(common[:3]) or common.startswith(word[:3]):
                    return True
        return True

    return False


def detect_language(text: str) -> str:
    """
    Определяет язык текста.
    Возвращает: 'ru', 'he' или 'en'.
    """
    if not text or not text.strip():
        return 'ru'

    text = text.strip()

    # Иврит — по алфавиту
    if _has_hebrew(text):
        return 'he'

    # Кириллица — точно русский
    if _has_cyrillic(text):
        return 'ru'

    # Латинница — английский или транслит
    if _has_latin(text):
        if _is_translit(text):
            return 'ru'
        return 'en'

    return 'ru'
'''

TRANSLATOR_PY = '''"""
Переводчик строк.
Функция t(key, lang) — возвращает строку из ru.json / en.json / he.json.
"""
import json
from pathlib import Path
from loguru import logger

_LOCALES_DIR = Path(__file__).parent

# Кэш загруженных переводов {lang: {key: value}}
_translations: dict = {}

SUPPORTED_LANGS = ['ru', 'he', 'en']
DEFAULT_LANG = 'ru'


def _load_lang(lang: str) -> dict:
    """Загружает переводы для языка."""
    if lang in _translations:
        return _translations[lang]

    file = _LOCALES_DIR / f"{lang}.json"
    if not file.exists():
        logger.warning(f"[i18n] Нет файла переводов: {file}")
        _translations[lang] = {}
        return {}

    try:
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
        _translations[lang] = data
        return data
    except Exception as e:
        logger.error(f"[i18n] Ошибка загрузки {file}: {e}")
        _translations[lang] = {}
        return {}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """
    Возвращает перевод строки.

    Пример:
        t("welcome", "ru") → "Привет!"
        t("welcome", "en") → "Hello!"
        t("booking_ask_name", "ru", name="Иван") → "Привет, Иван!"
    """
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG

    translations = _load_lang(lang)

    # Ищем ключ
    value = translations.get(key)

    # Fallback на русский
    if value is None and lang != DEFAULT_LANG:
        value = _load_lang(DEFAULT_LANG).get(key)

    # Если ключ не найден — возвращаем сам ключ
    if value is None:
        logger.warning(f"[i18n] Ключ не найден: '{key}' (lang={lang})")
        return key

    # Подставляем переменные
    if kwargs:
        try:
            value = value.format(**kwargs)
        except Exception as e:
            logger.error(f"[i18n] Ошибка форматирования '{key}': {e}")

    return value


def reload_translations() -> None:
    """Сбрасывает кэш переводов — для разработки."""
    global _translations
    _translations = {}
'''

RU_JSON = {
    "welcome": "👋 Привет! Я AI-ассистент тату-салона.\nВыбери действие:",
    "menu_booking": "Записаться",
    "menu_price": "Прайс",
    "menu_portfolio": "Портфолио",
    "menu_contacts": "Контакты",
    "price": "💰 Прайс:\n• Эскиз — от 2000₽\n• Маленькая (до 10 см) — от 5000₽\n• Средняя (10-20 см) — от 10000₽\n• Большая (20+ см) — от 20000₽",
    "portfolio": "🎨 Портфолио: реализм, графика, олдскул, нью-скул, японский, минимализм.",
    "contacts": "📞 Телефон: +7 (938) 300-33-20\n📍 г.Ставрополь, ул.Шпаковская, 97",
    "not_understood": "🤔 Пока не понял. Напиши «меню» для начала.",
    "booking_start": "✏️ Отлично! Начнём запись.\n\nКак тебя зовут?",
    "booking_ask_name": "📱 Приятно познакомиться, {name}!\n\nНапиши свой номер телефона:",
    "booking_ask_size": "📏 Какой размер татуировки тебя интересует?",
    "booking_ask_date": "📅 {service_name} — {hours}ч.\n\nВыбери удобную дату:",
    "booking_ask_time": "🕐 {date}\n\nВыбери удобное время:",
    "booking_no_dates": "😔 К сожалению, свободных дат нет. Попробуйте позже.",
    "booking_no_slots": "😔 На эту дату слотов нет. Выбери другую:",
    "booking_size_not_understood": "🤔 Не понял размер. Выбери, пожалуйста, из вариантов:",
    "booking_date_not_understood": "🤔 Не понял дату. Выбери из вариантов:",
    "booking_time_not_understood": "🤔 Не понял время. Выбери из вариантов:",
    "booking_success": "✅ {name}, ты записан!\n\n📅 {date}\n🕐 {time}\n⏱ {service_name} ({hours}ч)\n\nМы свяжемся с тобой для подтверждения.",
    "booking_failed": "⚠️ Не удалось забронировать. Попробуйте выбрать другое время.",
    "greeting": "👋 Привет! Рад тебя видеть! 😊\nЧем могу помочь?",
    "thanks": "😊 Всегда пожалуйста! Если будут вопросы — обращайся!",
    "goodbye": "👋 Пока! Увидимся! 😊",
}

EN_JSON = {
    "welcome": "👋 Hi! I'm an AI assistant for a tattoo studio.\nChoose an action:",
    "menu_booking": "Book",
    "menu_price": "Prices",
    "menu_portfolio": "Portfolio",
    "menu_contacts": "Contacts",
    "price": "💰 Prices:\n• Sketch — from 2000₽\n• Small (up to 10 cm) — from 5000₽\n• Medium (10-20 cm) — from 10000₽\n• Large (20+ cm) — from 20000₽",
    "portfolio": "🎨 Portfolio: realism, graphic, old school, new school, Japanese, minimalism.",
    "contacts": "📞 Phone: +7 (938) 300-33-20\n📍 Stavropol, Shpakovskaya st., 97",
    "not_understood": "🤔 Didn't understand. Type 'menu' to start.",
    "booking_start": "✏️ Great! Let's start booking.\n\nWhat's your name?",
    "booking_ask_name": "📱 Nice to meet you, {name}!\n\nPlease share your phone number:",
    "booking_ask_size": "📏 What tattoo size are you interested in?",
    "booking_ask_date": "📅 {service_name} — {hours}h.\n\nChoose a convenient date:",
    "booking_ask_time": "🕐 {date}\n\nChoose a convenient time:",
    "booking_no_dates": "😔 Unfortunately, no free dates. Try later.",
    "booking_no_slots": "😔 No slots on this date. Choose another:",
    "booking_size_not_understood": "🤔 Didn't understand the size. Please choose from options:",
    "booking_date_not_understood": "🤔 Didn't understand the date. Choose from options:",
    "booking_time_not_understood": "🤔 Didn't understand the time. Choose from options:",
    "booking_success": "✅ {name}, you're booked!\n\n📅 {date}\n🕐 {time}\n⏱ {service_name} ({hours}h)\n\nWe'll contact you to confirm.",
    "booking_failed": "⚠️ Booking failed. Please choose another time.",
    "greeting": "👋 Hi! Glad to see you! 😊\nHow can I help?",
    "thanks": "😊 You're welcome! Feel free to ask if you have questions!",
    "goodbye": "👋 Bye! See you! 😊",
}

HE_JSON = {
    "welcome": "👋 שלום! אני עוזר AI לסטודיו לקעקועים.\nבחר פעולה:",
    "menu_booking": "לקבוע תור",
    "menu_price": "מחירים",
    "menu_portfolio": "תיק עבודות",
    "menu_contacts": "יצירת קשר",
    "price": "💰 מחירים:\n• סקיצה — מ-2000₽\n• קטן (עד 10 ס\"מ) — מ-5000₽\n• בינוני (10-20 ס\"מ) — מ-10000₽\n• גדול (20+ ס\"מ) — מ-20000₽",
    "portfolio": "🎨 תיק עבודות: ריאליזם, גרפיקה, אולד סקול, ניו סקול, יפני, מינימליזם.",
    "contacts": "📞 טלפון: +7 (938) 300-33-20\n📍 סטברופול, רח' שפקובסקאיה, 97",
    "not_understood": "🤔 לא הבנתי. כתוב 'תפריט' כדי להתחיל.",
    "booking_start": "✏️ מעולה! נתחיל לקבוע תור.\n\nמה השם שלך?",
    "booking_ask_name": "📱 נעים להכיר, {name}!\n\nכתוב את מספר הטלפון שלך:",
    "booking_ask_size": "📏 איזה גודל קעקוע מעניין אותך?",
    "booking_ask_date": "📅 {service_name} — {hours} שעות.\n\nבחר תאריך נוח:",
    "booking_ask_time": "🕐 {date}\n\nבחר שעה נוחה:",
    "booking_no_dates": "😔 לצערי, אין תאריכים פנויים. נסה מאוחר יותר.",
    "booking_no_slots": "😔 אין שעות פנויות בתאריך זה. בחר אחר:",
    "booking_size_not_understood": "🤔 לא הבנתי את הגודל. בחר מהאפשרויות:",
    "booking_date_not_understood": "🤔 לא הבנתי את התאריך. בחר מהאפשרויות:",
    "booking_time_not_understood": "🤔 לא הבנתי את השעה. בחר מהאפשרויות:",
    "booking_success": "✅ {name}, קבעת תור!\n\n📅 {date}\n🕐 {time}\n⏱ {service_name} ({hours} שעות)\n\nניצור איתך קשר לאישור.",
    "booking_failed": "⚠️ לא הצלחנו לקבוע. בחר שעה אחרת.",
    "greeting": "👋 שלום! שמח לראות אותך! 😊\nאיך אני יכול לעזור?",
    "thanks": "😊 בבקשה! אם יש שאלות — פנה אליי!",
    "goodbye": "👋 להתראות! 😊",
}

TEST_LANG_PY = '''"""Тест определения языка."""
from core.i18n.detector import detect_language

tests = [
    ("привет", "ru"),
    ("Привет! Как дела?", "ru"),
    ("ghbdat", "ru"),
    ("ghfqc", "ru"),
    ("hello", "en"),
    ("Hello, how are you?", "en"),
    ("price please", "en"),
    ("שלום", "he"),
    ("מה המחיר?", "he"),
    ("אני רוצה לקבוע תור", "he"),
]

print("Тест определения языка:")
print("=" * 60)
ok = 0
for text, expected in tests:
    result = detect_language(text)
    status = "✅" if result == expected else "❌"
    if result == expected:
        ok += 1
    print(f"{status} '{text}' → '{result}' (ожидался '{expected}')")
print("=" * 60)
print(f"Результат: {ok}/{len(tests)}")
'''


def create_file(path: Path, content: str, force: bool = False):
    """Создаёт файл, если его нет (или force=True)."""
    if path.exists() and not force:
        print(f"⏭️  Уже существует: {path.relative_to(BASE)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"✅ Создан: {path.relative_to(BASE)}")


def create_json(path: Path, data: dict, force: bool = False):
    """Создаёт JSON-файл."""
    if path.exists() and not force:
        print(f"⏭️  Уже существует: {path.relative_to(BASE)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Создан: {path.relative_to(BASE)}")


def main():
    print("=" * 60)
    print("🚀 Установка i18n")
    print("=" * 60)
    print()

    # Папка
    i18n_dir = BASE / "core" / "i18n"
    i18n_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Папка: {i18n_dir.relative_to(BASE)}")
    print()

    # Файлы
    create_file(i18n_dir / "__init__.py", INIT_PY)
    create_file(i18n_dir / "detector.py", DETECTOR_PY)
    create_file(i18n_dir / "translator.py", TRANSLATOR_PY)
    create_json(i18n_dir / "ru.json", RU_JSON)
    create_json(i18n_dir / "en.json", EN_JSON)
    create_json(i18n_dir / "he.json", HE_JSON)
    create_file(BASE / "test_lang.py", TEST_LANG_PY)

    print()
    print("=" * 60)
    print("✅ Готово!")
    print("=" * 60)
    print()
    print("Проверьте:")
    print("  python test_lang.py")
    print()


if __name__ == '__main__':
    main()